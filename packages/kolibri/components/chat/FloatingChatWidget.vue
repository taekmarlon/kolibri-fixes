<template>

  <div class="phiedu-floating-chat-root">
    <!-- Active Floating Windows (capped at 3) -->
    <ChatWindow
      v-for="(conv, idx) in activeWindows"
      :key="conv.id"
      :conversation="conv"
      :dockIndex="idx"
      @minimize="minimizeConversation(conv.id)"
      @close="closeConversation(conv.id)"
    />

    <!-- Conversations Popup (Docked above launcher button) -->
    <ChatConversationsList
      v-if="isConversationsListOpen"
      @close="isConversationsListOpen = false"
    />

    <!-- Minimized Floating Chatheads Dock -->
    <ChatDock
      :chatheads="minimizedChatheads"
      @restore="restoreConversation"
      @close="closeConversation"
    />

    <!-- Bottom-Right Floating Launcher Button -->
    <ChatLauncher
      :isOpen="isConversationsListOpen"
      :unreadCount="totalUnreadCount"
      @toggle="isConversationsListOpen = !isConversationsListOpen"
    />
  </div>

</template>


<script>

  import { onMounted, onUnmounted } from 'vue';
  import useChat from '../../composables/useChat';
  import useChatRealtime from '../../composables/useChatRealtime';
  import ChatLauncher from './ChatLauncher';
  import ChatDock from './ChatDock';
  import ChatConversationsList from './ChatConversationsList';
  import ChatWindow from './ChatWindow';

  export default {
    name: 'FloatingChatWidget',
    components: {
      ChatLauncher,
      ChatDock,
      ChatConversationsList,
      ChatWindow,
    },
    setup() {
      const {
        activeWindows,
        minimizedChatheads,
        totalUnreadCount,
        isConversationsListOpen,
        fetchConversations,
        minimizeConversation,
        closeConversation,
        restoreConversation,
      } = useChat();

      const { startRealtime, stopRealtime } = useChatRealtime();

      onMounted(() => {
        fetchConversations();
        startRealtime();
      });

      onUnmounted(() => {
        stopRealtime();
      });

      return {
        activeWindows,
        minimizedChatheads,
        totalUnreadCount,
        isConversationsListOpen,
        minimizeConversation,
        closeConversation,
        restoreConversation,
      };
    },
  };

</script>


<style scoped>

  .phiedu-floating-chat-root {
    position: fixed;
    right: 0;
    bottom: 0;
    z-index: 10000;

    /* Let background clicks pass through; interactive widgets have pointer-events: auto */
    pointer-events: none;
  }

  /* Make sure children receive pointer events */
  .phiedu-floating-chat-root > * {
    pointer-events: auto;
  }

</style>
