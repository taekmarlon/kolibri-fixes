<template>

  <div class="phiedu-launcher-wrapper">
    <button
      type="button"
      class="phiedu-launcher-btn"
      :class="{ 'is-open': isOpen }"
      :style="{
        backgroundColor: launcherBg,
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.22), 0 2px 6px rgba(0, 0, 0, 0.14)',
      }"
      :aria-label="phieduMessages$()"
      :title="isOpen ? closeMessages$() : openMessages$()"
      @click="$emit('toggle')"
    >
      <!-- If open, show close 'X' icon -->
      <svg
        v-if="isOpen"
        class="close-icon launcher-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <line
          x1="18"
          y1="6"
          x2="6"
          y2="18"
        />
        <line
          x1="6"
          y1="6"
          x2="18"
          y2="18"
        />
      </svg>

      <!-- Otherwise show PHIEDU Messenger emblem -->
      <div
        v-else
        class="launcher-icon-group"
      >
        <!-- Messenger chat bubble with PHIEDU educational book emblem -->
        <svg
          class="launcher-icon messenger-icon"
          viewBox="0 0 48 48"
          fill="none"
        >
          <!-- Chat bubble outline / fill -->
          <path
            d="M24 6C13.5 6 5 13.8 5 23.5C5 28.8 7.6 33.6 11.9 36.8L10 44
               L17.7 40.5C19.7 41.1 21.8 41.5 24 41.5C34.5 41.5 43 33.7 43 24C43 14.3 34.5 6 24 6Z"
            fill="#ffffff"
          />
          <!-- PHIEDU Book emblem in primary color -->
          <path
            d="M17 19C17 18.2 17.8 17.5 18.8 17.5H23V29.5H18.8C17.8 29.5 17 28.8 17 28V19Z"
            :fill="launcherBg"
          />
          <path
            d="M31 19C31 18.2 30.2 17.5 29.2 17.5H25V29.5H29.2C30.2 29.5 31 28.8 31 28V19Z"
            :fill="launcherBg"
          />
          <line
            x1="24"
            y1="17.5"
            x2="24"
            y2="30.5"
            :stroke="launcherBg"
            stroke-width="1.8"
          />
        </svg>
      </div>

      <!-- Facility Logo Badge (Bottom-Left) -->
      <div
        v-if="facilityLogoUrl"
        class="facility-badge"
        :title="schoolFacility$()"
      >
        <img
          :src="facilityLogoUrl"
          :alt="schoolFacility$()"
          class="facility-badge-img"
        >
      </div>

      <!-- Unread Badge Counter (Top-Right) -->
      <div
        v-if="unreadCount > 0 && !isOpen"
        class="launcher-unread-badge"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </div>
    </button>
  </div>

</template>


<script>

  import { computed } from 'vue';
  import themeConfig from 'kolibri/styles/themeConfig';
  import { createTranslator } from 'kolibri/utils/i18n';

  export const launcherStrings = createTranslator('ChatLauncherStrings', {
    phieduMessages: {
      message: 'PHIEDU Messages',
      context: 'Title for the chat messaging system',
    },
    openMessages: {
      message: 'Open PHIEDU Messages',
      context: 'Tooltip to open chat messages dock',
    },
    closeMessages: {
      message: 'Close PHIEDU Messages',
      context: 'Tooltip to close chat messages dock',
    },
    schoolFacility: {
      message: 'School Facility',
      context: 'Alt text for facility badge image',
    },
  });

  export default {
    name: 'ChatLauncher',
    setup() {
      const { phieduMessages$, openMessages$, closeMessages$, schoolFacility$ } = launcherStrings;

      const launcherBg = computed(() => {
        return themeConfig.appBar.background || '#1d4ed8';
      });

      const facilityLogoUrl = computed(() => {
        return themeConfig.appBar.topLogo?.src || themeConfig.signIn.topLogo?.src || null;
      });

      return {
        launcherBg,
        facilityLogoUrl,
        phieduMessages$,
        openMessages$,
        closeMessages$,
        schoolFacility$,
      };
    },
    props: {
      isOpen: {
        type: Boolean,
        default: false,
      },
      unreadCount: {
        type: Number,
        default: 0,
      },
    },
    emits: ['toggle'],
  };

</script>


<style scoped>

  .phiedu-launcher-wrapper {
    position: fixed;
    right: 20px;
    bottom: 20px;
    z-index: 10001;
  }

  .phiedu-launcher-btn {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    padding: 0;
    cursor: pointer;
    border: 2px solid rgba(255, 255, 255, 0.25);
    border-radius: 50%;
    outline: none;
    transition:
      transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1),
      box-shadow 0.2s ease;
  }

  .phiedu-launcher-btn:hover {
    box-shadow:
      0 6px 20px rgba(0, 0, 0, 0.3),
      0 3px 8px rgba(0, 0, 0, 0.16) !important;
    transform: scale(1.08);
  }

  .phiedu-launcher-btn:active {
    transform: scale(0.96);
  }

  .launcher-icon-group {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
  }

  .launcher-icon {
    width: 32px;
    height: 32px;
  }

  .close-icon {
    width: 24px;
    height: 24px;
    color: #ffffff;
  }

  /* School Facility Badge (bottom-left) */
  .facility-badge {
    position: absolute;
    bottom: -3px;
    left: -3px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    overflow: hidden;
    background-color: #ffffff;
    border: 2px solid #ffffff;
    border-radius: 50%;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
  }

  .facility-badge-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  /* Unread Badge (top-right) */
  .launcher-unread-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 20px;
    height: 20px;
    padding: 0 5px;
    font-size: 11px;
    font-weight: 700;
    color: #ffffff;
    background-color: #ef4444;
    border: 2px solid #ffffff;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    animation: bounce-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
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
