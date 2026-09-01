<template>

  <div class="live-meeting-container" :style="{ backgroundColor: $themeTokens.surface }">
    <!-- Top Meeting Bar -->
    <div
      class="meeting-header"
      :style="{
        backgroundColor: $themeTokens.surface,
        borderBottom: `1px solid ${$themeTokens.fineLine}`,
      }"
    >
      <div class="header-left">
        <KIcon icon="group" class="meeting-icon" :style="{ color: $themeTokens.primary }" />
        <div class="meeting-info">
          <h2 class="meeting-title" :style="{ color: $themeTokens.text }">
            {{ meetingTitle || defaultTitle$() }}
          </h2>
          <span class="meeting-room-name" :style="{ color: $themeTokens.annotation }">
            {{ roomLabel$({ roomName: formattedRoomName }) }}
          </span>
        </div>
      </div>

      <div class="header-actions">
        <KButton
          :text="copied ? linkCopied$() : copyLink$()"
          icon="copy"
          appearance="basic-flat-button"
          :primary="false"
          @click="copyMeetingLink"
        />

        <KButton
          v-if="!isFullscreen"
          :text="fullscreen$()"
          icon="fullscreen"
          appearance="basic-flat-button"
          :primary="false"
          @click="toggleFullscreen"
        />
        <KButton
          v-else
          :text="exitFullscreen$()"
          icon="fullscreen_exit"
          appearance="basic-flat-button"
          :primary="false"
          @click="toggleFullscreen"
        />

        <KButton
          :text="leaveMeeting$()"
          appearance="raised-button"
          :style="{ backgroundColor: $themeTokens.error, color: 'white' }"
          @click="handleLeave"
        />
      </div>
    </div>

    <!-- Video Frame Area -->
    <div ref="meetingWrapper" class="meeting-frame-wrapper">
      <!-- Loading Spinner -->
      <div
        v-if="loading"
        class="loading-overlay"
        :style="{ backgroundColor: $themePalette.grey.v_200 }"
      >
        <KCircularLoader :delay="false" />
        <p :style="{ color: $themeTokens.text, marginTop: '16px', fontWeight: 'bold' }">
          {{ connecting$() }}
        </p>
      </div>

      <!-- Direct Jitsi Meet Iframe (100% reliable with WebRTC permissions) -->
      <iframe
        class="jitsi-iframe"
        :src="jitsiIframeUrl"
        allow="camera *; microphone *; display-capture *; autoplay *; clipboard-write *; fullscreen *"
        frameBorder="0"
        @load="onIframeLoad"
      ></iframe>
    </div>
  </div>

</template>


<script>

  import { ref, computed, onMounted } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useUser from 'kolibri/composables/useUser';

  const liveMeetingStrings = createTranslator('LiveMeetingStrings', {
    defaultTitle: {
      message: 'Live Virtual Classroom',
      context: 'Title of the virtual classroom / video meeting window',
    },
    roomLabel: {
      message: 'Room: {roomName}',
      context: 'Display name of the meeting room',
    },
    copyLink: {
      message: 'Copy Link',
      context: 'Button label to copy the meeting room link',
    },
    linkCopied: {
      message: 'Copied!',
      context: 'Confirmation that the meeting link was copied',
    },
    fullscreen: {
      message: 'Fullscreen',
      context: 'Button to expand meeting to fullscreen',
    },
    exitFullscreen: {
      message: 'Exit Fullscreen',
      context: 'Button to exit fullscreen meeting',
    },
    leaveMeeting: {
      message: 'Leave Meeting',
      context: 'Button to leave/hang up the video meeting',
    },
    connecting: {
      message: 'Connecting to live video meeting...',
      context: 'Loading status while connecting to Jitsi server',
    },
  });

  export default {
    name: 'LiveMeeting',
    props: {
      roomName: {
        type: String,
        required: true,
      },
      meetingTitle: {
        type: String,
        default: '',
      },
      jitsiDomain: {
        type: String,
        default: 'meet.jit.si',
      },
    },
    emits: ['leave'],
    setup(props, { emit }) {
      const { full_name, username } = useUser();
      const {
        defaultTitle$,
        roomLabel$,
        copyLink$,
        linkCopied$,
        fullscreen$,
        exitFullscreen$,
        leaveMeeting$,
        connecting$,
      } = liveMeetingStrings;

      const meetingWrapper = ref(null);
      const loading = ref(true);
      const copied = ref(false);
      const isFullscreen = ref(false);

      const userDisplayName = computed(() => {
        return full_name.value || username.value || 'Kolibri User';
      });

      const formattedRoomName = computed(() => {
        return props.roomName.replace(/[^a-zA-Z0-9-_]/g, '_');
      });

      const jitsiIframeUrl = computed(() => {
        const name = encodeURIComponent(userDisplayName.value);
        return `https://${props.jitsiDomain}/${formattedRoomName.value}#userInfo.displayName="${name}"&config.prejoinPageEnabled=false&config.startWithAudioMuted=true&config.disableDeepLinking=true`;
      });

      function onIframeLoad() {
        loading.value = false;
      }

      function handleLeave() {
        emit('leave');
      }

      function copyMeetingLink() {
        const url = window.location.href;
        if (navigator.clipboard) {
          navigator.clipboard.writeText(url).then(() => {
            copied.value = true;
            setTimeout(() => {
              copied.value = false;
            }, 3000);
          });
        }
      }

      function toggleFullscreen() {
        if (!meetingWrapper.value) return;
        if (!document.fullscreenElement) {
          meetingWrapper.value.requestFullscreen().then(() => {
            isFullscreen.value = true;
          });
        } else {
          document.exitFullscreen().then(() => {
            isFullscreen.value = false;
          });
        }
      }

      onMounted(() => {
        // Fallback timer to hide loader if iframe takes a moment
        setTimeout(() => {
          loading.value = false;
        }, 3000);

        document.addEventListener('fullscreenchange', () => {
          isFullscreen.value = Boolean(document.fullscreenElement);
        });
      });

      return {
        meetingWrapper,
        loading,
        copied,
        isFullscreen,
        userDisplayName,
        formattedRoomName,
        jitsiIframeUrl,
        defaultTitle$,
        roomLabel$,
        copyLink$,
        linkCopied$,
        fullscreen$,
        exitFullscreen$,
        leaveMeeting$,
        connecting$,
        onIframeLoad,
        handleLeave,
        copyMeetingLink,
        toggleFullscreen,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .live-meeting-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    min-height: 650px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .meeting-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 20px;
    flex-wrap: wrap;
    gap: 12px;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .meeting-icon {
    font-size: 28px;
  }

  .meeting-info {
    display: flex;
    flex-direction: column;
  }

  .meeting-title {
    margin: 0;
    font-size: 1.15rem;
    font-weight: bold;
  }

  .meeting-room-name {
    font-size: 0.85rem;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .meeting-frame-wrapper {
    position: relative;
    flex: 1;
    width: 100%;
    min-height: 600px;
    background-color: #111;
  }

  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 10;
  }

  .jitsi-iframe {
    width: 100%;
    height: 100%;
    min-height: 600px;
    border: none;
    display: block;
  }

</style>
