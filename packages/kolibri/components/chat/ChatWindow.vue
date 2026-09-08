<template>

  <div
    class="phiedu-chat-window"
    :class="{ maximized: isMaximized }"
    :style="windowStyle"
  >
    <!-- Window Header (Draggable) -->
    <!-- eslint-disable-next-line vuejs-accessibility/no-static-element-interactions -->
    <div
      class="chat-window-header"
      :style="{
        backgroundColor: headerBg,
        color: headerTextColor,
      }"
      @mousedown="startDrag"
    >
      <div class="header-left">
        <!-- School Facility Logo + PHIEDU Icon Together -->
        <div class="header-branding">
          <img
            v-if="facilityLogoUrl"
            :src="facilityLogoUrl"
            :alt="schoolFacility$()"
            class="school-facility-badge"
          >
          <svg
            class="phiedu-mini-logo"
            viewBox="0 0 48 48"
            fill="none"
            :aria-label="phiedu$()"
          >
            <rect
              width="48"
              height="48"
              rx="8"
              fill="#ffffff"
            />
            <path
              d="M12 16.5C12 15.12 13.12 14 14.5 14H22V31.5H14.5C13.12 31.5 12 30.38 12 29V16.5Z"
              fill="#2563eb"
            />
            <path
              d="M36 16.5C36 15.12 34.88 14 33.5 14H26V31.5H33.5C34.88 31.5 36 30.38 36 29V16.5Z"
              fill="#2563eb"
            />
            <line
              x1="24"
              y1="14"
              x2="24"
              y2="33"
              stroke="#2563eb"
              stroke-width="2"
            />
          </svg>
        </div>

        <!-- Title & Status -->
        <div class="header-info">
          <div class="conversation-title">
            {{ conversation.title || phieduChat$() }}
          </div>
          <div
            v-if="typingNames.length > 0"
            class="typing-indicator"
          >
            {{ typingText }}
          </div>
          <div
            v-else
            class="status-subtext"
          >
            {{ conversationSubtext }}
          </div>
        </div>
      </div>

      <!-- Controls: Minimize, Maximize, Close -->
      <div
        class="header-controls"
        @mousedown.stop
      >
        <button
          type="button"
          class="ctrl-btn"
          :aria-label="minimize$()"
          :title="minimize$()"
          @click="$emit('minimize')"
        >
          {{ '─' }}
        </button>
        <button
          type="button"
          class="ctrl-btn"
          :aria-label="isMaximized ? restore$() : maximize$()"
          :title="isMaximized ? restore$() : maximize$()"
          @click="isMaximized = !isMaximized"
        >
          {{ isMaximized ? '❐' : '⤢' }}
        </button>
        <button
          type="button"
          class="close-btn ctrl-btn"
          :aria-label="close$()"
          :title="close$()"
          @click="$emit('close')"
        >
          {{ '✕' }}
        </button>
      </div>
    </div>

    <!-- Message List -->
    <div
      ref="messageListEl"
      class="chat-messages-container"
      :style="{ backgroundColor: $themeTokens.surface }"
      @scroll="onScroll"
    >
      <!-- Load Earlier / Cursor Pagination -->
      <div
        v-if="hasMore"
        class="load-earlier-wrapper"
      >
        <button
          type="button"
          class="load-earlier-btn"
          :disabled="isLoadingEarlier"
          :style="{ color: $themeTokens.primary }"
          @click="loadEarlier"
        >
          {{ isLoadingEarlier ? loading$() : loadEarlier$() }}
        </button>
      </div>

      <!-- Messages Loop -->
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="message-row"
        :class="{ 'self-row': msg.is_self, 'peer-row': !msg.is_self }"
      >
        <!-- Peer Sender Name -->
        <div
          v-if="!msg.is_self && conversation.kind !== 'direct'"
          class="sender-label"
          :style="{ color: $themeTokens.annotation }"
        >
          {{ msg.sender ? msg.sender.full_name : '' }}
          <span
            v-if="
              msg.sender &&
                msg.sender.facility_name &&
                msg.sender.facility_name !== conversation.facility_name
            "
            class="sender-facility-tag"
          >
            ({{ msg.sender.facility_name }})
          </span>
        </div>

        <div class="bubble-wrapper">
          <!-- Hover action bar for own messages or reactions -->
          <div
            class="bubble-actions"
            :class="{ 'self-actions': msg.is_self }"
          >
            <button
              type="button"
              class="act-icon-btn"
              :title="addReaction$()"
              @click="toggleReactionPicker(msg.id)"
            >
              {{ '😊' }}
            </button>
            <button
              v-if="msg.is_self && !msg.is_deleted"
              type="button"
              class="act-icon-btn"
              :title="edit$()"
              @click="startEdit(msg)"
            >
              {{ '✏️' }}
            </button>
            <button
              v-if="!msg.is_deleted && (msg.is_self || isStaffUser)"
              type="button"
              class="act-icon-btn"
              :title="deleteMessage$()"
              @click="promptDelete(msg)"
            >
              {{ '🗑️' }}
            </button>
          </div>

          <!-- Message Bubble -->
          <div
            class="message-bubble"
            :class="{
              'self-bubble': msg.is_self,
              'peer-bubble': !msg.is_self,
              'deleted-bubble': msg.is_deleted,
            }"
            :style="
              msg.is_self && !msg.is_deleted
                ? { backgroundColor: $themeTokens.primary, color: '#ffffff' }
                : {
                  backgroundColor: $themeTokens.cardBackground || '#f3f4f6',
                  color: $themeTokens.text,
                }
            "
          >
            <span class="bubble-text">{{ msg.content }}</span>

            <!-- Edited tag -->
            <span
              v-if="msg.is_edited && !msg.is_deleted"
              class="edited-badge"
              :title="formatEditedTime(msg.edited_at)"
            >
              {{ edited$() }}
            </span>
          </div>
        </div>

        <!-- Timestamp -->
        <div
          class="message-time"
          :style="{ color: $themeTokens.annotation }"
        >
          {{ formatTime(msg.created_at) }}
        </div>

        <!-- Reaction Pills -->
        <div
          v-if="msg.reactions && msg.reactions.length > 0"
          class="reactions-bar"
        >
          <button
            v-for="r in msg.reactions"
            :key="r.emoji"
            type="button"
            class="reaction-pill"
            :class="{ 'user-reacted': r.user_reacted }"
            :style="r.user_reacted ? { borderColor: $themeTokens.primary } : {}"
            @click="reactToMessage(msg.id, r.emoji)"
          >
            <span>{{ r.emoji }}</span>
            <span class="pill-count">{{ r.count }}</span>
          </button>
        </div>

        <!-- Emoji picker popover for this message -->
        <div
          v-if="reactionTargetMessageId === msg.id"
          class="inline-reaction-popover"
        >
          <ChatEmojiPicker @select="onSelectReaction(msg.id, $event)" />
        </div>
      </div>

      <!-- Live typing in window -->
      <div
        v-if="typingNames.length > 0"
        class="typing-bubble-row"
      >
        <div class="typing-bubble">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>

    <!-- Inline Edit Bar -->
    <div
      v-if="editingMessage"
      class="edit-banner"
      :style="{ backgroundColor: $themeTokens.surface, borderColor: $themeTokens.fineLine }"
    >
      <div class="edit-banner-info">
        {{ editingMessage$() }}
      </div>
      <button
        type="button"
        class="cancel-edit-btn"
        @click="cancelEdit"
      >
        {{ cancel$() }}
      </button>
    </div>

    <!-- Footer: Input + Emoji Picker + Send -->
    <div
      class="chat-window-footer"
      :style="{
        backgroundColor: $themeTokens.surface,
        borderTopColor: $themeTokens.fineLine,
      }"
    >
      <!-- Emoji Picker Popover -->
      <div
        v-if="showEmojiPicker"
        class="footer-emoji-popover"
      >
        <ChatEmojiPicker @select="onInsertEmoji" />
      </div>

      <button
        type="button"
        class="emoji-toggle-btn"
        :title="chooseEmoji$()"
        :aria-label="chooseEmoji$()"
        @click="showEmojiPicker = !showEmojiPicker"
      >
        {{ '😊' }}
      </button>

      <textarea
        ref="inputEl"
        v-model="inputText"
        class="chat-input"
        :placeholder="typeMessage$()"
        :aria-label="typeMessage$()"
        :style="{
          backgroundColor: $themeTokens.surface,
          color: $themeTokens.text,
          borderColor: $themeTokens.fineLine,
        }"
        rows="1"
        @keydown="handleKeyDown"
        @input="onInput"
      ></textarea>

      <button
        type="button"
        class="send-btn"
        :aria-label="sendMessage$()"
        :disabled="!inputText.trim()"
        :style="
          inputText.trim()
            ? { backgroundColor: $themeTokens.primary, color: '#ffffff' }
            : { opacity: 0.5 }
        "
        @click="submitMessage"
      >
        {{ '➤' }}
      </button>
    </div>
  </div>

