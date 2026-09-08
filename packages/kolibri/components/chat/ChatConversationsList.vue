<template>

  <div
    class="phiedu-conversations-popup"
    :style="{
      backgroundColor: $themeTokens.surface,
      color: $themeTokens.text,
      borderColor: $themeTokens.fineLine,
    }"
  >
    <!-- Header -->
    <div
      class="popup-header"
      :style="{
        backgroundColor: headerBg,
        color: headerTextColor,
      }"
    >
      <div class="header-left">
        <!-- School Facility Logo + PHIEDU Logo Together -->
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
        <span class="app-title">{{ phieduMessages$() }}</span>
      </div>

      <div class="header-actions">
        <!-- Sound Mute Toggle -->
        <button
          type="button"
          class="hdr-action-btn"
          :title="isMuted ? unmuteSounds$() : muteSounds$()"
          :aria-label="isMuted ? unmuteSounds$() : muteSounds$()"
          @click="toggleMute"
        >
          {{ isMuted ? '🔕' : '🔔' }}
        </button>

        <!-- New Message Button -->
        <button
          type="button"
          class="hdr-action-btn"
          :title="newMessage$()"
          :aria-label="newMessage$()"
          @click="showNewChatModal = !showNewChatModal"
        >
          {{ '✏️' }}
        </button>

        <!-- Close popup -->
        <button
          type="button"
          class="hdr-action-btn"
          :title="close$()"
          :aria-label="close$()"
          @click="$emit('close')"
        >
          {{ '✕' }}
        </button>
      </div>
    </div>

    <!-- Active Facility Indicator Strip -->
    <div
      v-if="currentFacilityName"
      class="active-facility-strip"
      :style="{
        backgroundColor: $themeTokens.surface,
        borderBottom: '1px solid ' + $themeTokens.fineLine,
        color: $themeTokens.annotation,
      }"
    >
      <span
        class="facility-icon"
        aria-hidden="true"
      >{{ '🏫' }}</span>
      <span class="facility-label">{{ facilityLabel$() }}:</span>
      <span class="facility-name-text">{{ currentFacilityName }}</span>
    </div>

    <!-- Search input -->
    <div
      class="search-bar-wrapper"
      :style="{ borderBottomColor: $themeTokens.fineLine }"
    >
      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        :placeholder="searchPlaceholder$()"
        :aria-label="searchPlaceholder$()"
        :style="{
          backgroundColor: $themeTokens.cardBackground || '#f3f4f6',
          color: $themeTokens.text,
        }"
      >
    </div>

    <!-- New Chat / Contacts Mode -->
    <div
      v-if="showNewChatModal"
      class="contacts-mode-container"
    >
      <div
        class="contacts-mode-header"
        :style="{ borderBottomColor: $themeTokens.fineLine }"
      >
        <span class="mode-title">{{ newConversation$() }}</span>
        <button
          type="button"
          class="back-btn"
          @click="showNewChatModal = false"
        >
          {{ back$() }}
        </button>
      </div>

      <div class="contacts-scroll-list">
        <!-- Classrooms group chats -->
        <div
          v-if="classrooms.length > 0"
          class="contact-group-header"
        >
          {{ classrooms$() }}
        </div>
        <button
          v-for="cls in filteredClassrooms"
          :key="cls.id"
          type="button"
          class="contact-row"
          @click="handleSelectClassroom(cls.id)"
        >
          <div
            class="class-avatar contact-avatar"
            :style="{ backgroundColor: $themeTokens.primary }"
          >
            {{ '👥' }}
          </div>
          <div class="contact-info">
            <div class="contact-name">
              {{ cls.name }}
            </div>
            <div class="contact-sub">
              {{ classGroupChat$() }}
              <span v-if="cls.facility_name"> • {{ cls.facility_name }}</span>
            </div>
          </div>
        </button>

        <!-- Direct Contacts -->
        <div class="contact-group-header">
          {{ directContacts$() }}
        </div>
        <button
          v-for="c in filteredContacts"
          :key="c.id"
          type="button"
          class="contact-row"
          @click="handleSelectContact(c.id)"
        >
          <div class="contact-avatar user-avatar">
            {{ getInitials(c.full_name || c.username) }}
          </div>
          <div class="contact-info">
            <div class="contact-name">
              {{ c.full_name || c.username }}
              <span
                v-if="c.is_coach"
                class="coach-badge"
              >{{ teacher$() }}</span>
            </div>
            <div class="contact-sub">
              {{ c.facility_name || schoolFacility$() }}
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- Conversations List Mode -->
    <div
      v-else
      class="conversations-scroll-list"
    >
      <div
        v-if="filteredConversations.length === 0"
        class="empty-state"
        :style="{ color: $themeTokens.annotation }"
      >
        <div class="empty-icon">
          {{ '💬' }}
        </div>
        <div>{{ noConversationsYet$() }}</div>
        <button
          type="button"
          class="start-first-btn"
          :style="{ backgroundColor: $themeTokens.primary, color: '#ffffff' }"
          @click="showNewChatModal = true"
        >
          {{ startMessage$() }}
        </button>
      </div>

      <button
        v-for="conv in filteredConversations"
        :key="conv.id"
        type="button"
        class="conversation-row"
        @click="handleOpenConversation(conv)"
      >
        <!-- Avatar -->
        <div class="conv-avatar-wrapper">
          <div
            v-if="conv.kind === 'classroom'"
            class="class-avatar contact-avatar"
            :style="{ backgroundColor: $themeTokens.primary }"
          >
            {{ '👥' }}
          </div>
          <div
            v-else
            class="contact-avatar user-avatar"
          >
            {{ getInitials(conv.title) }}
          </div>
          <!-- Online dot -->
          <span class="online-dot"></span>
        </div>

        <!-- Conversation Details -->
        <div class="conv-details">
          <div class="conv-top-line">
            <span class="conv-title">{{ conv.title }}</span>
            <span
              v-if="conv.last_message"
              class="conv-time"
              :style="{ color: $themeTokens.annotation }"
            >
              {{ formatRelativeTime(conv.last_message.created_at) }}
            </span>
          </div>

          <!-- Facility Tag / Badge for Conversation -->
          <div
            v-if="conv.facility_name"
            class="conv-facility-line"
          >
            <span
              class="facility-chip"
              :style="{ color: $themeTokens.annotation }"
            >
              {{ '🏫 ' + conv.facility_name }}
            </span>
          </div>

          <div class="conv-bottom-line">
            <span
              class="conv-snippet"
              :class="{ 'unread-snippet': conv.unread_count > 0 }"
              :style="{
                color: conv.unread_count > 0 ? $themeTokens.text : $themeTokens.annotation,
              }"
            >
              <span v-if="conv.last_message && conv.last_message.is_self">{{ you$() }}</span>
              {{ conv.last_message ? conv.last_message.content : noMessagesYet$() }}
            </span>

            <span
              v-if="conv.unread_count > 0"
              class="unread-pill"
            >
              {{ conv.unread_count }}
            </span>
          </div>
        </div>
      </button>
    </div>
  </div>

