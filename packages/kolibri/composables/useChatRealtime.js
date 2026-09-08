import { ref } from 'vue';
import client from 'kolibri/client';
import { playMessageChime } from '../components/chat/chatAudio';
import useChat from './useChat';

let pollTimer = null;
let lastSyncTime = null;
let isPollingActive = false;

// Event bus for message updates per conversation
const messageListeners = new Map(); // conversationId -> Set of callbacks
const typingMap = ref(new Map()); // conversationId -> Set of user names typing
const readReceiptsMap = ref(new Map()); // conversationId -> Map(userId -> messageId)

export function registerMessageListener(conversationId, callback) {
  if (!messageListeners.has(conversationId)) {
    messageListeners.set(conversationId, new Set());
  }
  messageListeners.get(conversationId).add(callback);
  return () => {
    const set = messageListeners.get(conversationId);
    if (set) {
      set.delete(callback);
      if (set.size === 0) messageListeners.delete(conversationId);
    }
  };
}

export default function useChatRealtime() {
  const { conversations, activeWindows } = useChat();

  function getPollInterval() {
    if (typeof document !== 'undefined' && document.hidden) {
      return 15000; // 15s in background
    }
    if (activeWindows.value.length > 0) {
      return 2500; // 2.5s when chatting
    }
    return 6000; // 6s when docked idle
  }

  async function syncDelta() {
    if (!isPollingActive) return;

    try {
      const params = {};
      if (lastSyncTime) {
        params.since = lastSyncTime;
      }

      const res = await client({
        url: '/api/chat/updates/',
        method: 'GET',
        params,
      });

      lastSyncTime = res.data.server_time;

      const { new_messages, updated_messages, typing, read_receipts } = res.data;

      let hasNewExternalMsg = false;

      // 1. Process new messages
      if (new_messages && new_messages.length > 0) {
        for (const msg of new_messages) {
          if (!msg.is_self) {
            hasNewExternalMsg = true;
          }
          // Notify listeners
          const listeners = messageListeners.get(msg.conversation_id);
          if (listeners) {
            listeners.forEach(cb => cb({ type: 'new_message', message: msg }));
          }
          // Update conversation in list
          const conv = conversations.value.find(c => c.id === msg.conversation_id);
          if (conv) {
            conv.last_message = {
              id: msg.id,
              content: msg.content,
              sender_name: msg.sender ? msg.sender.full_name : '',
              created_at: msg.created_at,
              is_self: msg.is_self,
            };
            conv.updated_at = msg.created_at;
            // If window not open, increment unread count
            const isOpen = activeWindows.value.some(w => w.id === conv.id);
            if (!isOpen && !msg.is_self) {
              conv.unread_count = (conv.unread_count || 0) + 1;
            }
          }
        }

        if (hasNewExternalMsg) {
          playMessageChime();
        }
      }

      // 2. Process updated / deleted / edited messages
      if (updated_messages && updated_messages.length > 0) {
        for (const msg of updated_messages) {
          const listeners = messageListeners.get(msg.conversation_id);
          if (listeners) {
            listeners.forEach(cb => cb({ type: 'update_message', message: msg }));
          }
        }
      }

      // 3. Process typing indicators
      const newTyping = new Map();
      if (typing) {
        for (const t of typing) {
          if (!newTyping.has(t.conversation_id)) {
            newTyping.set(t.conversation_id, []);
          }
          newTyping.get(t.conversation_id).push(t.user.full_name || t.user.username);
        }
      }
      typingMap.value = newTyping;

      // 4. Process read receipts
      if (read_receipts && read_receipts.length > 0) {
        for (const r of read_receipts) {
          if (!readReceiptsMap.value.has(r.conversation_id)) {
            readReceiptsMap.value.set(r.conversation_id, new Map());
          }
          readReceiptsMap.value.get(r.conversation_id).set(r.user_id, r.last_read_message_id);
        }
      }
    } catch (err) {
      // Non-blocking network errors
    } finally {
      if (isPollingActive) {
        pollTimer = setTimeout(syncDelta, getPollInterval());
      }
    }
  }

  function startRealtime() {
    if (isPollingActive) return;
    isPollingActive = true;
    syncDelta();
  }

  function stopRealtime() {
    isPollingActive = false;
    if (pollTimer) {
      clearTimeout(pollTimer);
      pollTimer = null;
    }
  }

  return {
    typingMap,
    readReceiptsMap,
    startRealtime,
    stopRealtime,
    syncDelta,
  };
}