</template>


<script>

  import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
  import themeConfig from 'kolibri/styles/themeConfig';
  import useUser from 'kolibri/composables/useUser';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useChat from '../../composables/useChat';
  import useChatRealtime, { registerMessageListener } from '../../composables/useChatRealtime';
  import ChatEmojiPicker from './ChatEmojiPicker';

  export const chatWindowStrings = createTranslator('ChatWindowStrings', {
    phieduChat: {
      message: 'PHIEDU Chat',
      context: 'Default title for chat window',
    },
    classroomGroup: {
      message: 'Classroom Group',
      context: 'Subtext indicating classroom conversation',
    },
    active: {
      message: 'Active',
      context: 'Subtext indicating active conversation',
    },
    isTyping: {
      message: '{name} is typing...',
      context: 'Status message when a user is typing',
    },
    peopleAreTyping: {
      message: '{count} people are typing...',
      context: 'Status message when multiple users are typing',
    },
    minimize: {
      message: 'Minimize',
      context: 'Tooltip and aria label for minimize button',
    },
    maximize: {
      message: 'Maximize',
      context: 'Tooltip and aria label for maximize button',
    },
    restore: {
      message: 'Restore',
      context: 'Tooltip and aria label for restore button',
    },
    close: {
      message: 'Close',
      context: 'Tooltip and aria label for close button',
    },
    loading: {
      message: 'Loading...',
      context: 'Loading state indicator',
    },
    loadEarlier: {
      message: '↑ Load earlier messages',
      context: 'Button label to load older messages',
    },
    addReaction: {
      message: 'Add reaction',
      context: 'Tooltip for adding a reaction',
    },
    edit: {
      message: 'Edit',
      context: 'Tooltip for editing a message',
    },
    deleteMessage: {
      message: 'Delete message',
      context: 'Tooltip for deleting a message',
    },
    edited: {
      message: '(edited)',
      context: 'Label indicating message was edited',
    },
    editedAt: {
      message: 'Edited at {time}',
      context: 'Tooltip displaying edited timestamp',
    },
    editingMessage: {
      message: 'Editing message',
      context: 'Banner header when editing a message',
    },
    cancel: {
      message: 'Cancel',
      context: 'Button to cancel action',
    },
    chooseEmoji: {
      message: 'Choose an emoji',
      context: 'Tooltip for emoji picker button',
    },
    typeMessage: {
      message: 'Type a message...',
      context: 'Placeholder and aria label for message input',
    },
    sendMessage: {
      message: 'Send message',
      context: 'Aria label for send button',
    },
    schoolFacility: {
      message: 'School Facility',
      context: 'Alt text for school facility badge',
    },
    phiedu: {
      message: 'PHIEDU',
      context: 'Aria label for PHIEDU logo',
    },
  });

  export default {
    name: 'ChatWindow',
    components: {
      ChatEmojiPicker,
    },
    setup(props) {
      const {
        phieduChat$,
        classroomGroup$,
        active$,
        isTyping$,
        peopleAreTyping$,
        minimize$,
        maximize$,
        restore$,
        close$,
        loading$,
        loadEarlier$,
        addReaction$,
        edit$,
        deleteMessage$,
        edited$,
        editedAt$,
        editingMessage$,
        cancel$,
        chooseEmoji$,
        typeMessage$,
        sendMessage$,
        schoolFacility$,
        phiedu$,
      } = chatWindowStrings;

      const {
        fetchMessages,
        sendMessage,
        editMessage,
        deleteMessage,
        toggleReaction,
        sendTyping,
        markConversationRead,
      } = useChat();
      const { typingMap } = useChatRealtime();
      const { isCoach, isAdmin, isSuperuser } = useUser();

      const messages = ref([]);
      const inputText = ref('');
      const hasMore = ref(false);
      const cursor = ref(null);
      const isLoadingEarlier = ref(false);
      const isMaximized = ref(false);
      const showEmojiPicker = ref(false);
      const reactionTargetMessageId = ref(null);
      const editingMessage = ref(null);

      // Dragging state
      const pos = ref({ x: null, y: null });
      const isDragging = ref(false);
      const dragStart = { x: 0, y: 0, initialX: 0, initialY: 0 };

      const messageListEl = ref(null);
      const inputEl = ref(null);

      let typingDebounceTimeout = null;
      let unregisterListener = null;

      const isStaffUser = computed(() => {
        return isCoach.value || isAdmin.value || isSuperuser.value;
      });

      // School Facility logo & PHIEDU colors
      const facilityLogoUrl = computed(() => {
        return themeConfig.appBar.topLogo?.src || themeConfig.signIn.topLogo?.src || null;
      });

      const headerBg = computed(() => {
        return themeConfig.appBar.background || '#1d4ed8';
      });

      const headerTextColor = computed(() => {
        return themeConfig.appBar.textColor || '#ffffff';
      });

      const typingNames = computed(() => {
        return typingMap.value.get(props.conversation.id) || [];
      });

      const typingText = computed(() => {
        const names = typingNames.value;
        if (!names || names.length === 0) return '';
        if (names.length === 1) {
          return isTyping$({ name: names[0] });
        }
        return peopleAreTyping$({ count: names.length });
      });

      const conversationSubtext = computed(() => {
        const base = props.conversation.kind === 'classroom' ? classroomGroup$() : active$();
        if (props.conversation.facility_name) {
          return `${base} • ${props.conversation.facility_name}`;
        }
        return base;
      });

      // Position computation: right-docked offset by dockIndex unless user dragged
      const windowStyle = computed(() => {
        if (isMaximized.value) {
          return {
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            width: 'calc(100vw - 40px)',
            maxWidth: '720px',
            height: 'calc(100vh - 80px)',
            zIndex: 10010,
          };
        }

        if (pos.value.x !== null && pos.value.y !== null) {
          return {
            position: 'fixed',
            left: `${pos.value.x}px`,
            top: `${pos.value.y}px`,
            width: '340px',
            height: '470px',
            zIndex: 10002 + props.dockIndex,
          };
        }

        // Docked offset from right
        const rightOffset = 20 + props.dockIndex * 356;
        return {
          position: 'fixed',
          bottom: '80px',
          right: `${rightOffset}px`,
          width: '340px',
          height: '470px',
          zIndex: 10002 + props.dockIndex,
        };
      });

      function scrollToBottom() {
        nextTick(() => {
          if (messageListEl.value) {
            messageListEl.value.scrollTop = messageListEl.value.scrollHeight;
          }
        });
      }

      async function loadInitialMessages() {
        const data = await fetchMessages(props.conversation.id);
        messages.value = data.messages || [];
        hasMore.value = data.has_more || false;
        cursor.value = data.cursor || null;
        scrollToBottom();
      }

      async function loadEarlier() {
        if (!cursor.value || isLoadingEarlier.value) return;
        isLoadingEarlier.value = true;
        const currentScrollHeight = messageListEl.value?.scrollHeight || 0;

        const data = await fetchMessages(props.conversation.id, cursor.value);
        const older = data.messages || [];
        messages.value = [...older, ...messages.value];
        hasMore.value = data.has_more || false;
        cursor.value = data.cursor || null;
        isLoadingEarlier.value = false;

        nextTick(() => {
          if (messageListEl.value) {
            messageListEl.value.scrollTop = messageListEl.value.scrollHeight - currentScrollHeight;
          }
        });
      }

      function onScroll(e) {
        if (e.target.scrollTop === 0 && hasMore.value && !isLoadingEarlier.value) {
          loadEarlier();
        }
      }

      function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          submitMessage();
        }
      }

      function onInput() {
        // Send typing status
        sendTyping(props.conversation.id, true);
        if (typingDebounceTimeout) clearTimeout(typingDebounceTimeout);
        typingDebounceTimeout = setTimeout(() => {
          sendTyping(props.conversation.id, false);
        }, 2000);
      }

      async function submitMessage() {
        const text = inputText.value.trim();
        if (!text) return;

        if (editingMessage.value) {
          // Edit existing message
          const msgId = editingMessage.value.id;
          editingMessage.value = null;
          inputText.value = '';
          const updated = await editMessage(msgId, text);
          const idx = messages.value.findIndex(m => m.id === msgId);
          if (idx !== -1) {
            messages.value.splice(idx, 1, updated);
          }
        } else {
          // Send new message
          inputText.value = '';
          const newMsg = await sendMessage(props.conversation.id, text);
          messages.value.push(newMsg);
          scrollToBottom();
        }
        showEmojiPicker.value = false;
      }

      function onInsertEmoji(emoji) {
        inputText.value += emoji;
        showEmojiPicker.value = false;
        inputEl.value?.focus();
      }

      function toggleReactionPicker(msgId) {
        if (reactionTargetMessageId.value === msgId) {
          reactionTargetMessageId.value = null;
        } else {
          reactionTargetMessageId.value = msgId;
        }
      }

      async function onSelectReaction(msgId, emoji) {
        reactionTargetMessageId.value = null;
        await reactToMessage(msgId, emoji);
      }

      async function reactToMessage(msgId, emoji) {
        const res = await toggleReaction(msgId, emoji);
        const idx = messages.value.findIndex(m => m.id === msgId);
        if (idx !== -1 && res.message) {
          messages.value.splice(idx, 1, res.message);
        }
      }

      function startEdit(msg) {
        editingMessage.value = msg;
        inputText.value = msg.content;
        inputEl.value?.focus();
      }

      function cancelEdit() {
        editingMessage.value = null;
        inputText.value = '';
      }

      async function promptDelete(msg) {
        const confirmDelete = window.confirm(
          'Delete this message?\nClick OK to delete for everyone, or Cancel to abort.',
        );
        if (confirmDelete) {
          const res = await deleteMessage(msg.id, true);
          const idx = messages.value.findIndex(m => m.id === msg.id);
          if (idx !== -1) {
            messages.value.splice(idx, 1, res);
          }
        }
      }

      function formatTime(isoStr) {
        if (!isoStr) return '';
        const d = new Date(isoStr);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }

      function formatEditedTime(isoStr) {
        return editedAt$({ time: formatTime(isoStr) });
      }

      // Drag and drop implementation
      function startDrag(e) {
        if (isMaximized.value) return;
        isDragging.value = true;
        const rect = e.currentTarget.closest('.phiedu-chat-window').getBoundingClientRect();
        dragStart.initialX = rect.left;
        dragStart.initialY = rect.top;
        dragStart.x = e.clientX;
        dragStart.y = e.clientY;

        window.addEventListener('mousemove', onDrag);
        window.addEventListener('mouseup', stopDrag);
      }

      function onDrag(e) {
        if (!isDragging.value) return;
        const dx = e.clientX - dragStart.x;
        const dy = e.clientY - dragStart.y;
        pos.value = {
          x: Math.max(0, Math.min(window.innerWidth - 350, dragStart.initialX + dx)),
          y: Math.max(0, Math.min(window.innerHeight - 480, dragStart.initialY + dy)),
        };
      }

      function stopDrag() {
        isDragging.value = false;
        window.removeEventListener('mousemove', onDrag);
        window.removeEventListener('mouseup', stopDrag);
      }

      onMounted(() => {
        loadInitialMessages();
        markConversationRead(props.conversation.id);

        // Listen for real-time messages and updates
        unregisterListener = registerMessageListener(props.conversation.id, event => {
          if (event.type === 'new_message') {
            const exists = messages.value.some(m => m.id === event.message.id);
            if (!exists) {
              messages.value.push(event.message);
              scrollToBottom();
            }
          } else if (event.type === 'update_message') {
            const idx = messages.value.findIndex(m => m.id === event.message.id);
            if (idx !== -1) {
              messages.value.splice(idx, 1, event.message);
            }
          }
        });
      });

      onUnmounted(() => {
        if (unregisterListener) unregisterListener();
        if (typingDebounceTimeout) clearTimeout(typingDebounceTimeout);
        stopDrag();
      });

      return {
        messages,
        inputText,
        hasMore,
        isLoadingEarlier,
        isMaximized,
        showEmojiPicker,
        reactionTargetMessageId,
        editingMessage,
        messageListEl,
        inputEl,
        isStaffUser,
        facilityLogoUrl,
        headerBg,
        headerTextColor,
        typingNames,
        typingText,
        windowStyle,
        loadEarlier,
        onScroll,
        handleKeyDown,
        onInput,
        submitMessage,
        onInsertEmoji,
        toggleReactionPicker,
        onSelectReaction,
        reactToMessage,
        startEdit,
        cancelEdit,
        promptDelete,
        formatTime,
        formatEditedTime,
        startDrag,
        phieduChat$,
        conversationSubtext,
        minimize$,
        maximize$,
        restore$,
        close$,
        loading$,
        loadEarlier$,
        addReaction$,
        edit$,
        deleteMessage$,
        edited$,
        editingMessage$,
        cancel$,
        chooseEmoji$,
        typeMessage$,
        sendMessage$,
        schoolFacility$,
        phiedu$,
      };
    },
    props: {
      conversation: {
        type: Object,
        required: true,
      },
      dockIndex: {
        type: Number,
        default: 0,
      },
    },
    emits: ['close', 'minimize'],
  };

