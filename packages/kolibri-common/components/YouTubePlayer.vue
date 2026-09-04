<template>
  <div
    class="youtube-player-container"
    :class="{ 'is-fullscreen': isFullscreen }"
    :style="{
      backgroundColor: $themeTokens.surface,
      borderColor: $themeTokens.fineLine,
    }"
  >
    <!-- Header Toolbar -->
    <div
      class="youtube-header"
      :style="{
        backgroundColor: $themePalette.grey.v_100,
        borderBottom: `1px solid ${$themeTokens.fineLine}`,
      }"
    >
      <div class="header-left">
        <span class="youtube-badge">▶ YouTube</span>
        <span class="video-title" :style="{ color: $themeTokens.text }">
          {{ title || videoTitleText$() }}
        </span>
        <span
          class="safe-tag"
          :style="{ backgroundColor: $themeTokens.primary, color: 'white' }"
        >
          {{ nativePlayerLabel$() }}
        </span>
      </div>

      <div class="header-actions">
        <!-- Fullscreen Button -->
        <button
          type="button"
          class="action-btn"
          :title="isFullscreen ? exitFullscreenLabel$() : enterFullscreenLabel$()"
          @click="toggleFullscreen"
        >
          <span>{{ isFullscreen ? '🗗' : '⛶' }}</span>
          <span class="btn-label">{{ isFullscreen ? exitLabel$() : fullscreenLabel$() }}</span>
        </button>
      </div>
    </div>

    <!-- Video Frame Wrapper -->
    <div class="player-wrapper">
      <div v-if="embedUrl" class="aspect-ratio-box">
        <iframe
          :src="embedUrl"
          class="youtube-iframe"
          title="YouTube video player"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowfullscreen
          sandbox="allow-scripts allow-same-origin allow-presentation"
        ></iframe>
      </div>
      <div
        v-else
        class="no-video-placeholder"
        :style="{ color: $themeTokens.annotation }"
      >
        <p>⚠️ {{ invalidUrlMessage$() }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref } from 'vue';
import { createTranslator } from 'kolibri/utils/i18n';

const strings = createTranslator('YouTubePlayerStrings', {
  videoTitleText: { message: 'Video Resource', context: 'Fallback title for video' },
  nativePlayerLabel: { message: 'Native In-Kolibri Player', context: 'Badge label' },
  fullscreenLabel: { message: 'Fullscreen', context: 'Button label' },
  exitFullscreenLabel: { message: 'Exit Fullscreen', context: 'Tooltip' },
  enterFullscreenLabel: { message: 'Enter Fullscreen', context: 'Tooltip' },
  exitLabel: { message: 'Exit', context: 'Button label' },
  invalidUrlMessage: { message: 'Please provide a valid YouTube video URL or ID.', context: 'Error message' },
});

export default {
  name: 'YouTubePlayer',
  props: {
    videoUrl: {
      type: String,
      default: '',
    },
    videoId: {
      type: String,
      default: '',
    },
    title: {
      type: String,
      default: '',
    },
  },
  setup(props) {
    const isFullscreen = ref(false);
    const {
      videoTitleText$,
      nativePlayerLabel$,
      fullscreenLabel$,
      exitFullscreenLabel$,
      enterFullscreenLabel$,
      exitLabel$,
      invalidUrlMessage$,
    } = strings;

    const parsedVideoId = computed(() => {
      if (props.videoId && /^[a-zA-Z0-9_-]{11}$/.test(props.videoId.trim())) {
        return props.videoId.trim();
      }
      const url = (props.videoUrl || '').trim();
      if (!url) {
        return '';
      }

      // Check for 11-char ID directly
      if (/^[a-zA-Z0-9_-]{11}$/.test(url)) {
        return url;
      }

      // Check standard youtube.com/watch?v=ID
      const watchMatch = url.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
      if (watchMatch) {
        return watchMatch[1];
      }

      // Check youtu.be/ID
      const shortMatch = url.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/);
      if (shortMatch) {
        return shortMatch[1];
      }

      // Check youtube.com/embed/ID or youtube-nocookie.com/embed/ID
      const embedMatch = url.match(/youtube(?:-nocookie)?\.com\/embed\/([a-zA-Z0-9_-]{11})/);
      if (embedMatch) {
        return embedMatch[1];
      }

      // Check shorts URL: youtube.com/shorts/ID
      const shortsMatch = url.match(/youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/);
      if (shortsMatch) {
        return shortsMatch[1];
      }

      return '';
    });

    const embedUrl = computed(() => {
      const id = parsedVideoId.value;
      if (!id) {
        return '';
      }
      // Privacy-enhanced mode, rel=0 prevents external channel recommendations
      return 'https://www.youtube-nocookie.com/embed/' + id + '?rel=0&modestbranding=1&enablejsapi=1';
    });

    function toggleFullscreen() {
      isFullscreen.value = !isFullscreen.value;
    }

    return {
      isFullscreen,
      embedUrl,
      toggleFullscreen,
      videoTitleText$,
      nativePlayerLabel$,
      fullscreenLabel$,
      exitFullscreenLabel$,
      enterFullscreenLabel$,
      exitLabel$,
      invalidUrlMessage$,
    };
  },
};
</script>

<style lang="scss" scoped>
.youtube-player-container {
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  border-style: solid;
  border-width: 1px;
  overflow: hidden;
  margin: 16px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

  &.is-fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 999999;
    border-radius: 0;
    margin: 0;

    .player-wrapper {
      flex: 1;
      height: 100%;
    }

    .aspect-ratio-box {
      padding-top: 0;
      height: 100%;
    }

    .youtube-iframe {
      height: 100%;
    }
  }
}

.youtube-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  gap: 8px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.youtube-badge {
  background-color: #ff0000;
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 0.5px;
}

.video-title {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.safe-tag {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  font-size: 12px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;

  &:hover {
    background: #f3f4f6;
  }
}

.player-wrapper {
  position: relative;
  width: 100%;
  background-color: #000000;
}

.aspect-ratio-box {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 Aspect Ratio */
}

.youtube-iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 0;
}

.no-video-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 16px;
  font-size: 14px;
  text-align: center;
}
</style>
