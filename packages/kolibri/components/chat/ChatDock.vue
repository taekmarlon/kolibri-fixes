<template>

  <div
    v-if="chatheads && chatheads.length > 0"
    class="phiedu-chat-dock"
  >
    <button
      v-for="c in chatheads"
      :key="c.id"
      type="button"
      class="chathead-item"
      :title="c.title"
      @click="$emit('restore', c)"
    >
      <!-- Chathead circle avatar -->
      <div
        class="chathead-avatar"
        :style="{
          backgroundColor: c.kind === 'classroom' ? '#2563eb' : '#3b82f6',
        }"
      >
        <span
          v-if="c.kind === 'classroom'"
          class="chathead-icon"
        >{{ '👥' }}</span>
        <span
          v-else
          class="chathead-initials"
        >{{ getInitials(c.title) }}</span>
      </div>

      <!-- Online status dot -->
      <span class="online-indicator"></span>

      <!-- Unread badge counter -->
      <span
        v-if="c.unread_count > 0"
        class="chathead-unread"
      >
        {{ c.unread_count > 9 ? '9+' : c.unread_count }}
      </span>

      <!-- Hover dismiss button -->
      <button
        type="button"
        class="chathead-close-btn"
        :title="closeChathead$()"
        :aria-label="close$()"
        @click.stop="$emit('close', c.id)"
      >
        {{ '✕' }}
      </button>

      <!-- Hover tooltip -->
      <div class="chathead-tooltip">
        {{ c.title }}
      </div>
    </button>
  </div>

</template>


<script>

  import { createTranslator } from 'kolibri/utils/i18n';

  const chatDockStrings = createTranslator('ChatDockStrings', {
    closeChathead: {
      message: 'Close chathead',
      context: 'Tooltip for button to close minimized chathead',
    },
    close: {
      message: 'Close',
      context: 'Aria label for close button',
    },
  });

  export default {
    name: 'ChatDock',
    setup() {
      const { closeChathead$, close$ } = chatDockStrings;

      function getInitials(name) {
        if (!name) return '?';
        const parts = name.trim().split(' ');
        if (parts.length >= 2) {
          return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return name.slice(0, 2).toUpperCase();
      }

      return {
        getInitials,
        closeChathead$,
        close$,
      };
    },
    props: {
      chatheads: {
        type: Array,
        default: () => [],
      },
    },
    emits: ['restore', 'close'],
  };

</script>


<style scoped>

  .phiedu-chat-dock {
    position: fixed;
    right: 88px;
    bottom: 24px;
    z-index: 10001;
    display: flex;
    flex-direction: row-reverse;
    gap: 12px;
    align-items: center;
    pointer-events: none; /* Let empty space pass through */
  }

  .chathead-item {
    position: relative;
    width: 48px;
    height: 48px;
    padding: 0;
    pointer-events: auto;
    cursor: pointer;
    background: transparent;
    border: 0;
    border-radius: 50%;
    box-shadow:
      0 4px 12px rgba(0, 0, 0, 0.2),
      0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .chathead-item:hover {
    transform: scale(1.1);
  }

  .chathead-avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    user-select: none;
    border: 2px solid #ffffff;
    border-radius: 50%;
  }

  .chathead-icon {
    font-size: 18px;
  }

  .chathead-initials {
    letter-spacing: 0.5px;
  }

  /* Online indicator */
  .online-indicator {
    position: absolute;
    right: 1px;
    bottom: 1px;
    width: 12px;
    height: 12px;
    background-color: #22c55e;
    border: 2px solid #ffffff;
    border-radius: 50%;
  }

  /* Unread badge */
  .chathead-unread {
    position: absolute;
    top: -4px;
    right: -4px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 18px;
    height: 18px;
    padding: 0 4px;
    font-size: 10px;
    font-weight: 800;
    color: #ffffff;
    background-color: #ef4444;
    border: 2px solid #ffffff;
    border-radius: 9px;
    animation: bounce-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  /* Hover close button */
  .chathead-close-btn {
    position: absolute;
    top: -6px;
    left: -6px;
    display: none;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    padding: 0;
    font-size: 10px;
    line-height: 1;
    color: #ffffff;
    cursor: pointer;
    background-color: #4b5563;
    border: 2px solid #ffffff;
    border-radius: 50%;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  }

  .chathead-item:hover .chathead-close-btn {
    display: flex;
  }

  .chathead-close-btn:hover {
    background-color: #ef4444;
  }

  /* Hover Tooltip */
  .chathead-tooltip {
    position: absolute;
    bottom: 56px;
    left: 50%;
    display: none;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 500;
    color: #ffffff;
    white-space: nowrap;
    pointer-events: none;
    background-color: rgba(17, 24, 39, 0.9);
    border-radius: 6px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    transform: translateX(-50%);
  }

  .chathead-item:hover .chathead-tooltip {
    display: block;
  }

  @keyframes bounce-in {
    0% {
      transform: scale(0);
    }

    100% {
      transform: scale(1);
    }
  }

</style>