</script>


<style scoped>

  .phiedu-chat-window {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background-color: #ffffff;
    border-radius: 12px 12px 0 0;
    box-shadow:
      0 8px 30px rgba(0, 0, 0, 0.25),
      0 3px 10px rgba(0, 0, 0, 0.15);
    transition:
      width 0.2s cubic-bezier(0.4, 0, 0.2, 1),
      height 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .phiedu-chat-window.maximized {
    border-radius: 12px;
  }

  /* Header */
  .chat-window-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 48px;
    padding: 0 10px;
    cursor: grab;
    user-select: none;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
  }

  .chat-window-header:active {
    cursor: grabbing;
  }

  .header-left {
    display: flex;
    gap: 8px;
    align-items: center;
    overflow: hidden;
  }

  .header-branding {
    position: relative;
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
  }

  .school-facility-badge {
    position: absolute;
    top: -2px;
    left: -4px;
    z-index: 2;
    width: 16px;
    height: 16px;
    overflow: hidden;
    object-fit: cover;
    background: #ffffff;
    border: 1px solid #ffffff;
    border-radius: 50%;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  }

  .phiedu-mini-logo {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  }

  .header-info {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .conversation-title {
    overflow: hidden;
    font-size: 13px;
    font-weight: 700;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .status-subtext {
    font-size: 10px;
    opacity: 0.85;
  }

  .typing-indicator {
    font-size: 10px;
    font-weight: 600;
    color: #bbf7d0;
  }

  .header-controls {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .ctrl-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    font-size: 14px;
    color: inherit;
    cursor: pointer;
    background: transparent;
    border: 0;
    border-radius: 50%;
    opacity: 0.85;
    transition:
      background 0.15s,
      opacity 0.15s;
  }

  .ctrl-btn:hover {
    background-color: rgba(255, 255, 255, 0.2);
    opacity: 1;
  }

  /* Messages List */
  .chat-messages-container {
    display: flex;
    flex: 1;
    flex-direction: column;
    gap: 8px;
    padding: 12px;
    overflow-y: auto;
  }

  .load-earlier-wrapper {
    display: flex;
    justify-content: center;
    margin-bottom: 6px;
  }

  .load-earlier-btn {
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    background: transparent;
    border: 0;
    border-radius: 12px;
  }

  .load-earlier-btn:hover {
    text-decoration: underline;
  }

  .message-row {
    position: relative;
    display: flex;
    flex-direction: column;
    max-width: 82%;
  }

  .self-row {
    align-items: flex-end;
    align-self: flex-end;
  }

  .peer-row {
    align-items: flex-start;
    align-self: flex-start;
  }

  .sender-label {
    margin-bottom: 2px;
    font-size: 10px;
    font-weight: 600;
  }

  .sender-facility-tag {
    font-weight: 500;
    font-size: 9px;
    opacity: 0.85;
    margin-left: 4px;
  }

  .bubble-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }

  .bubble-actions {
    display: none;
    gap: 2px;
    align-items: center;
    padding: 0 4px;
  }

  .self-actions {
    order: -1;
  }

  .bubble-wrapper:hover .bubble-actions {
    display: flex;
  }

  .act-icon-btn {
    padding: 2px;
    font-size: 12px;
    cursor: pointer;
    background: transparent;
    border: 0;
    border-radius: 4px;
    opacity: 0.7;
    transition: opacity 0.1s;
  }

  .act-icon-btn:hover {
    opacity: 1;
  }

  .message-bubble {
    position: relative;
    padding: 8px 12px;
    font-size: 13px;
    line-height: 1.4;
    word-break: break-word;
    border-radius: 18px;
  }

  .self-bubble {
    border-bottom-right-radius: 4px;
  }

  .peer-bubble {
    border-bottom-left-radius: 4px;
  }

  .deleted-bubble {
    font-style: italic;
    opacity: 0.6;
  }

  .edited-badge {
    margin-left: 4px;
    font-size: 10px;
    cursor: help;
    opacity: 0.75;
  }

  .message-time {
    padding: 0 4px;
    margin-top: 2px;
    font-size: 9px;
  }

  .reactions-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 3px;
  }

  .reaction-pill {
    display: flex;
    gap: 3px;
    align-items: center;
    padding: 1px 6px;
    font-size: 11px;
    cursor: pointer;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }

  .reaction-pill.user-reacted {
    font-weight: 600;
    background: #eff6ff;
  }

  .inline-reaction-popover {
    position: absolute;
    top: -240px;
    z-index: 10020;
  }

  /* Typing Dots */
  .typing-bubble-row {
    align-self: flex-start;
  }

  .typing-bubble {
    display: flex;
    gap: 4px;
    align-items: center;
    padding: 6px 12px;
    background: #e5e7eb;
    border-radius: 14px;
  }

  .dot {
    width: 6px;
    height: 6px;
    background: #6b7280;
    border-radius: 50%;
    animation: typing-bounce 1.2s infinite ease-in-out;
  }

  .dot:nth-child(2) {
    animation-delay: 0.2s;
  }

  .dot:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes typing-bounce {
    0%,
    60%,
    100% {
      transform: translateY(0);
    }

    30% {
      transform: translateY(-4px);
    }
  }

  /* Edit banner */
  .edit-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 12px;
    font-size: 11px;
    border-top: 1px solid;
  }

  .cancel-edit-btn {
    font-weight: 600;
    color: #ef4444;
    cursor: pointer;
    background: transparent;
    border: 0;
  }

  /* Footer */
  .chat-window-footer {
    position: relative;
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 8px 10px;
    border-top: 1px solid;
  }

  .footer-emoji-popover {
    position: absolute;
    bottom: 52px;
    left: 10px;
    z-index: 10020;
  }

  .emoji-toggle-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
    font-size: 20px;
    cursor: pointer;
    background: transparent;
    border: 0;
    border-radius: 50%;
  }

  .emoji-toggle-btn:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }

  .chat-input {
    flex: 1;
    max-height: 80px;
    padding: 8px 12px;
    font-family: inherit;
    font-size: 13px;
    line-height: 1.4;
    resize: none;
    border: 1px solid;
    border-radius: 18px;
    outline: none;
  }

  .send-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    font-size: 14px;
    cursor: pointer;
    border: 0;
    border-radius: 50%;
    transition:
      transform 0.1s,
      opacity 0.15s;
  }

  .send-btn:active {
    transform: scale(0.92);
  }

</style>