</template>


<script>

  import { ref, computed, onMounted } from 'vue';
  import themeConfig from 'kolibri/styles/themeConfig';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useUser from 'kolibri/composables/useUser';
  import useChat from '../../composables/useChat';

  export const chatListStrings = createTranslator('ChatConversationsListStrings', {
    phieduMessages: {
      message: 'PHIEDU Messages',
      context: 'Popup title',
    },
    facilityLabel: {
      message: 'Facility',
      context: 'Label indicating active facility',
    },
    muteSounds: {
      message: 'Mute sounds',
      context: 'Tooltip to mute sound',
    },
    unmuteSounds: {
      message: 'Unmute sounds',
      context: 'Tooltip to unmute sound',
    },
    newMessage: {
      message: 'New Message',
      context: 'Button to create new message',
    },
    close: {
      message: 'Close',
      context: 'Close button',
    },
    searchPlaceholder: {
      message: 'Search chats or people...',
      context: 'Search placeholder and label',
    },
    newConversation: {
      message: 'New Conversation',
      context: 'Header for new chat modal',
    },
    back: {
      message: '← Back',
      context: 'Back button text',
    },
    classrooms: {
      message: 'CLASSROOMS',
      context: 'Classrooms section header',
    },
    classGroupChat: {
      message: 'Class group chat',
      context: 'Classroom subtitle',
    },
    directContacts: {
      message: 'DIRECT CONTACTS',
      context: 'Contacts section header',
    },
    teacher: {
      message: 'Teacher',
      context: 'Teacher badge label',
    },
    schoolFacility: {
      message: 'School Facility',
      context: 'Default facility label',
    },
    noConversationsYet: {
      message: 'No conversations yet.',
      context: 'Empty conversations message',
    },
    startMessage: {
      message: 'Start a message',
      context: 'Button to start first message',
    },
    you: {
      message: 'You: ',
      context: 'Prefix for messages sent by self',
    },
    noMessagesYet: {
      message: 'No messages yet',
      context: 'Preview text for empty thread',
    },
    phiedu: {
      message: 'PHIEDU',
      context: 'Aria label for PHIEDU logo',
    },
  });

  export default {
    name: 'ChatConversationsList',
    emits: ['close'],
    setup(props, { emit }) {
      const {
        phieduMessages$,
        facilityLabel$,
        muteSounds$,
        unmuteSounds$,
        newMessage$,
        close$,
        searchPlaceholder$,
        newConversation$,
        back$,
        classrooms$,
        classGroupChat$,
        directContacts$,
        teacher$,
        schoolFacility$,
        noConversationsYet$,
        startMessage$,
        you$,
        noMessagesYet$,
        phiedu$,
      } = chatListStrings;

      const { userFacilityName } = useUser();
      const activeFacilityOverride = ref(
        localStorage.getItem('facilityName') ||
          localStorage.getItem('kolibri_active_facility_name') ||
          ''
      );

      const currentFacilityName = computed(() => {
        return (
          activeFacilityOverride.value ||
          userFacilityName.value ||
          themeConfig.appBar?.headerTitle ||
          ''
        );
      });

      const {
        conversations,
        contacts,
        classrooms,
        isMuted,
        fetchConversations,
        fetchContacts,
        openConversation,
        startDirectChat,
        startClassroomChat,
        toggleMute,
      } = useChat();

      const searchQuery = ref('');
      const showNewChatModal = ref(false);

      const facilityLogoUrl = computed(() => {
        return themeConfig.appBar.topLogo?.src || themeConfig.signIn.topLogo?.src || null;
      });

      const headerBg = computed(() => {
        return themeConfig.appBar.background || '#1d4ed8';
      });

      const headerTextColor = computed(() => {
        return themeConfig.appBar.textColor || '#ffffff';
      });

      const filteredConversations = computed(() => {
        const q = searchQuery.value.trim().toLowerCase();
        if (!q) return conversations.value;
        return conversations.value.filter(c => {
          return (
            (c.title && c.title.toLowerCase().includes(q)) ||
            (c.last_message &&
              c.last_message.content &&
              c.last_message.content.toLowerCase().includes(q))
          );
        });
      });

      const filteredContacts = computed(() => {
        const q = searchQuery.value.trim().toLowerCase();
        if (!q) return contacts.value;
        return contacts.value.filter(c => {
          const name = c.full_name || c.username;
          return name.toLowerCase().includes(q);
        });
      });

      const filteredClassrooms = computed(() => {
        const q = searchQuery.value.trim().toLowerCase();
        if (!q) return classrooms.value;
        return classrooms.value.filter(c => c.name.toLowerCase().includes(q));
      });

      function getInitials(name) {
        if (!name) return '?';
        const parts = name.trim().split(' ');
        if (parts.length >= 2) {
          return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return name.slice(0, 2).toUpperCase();
      }

      function formatRelativeTime(isoStr) {
        if (!isoStr) return '';
        const date = new Date(isoStr);
        const now = new Date();
        const diffMs = now - date;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffSecs < 60) return 'now';
        if (diffMins < 60) return `${diffMins}m`;
        if (diffHours < 24) return `${diffHours}h`;
        if (diffDays < 7) return `${diffDays}d`;
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
      }

      function handleOpenConversation(conv) {
        openConversation(conv);
        emit('close');
      }

      async function handleSelectContact(userId) {
        await startDirectChat(userId);
        showNewChatModal.value = false;
        emit('close');
      }

      async function handleSelectClassroom(classroomId) {
        await startClassroomChat(classroomId);
        showNewChatModal.value = false;
        emit('close');
      }

      onMounted(() => {
        fetchConversations();
        fetchContacts();
        const facilityHandler = e => {
          if (e.detail && e.detail.name) {
            activeFacilityOverride.value = e.detail.name;
          }
        };
        window.addEventListener('kolibri-facility-changed', facilityHandler);
      });

      return {
        classrooms,
        isMuted,
        searchQuery,
        showNewChatModal,
        facilityLogoUrl,
        currentFacilityName,
        headerBg,
        headerTextColor,
        filteredConversations,
        filteredContacts,
        filteredClassrooms,
        getInitials,
        formatRelativeTime,
        handleOpenConversation,
        handleSelectContact,
        handleSelectClassroom,
        toggleMute,
        phieduMessages$,
        facilityLabel$,
        muteSounds$,
        unmuteSounds$,
        newMessage$,
        close$,
        searchPlaceholder$,
        newConversation$,
        back$,
        classrooms$,
        classGroupChat$,
        directContacts$,
        teacher$,
        schoolFacility$,
        noConversationsYet$,
        startMessage$,
        you$,
        noMessagesYet$,
        phiedu$,
      };
    },
  };

