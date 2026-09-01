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
        <KIcon icon="group" class="meeting-icon" />
        <div class="meeting-info">
          <h2 class="meeting-title" :style="{ color: $themeTokens.text }">
            {{ meetingTitle || defaultTitle$() }}
          </h2>
          <span class="meeting-room-name" :style="{ color: $themeTokens.annotation }">
            {{ $tr('roomLabel', { roomName: formattedRoomName }) }}
          </span>
        </div>
      </div>

      <div class="header-actions">
        <KButton
          :text="copied ? $tr('linkCopied') : $tr('copyLink')"
          icon="copy"
          appearance="basic-flat-button"
          :primary="false"
          @click="copyMeetingLink"
        />

        <KButton
          v-if="!isFullscreen"
          :text="$tr('fullscreen')"
          icon="fullscreen"
          appearance="basic-flat-button"
          :primary="false"
          @click="toggleFullscreen"
        />
        <KButton
          v-else
          :text="$tr('exitFullscreen')"
          icon="fullscreen_exit"
          appearance="basic-flat-button"
          :primary="false"
          @click="toggleFullscreen"
        />

        <KButton
          :text="$tr('leaveMeeting')"
          appearance="raised-button"
          :style="{ backgroundColor: $themeTokens.error, color: 'white' }"
          @click="handleLeave"
        />
      </div>
    </div>

    <!-- Video Frame Area -->
    <div ref="meetingWrapper" class="meeting-frame-wrapper">
      <div
        v-if="loading"
        class="loading-overlay"
        :style="{ backgroundColor: $themePalette.grey.v_200 }"
      >
        <KCircularLoader :delay="false" />
        <p :style="{ color: $themeTokens.text, marginTop: '16px' }">
          {{ $tr('connecting') }}
        </p>
      </div>

      <!-- Jitsi target container -->
      <div id="jitsi-meet-target" ref="jitsiContainer" class="jitsi-target"></div>

      <!-- Fallback direct iframe if external_api.js is unavailable -->
      <iframe
        v-if="useIframeFallback"
        class="fallback-iframe"
        :src="fallbackIframeUrl"
        allow="camera; microphone; display-capture; autoplay; clipboard-write"
        frameBorder="0"
      ></iframe>
    </div>
  </div>

</template>


<script>

  import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
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
      const { defaultTitle$ } = liveMeetingStrings;

      const jitsiContainer = ref(null);
      const meetingWrapper = ref(null);
      const loading = ref(true);
      const copied = ref(false);
      const isFullscreen = ref(false);
      const useIframeFallback = ref(false);
      let jitsiApi = null;

      const userDisplayName = computed(() => {
        return full_name.value || username.value || 'Kolibri User';
      });

      const formattedRoomName = computed(() => {
        // Clean room name: only alphanumeric and underscores/dashes
        return props.roomName.replace(/[^a-zA-Z0-9-_]/g, '_');
      });

      const fallbackIframeUrl = computed(() => {
        const name = encodeURIComponent(userDisplayName.value);
        return `https://${props.jitsiDomain}/${formattedRoomName.value}#userInfo.displayName="${name}"&config.startWithAudioMuted=true&config.prejoinPageEnabled=false`;
      });

      function loadJitsiScript() {
        return new Promise((resolve, reject) => {
          if (window.JitsiMeetExternalAPI) {
            resolve();
            return;
          }
          const script = document.createElement('script');
          script.src = `https://${props.jitsiDomain}/external_api.js`;
          script.async = true;
          script.onload = () => resolve();
          script.onerror = () => reject(new Error('Failed to load Jitsi API'));
          document.head.appendChild(script);
        });
      }

      function initJitsi() {
        loadJitsiScript()
          .then(() => {
            if (!jitsiContainer.value) return;

            const options = {
              roomName: formattedRoomName.value,
              parentNode: jitsiContainer.value,
              width: '100%',
              height: '100%',
              userInfo: {
                displayName: userDisplayName.value,
              },
              configOverwrite: {
                startWithAudioMuted: false,
                startWithVideoMuted: false,
                disableDeepLinking: true,
                prejoinPageEnabled: false,
                enableWelcomePage: false,
                enableClosePage: false,
              },
              interfaceConfigOverwrite: {
                TOOLBAR_BUTTONS: [
                  'microphone',
                  'camera',
                  'closedcaptions',
                  'desktop',
                  'fullscreen',
                  'fodeviceselection',
                  'hangup',
                  'chat',
                  'raisehand',
                  'videoquality',
                  'filmstrip',
                  'tileview',
                  'videobackgroundblur',
                  'mute-everyone',
                ],
                SHOW_JITSI_WATERMARK: false,
                SHOW_WATERMARK_FOR_GUESTS: false,
              },
            };

            jitsiApi = new window.JitsiMeetExternalAPI(props.jitsiDomain, options);
            loading.value = false;

            jitsiApi.addEventListener('readyToClose', () => {
              handleLeave();
            });
          })
          .catch(() => {
            // If script tag is blocked, use direct iframe
            useIframeFallback.value = true;
            loading.value = false;
          });
      }

      function handleLeave() {
        if (jitsiApi) {
          try {
            jitsiApi.dispose();
          } catch (e) {
            // ignore
          }
          jitsiApi = null;
        }
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
        initJitsi();
        document.addEventListener('fullscreenchange', () => {
          isFullscreen.value = Boolean(document.fullscreenElement);
        });
      });

      onBeforeUnmount(() => {
        if (jitsiApi) {
          try {
            jitsiApi.dispose();
          } catch (e) {
            // ignore
          }
        }
      });

      return {
        jitsiContainer,
        meetingWrapper,
        loading,
        copied,
        isFullscreen,
        useIframeFallback,
        userDisplayName,
        formattedRoomName,
        fallbackIframeUrl,
        defaultTitle$,
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
    min-height: 580px;
    background-color: #000;
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

  .jitsi-target {
    width: 100%;
    height: 100%;
    min-height: 580px;
  }

  .fallback-iframe {
    width: 100%;
    height: 100%;
    min-height: 580px;
    border: none;
  }

</style>
