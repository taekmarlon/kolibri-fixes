import { ref, computed } from 'vue';
import client from 'kolibri/client';
import { playMessageChime, isChatMuted, setChatMuted } from '../components/chat/chatAudio';

// Shared module-level reactive state
const conversations = ref([]);
const activeWindows = ref([]); // List of active conversation objects (max 3)
const minimizedChatheads = ref([]); // List of conversation objects docked as small chatheads
const contacts = ref([]);
const classrooms = ref([]);
const isConversationsListOpen = ref(false);
const isMuted = ref(isChatMuted());
const isContactsModalOpen = ref(false);

const MAX_ACTIVE_WINDOWS = 3;

export default function useChat() {
  const totalUnreadCount = computed(() => {
    return conversations.value.reduce((sum, c) => sum + (c.unread_count || 0), 0);
  });

  async function fetchConversations() {
    try {
      const res = await client({
        url: '/api/chat/conversations/',
        method: 'GET',
      });
      conversations.value = res.data;
      return res.data;
    } catch (err) {
      return [];
    }
  }

  async function fetchContacts(searchQuery = '') {
    try {
      const res = await client({
        url: '/api/chat/contacts/',
        method: 'GET',
        params: searchQuery ? { q: searchQuery } : {},
      });
      contacts.value = res.data.contacts || [];
      classrooms.value = res.data.classrooms || [];
      return res.data;
    } catch (err) {
      return { contacts: [], classrooms: [] };
    }
  }

  function openConversation(conv) {
    if (!conv || !conv.id) return;

    // Check if already open
    const openIdx = activeWindows.value.findIndex(w => w.id === conv.id);
    if (openIdx !== -1) {
      // Bring to front
      const [item] = activeWindows.value.splice(openIdx, 1);
      activeWindows.value.push(item);
      return;
    }

    // Check if in minimized chatheads; remove if so
    const headIdx = minimizedChatheads.value.findIndex(h => h.id === conv.id);
    if (headIdx !== -1) {
      minimizedChatheads.value.splice(headIdx, 1);
    }

    // If max active windows reached, minimize the oldest one to chathead
    if (activeWindows.value.length >= MAX_ACTIVE_WINDOWS) {
      const oldest = activeWindows.value.shift();
      if (oldest && !minimizedChatheads.value.some(h => h.id === oldest.id)) {
        minimizedChatheads.value.unshift(oldest);
      }
    }

    activeWindows.value.push(conv);
    markConversationRead(conv.id);
  }

  function closeConversation(convId) {
    activeWindows.value = activeWindows.value.filter(w => w.id !== convId);
    minimizedChatheads.value = minimizedChatheads.value.filter(h => h.id !== convId);
  }

  function minimizeConversation(convId) {
    const idx = activeWindows.value.findIndex(w => w.id === convId);
    if (idx !== -1) {
      const [conv] = activeWindows.value.splice(idx, 1);
      if (!minimizedChatheads.value.some(h => h.id === conv.id)) {
        minimizedChatheads.value.unshift(conv);
      }
    }
  }

  function restoreConversation(conv) {
    minimizedChatheads.value = minimizedChatheads.value.filter(h => h.id !== conv.id);
    openConversation(conv);
  }

  async function startDirectChat(recipientId) {
    const res = await client({
      url: '/api/chat/conversations/',
      method: 'POST',
      data: {
        kind: 'direct',
        recipient_id: recipientId,
      },
    });
    await fetchConversations();
    const conv = conversations.value.find(c => c.id === res.data.id) || res.data;
    openConversation(conv);
    isConversationsListOpen.value = false;
    isContactsModalOpen.value = false;
    return conv;
  }

  async function startClassroomChat(collectionId) {
    const res = await client({
      url: '/api/chat/conversations/',
      method: 'POST',
      data: {
        kind: 'classroom',
        collection_id: collectionId,
      },
    });
    await fetchConversations();
    const conv = conversations.value.find(c => c.id === res.data.id) || res.data;
    openConversation(conv);
    isConversationsListOpen.value = false;
    isContactsModalOpen.value = false;
    return conv;
  }

  async function fetchMessages(conversationId, beforeId = null) {
    try {
      const params = { conversation_id: conversationId, limit: 25 };
      if (beforeId) params.before_id = beforeId;

      const res = await client({
        url: '/api/chat/messages/',
        method: 'GET',
        params,
      });
      return res.data;
    } catch (err) {
      return { messages: [], has_more: false, cursor: null };
    }
  }

  async function sendMessage(conversationId, content) {
    const res = await client({
      url: '/api/chat/messages/',
      method: 'POST',
      data: {
        conversation_id: conversationId,
        content,
      },
    });
    // Update local last message in conversation
    const conv = conversations.value.find(c => c.id === conversationId);
    if (conv) {
      conv.last_message = {
        id: res.data.id,
        content: res.data.content,
        sender_name: res.data.sender ? res.data.sender.full_name : '',
        created_at: res.data.created_at,
        is_self: true,
      };
      conv.updated_at = res.data.created_at;
    }
    return res.data;
  }

  async function editMessage(messageId, content) {
    const res = await client({
      url: `/api/chat/messages/${messageId}/`,
      method: 'PATCH',
      data: { content },
    });
    return res.data;
  }

  async function deleteMessage(messageId, forEveryone = false) {
    const res = await client({
      url: `/api/chat/messages/${messageId}/`,
      method: 'DELETE',
      params: { for_everyone: forEveryone },
    });
    return res.data;
  }

  async function toggleReaction(messageId, emoji) {
    const res = await client({
      url: `/api/chat/messages/${messageId}/react/`,
      method: 'POST',
      data: { emoji },
    });
    return res.data;
  }

  async function markConversationRead(conversationId) {
    try {
      const conv = conversations.value.find(c => c.id === conversationId);
      if (conv) {
        conv.unread_count = 0;
      }
      await client({
        url: `/api/chat/conversations/${conversationId}/read/`,
        method: 'POST',
      });
    } catch (err) {
      // Non-blocking
    }
  }

  async function sendTyping(conversationId, isTyping = true) {
    try {
      await client({
        url: '/api/chat/typing/',
        method: 'POST',
        data: { conversation_id: conversationId, is_typing: isTyping },
      });
    } catch (err) {
      // Non-blocking
    }
  }

  function toggleMute() {
    isMuted.value = !isMuted.value;
    setChatMuted(isMuted.value);
  }

  return {
    conversations,
    activeWindows,
    minimizedChatheads,
    contacts,
    classrooms,
    isConversationsListOpen,
    isContactsModalOpen,
    isMuted,
    totalUnreadCount,
    fetchConversations,
    fetchContacts,
    openConversation,
    closeConversation,
    minimizeConversation,
    restoreConversation,
    startDirectChat,
    startClassroomChat,
    fetchMessages,
    sendMessage,
    editMessage,
    deleteMessage,
    toggleReaction,
    markConversationRead,
    sendTyping,
    toggleMute,
    playMessageChime,
  };
}