</script>


<style scoped>

  .phiedu-conversations-popup {
    position: fixed;
    right: 20px;
    bottom: 84px;
    z-index: 10002;
    display: flex;
    flex-direction: column;
    width: 360px;
    height: 480px;
    overflow: hidden;
    background-color: #ffffff;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 14px;
    box-shadow:
      0 10px 32px rgba(0, 0, 0, 0.22),
      0 3px 10px rgba(0, 0, 0, 0.12);
  }

  /* Header */
  .popup-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 52px;
    padding: 0 12px;
    user-select: none;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .header-left {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .header-branding {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .school-facility-badge {
    position: absolute;
    top: -3px;
    left: -5px;
    z-index: 2;
    width: 18px;
    height: 18px;
    overflow: hidden;
    object-fit: cover;
    background: #ffffff;
    border: 1px solid #ffffff;
    border-radius: 50%;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  }

  .phiedu-mini-logo {
    width: 30px;
    height: 30px;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  }

  .app-title {
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.2px;
  }

  .header-actions {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .hdr-action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    font-size: 14px;
    color: inherit;
    cursor: pointer;
    background: transparent;
    border: 0;
    border-radius: 50%;
    opacity: 0.9;
    transition: background 0.15s;
  }

  .hdr-action-btn:hover {
    background-color: rgba(255, 255, 255, 0.2);
  }

  /* Active Facility Strip */
  .active-facility-strip {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 500;
    user-select: none;
  }

  .facility-icon {
    font-size: 12px;
    line-height: 1;
  }

  .facility-label {
    font-weight: 600;
  }

  .facility-name-text {
    font-weight: 700;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* Search Bar */
  .search-bar-wrapper {
    padding: 8px 12px;
    border-bottom: 1px solid;
  }

  .search-input {
    box-sizing: border-box;
    width: 100%;
    padding: 7px 12px;
    font-size: 13px;
    border: 0;
    border-radius: 16px;
    outline: none;
  }

  /* Scroll Lists */
  .conversations-scroll-list,
  .contacts-scroll-list {
    flex: 1;
    overflow-y: auto;
  }

  .conversation-row,
  .contact-row {
    box-sizing: border-box;
    display: flex;
    gap: 12px;
    align-items: center;
    width: 100%;
    padding: 10px 14px;
    font-family: inherit;
    text-align: left;
    cursor: pointer;
    background: transparent;
    border: 0;
    transition: background-color 0.15s;
  }

  .conversation-row:hover,
  .contact-row:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }

  .conv-avatar-wrapper {
    position: relative;
  }

  .contact-avatar {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
    background-color: #6366f1;
    border-radius: 50%;
  }

  .class-avatar {
    font-size: 18px;
  }

  .online-dot {
    position: absolute;
    right: 0;
    bottom: 0;
    width: 10px;
    height: 10px;
    background-color: #22c55e;
    border: 2px solid #ffffff;
    border-radius: 50%;
  }

  .conv-details,
  .contact-info {
    flex: 1;
    overflow: hidden;
  }

  .conv-top-line {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 3px;
  }

  .conv-title,
  .contact-name {
    overflow: hidden;
    font-size: 13px;
    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .conv-time {
    font-size: 10px;
  }

  .conv-bottom-line {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .conv-snippet,
  .contact-sub {
    max-width: 220px;
    overflow: hidden;
    font-size: 11px;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .unread-snippet {
    font-weight: 700;
  }

  .unread-pill {
    padding: 1px 6px;
    font-size: 10px;
    font-weight: 700;
    color: #ffffff;
    background-color: #ef4444;
    border-radius: 10px;
  }

  .coach-badge {
    padding: 2px 6px;
    margin-left: 6px;
    font-size: 9px;
    font-weight: 700;
    color: #1d4ed8;
    background-color: #dbeafe;
    border-radius: 6px;
  }

  .conv-facility-line {
    margin-top: 1px;
    margin-bottom: 2px;
    line-height: 1.2;
  }

  .facility-chip {
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    font-size: 10px;
    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* Contacts Mode */
  .contacts-mode-container {
    display: flex;
    flex: 1;
    flex-direction: column;
    overflow: hidden;
  }

  .contacts-mode-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 600;
    border-bottom: 1px solid;
  }

  .back-btn {
    font-weight: 600;
    color: #2563eb;
    cursor: pointer;
    background: transparent;
    border: 0;
  }

  .contact-group-header {
    padding: 8px 14px 4px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
    opacity: 0.6;
  }

  /* Empty State */
  .empty-state {
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 20px;
    font-size: 13px;
    text-align: center;
  }

  .empty-icon {
    font-size: 36px;
  }

  .start-first-btn {
    padding: 8px 16px;
    margin-top: 6px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    border: 0;
    border-radius: 16px;
  }

</style>
