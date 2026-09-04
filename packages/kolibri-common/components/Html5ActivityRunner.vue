<template>
  <div
    class="html5-activity-container"
    :class="{ 'is-fullscreen': isFullscreen }"
    :style="{
      backgroundColor: $themeTokens.surface,
      borderColor: $themeTokens.fineLine,
    }"
  >
    <!-- Header Toolbar -->
    <div
      class="activity-header"
      :style="{
        backgroundColor: $themePalette.grey.v_100,
        borderBottom: `1px solid ${$themeTokens.fineLine}`,
      }"
    >
      <div class="header-left">
        <span class="activity-icon">🎮</span>
        <span class="activity-title" :style="{ color: $themeTokens.text }">
          {{ title || 'Interactive HTML5 Activity / Simulation' }}
        </span>
        <span class="activity-tag" :style="{ backgroundColor: $themeTokens.primary, color: 'white' }">
          Playable
        </span>
      </div>

      <div class="header-actions">
        <!-- Reset Button -->
        <button
          type="button"
          class="action-btn"
          @click="resetActivity"
          title="Reset / Reload Activity"
        >
          🔄 <span class="btn-label">Reset</span>
        </button>

        <!-- Fullscreen Button -->
        <button
          type="button"
          class="action-btn"
          @click="toggleFullscreen"
          :title="isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'"
        >
          <span>{{ isFullscreen ? '🗗' : '⛶' }}</span>
          <span class="btn-label">{{ isFullscreen ? 'Exit' : 'Fullscreen' }}</span>
        </button>

        <!-- Copy Code Button -->
        <button
          type="button"
          class="action-btn"
          @click="copyCode"
          title="Copy HTML5 Code"
        >
          <span>{{ copied ? '✅' : '📋' }}</span>
          <span class="btn-label">{{ copied ? 'Copied!' : 'Copy Code' }}</span>
        </button>

        <!-- Download HTML Button -->
        <button
          type="button"
          class="action-btn"
          @click="downloadHtml"
          title="Download HTML5 File"
        >
          💾 <span class="btn-label">Download</span>
        </button>
      </div>
    </div>

    <!-- Interactive Sandboxed Iframe -->
    <div class="iframe-wrapper" @click="focusIframe">
      <iframe
        ref="iframeRef"
        :key="reloadKey"
        :srcdoc="processedSrcdoc"
        sandbox="allow-scripts"
        class="activity-iframe"
        title="Interactive HTML5 Activity"
      ></iframe>
    </div>

    <!-- Interaction Hint Bar -->
    <div
      class="activity-footer"
      :style="{
        backgroundColor: $themePalette.grey.v_100,
        borderTop: `1px solid ${$themeTokens.fineLine}`,
        color: $themeTokens.annotation,
      }"
    >
      <span class="footer-hint">
        ⌨️ 🖱️ Click inside to interact using keyboard and mouse
      </span>
    </div>
  </div>
</template>

<script>
  import { ref, computed } from 'vue';

  export default {
    name: 'Html5ActivityRunner',
    props: {
      htmlCode: {
        type: String,
        required: true,
      },
      title: {
        type: String,
        default: '',
      },
    },
    setup(props) {
      const reloadKey = ref(0);
      const isFullscreen = ref(false);
      const copied = ref(false);
      const iframeRef = ref(null);

      const processedSrcdoc = computed(() => {
        let code = (props.htmlCode || '').trim();
        const hasDoctype = /<!doctype\s+html/i.test(code) || /<html/i.test(code);
        if (!hasDoctype) {
          code = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 12px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
      background-color: #ffffff;
      line-height: 1.5;
    }
  </style>
</head>
<body>
  ${code}
</body>
</html>`;
        }
        return code;
      });

      function resetActivity() {
        reloadKey.value += 1;
      }

      function toggleFullscreen() {
        isFullscreen.value = !isFullscreen.value;
      }

      function copyCode() {
        if (!props.htmlCode) return;
        if (navigator.clipboard) {
          navigator.clipboard.writeText(props.htmlCode).then(() => {
            copied.value = true;
            setTimeout(() => {
              copied.value = false;
            }, 2000);
          });
        }
      }

      function downloadHtml() {
        if (!props.htmlCode) return;
        const blob = new Blob([processedSrcdoc.value], { type: 'text/html;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const safeTitle = (props.title || 'interactive-activity').toLowerCase().replace(/[^a-z0-9]+/g, '-');
        a.download = `${safeTitle}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }

      function focusIframe() {
        if (iframeRef.value && iframeRef.value.contentWindow) {
          try {
            iframeRef.value.contentWindow.focus();
          } catch (e) {
            // sandbox origin restriction
          }
        }
      }

      return {
        reloadKey,
        isFullscreen,
        copied,
        iframeRef,
        processedSrcdoc,
        resetActivity,
        toggleFullscreen,
        copyCode,
        downloadHtml,
        focusIframe,
      };
    },
  };
</script>

<style scoped>
  .html5-activity-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    margin: 16px 0;
    border-radius: 10px;
    border-width: 1.5px;
    border-style: solid;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.07);
    transition: all 0.2s ease;
  }

  .html5-activity-container.is-fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 99999;
    margin: 0;
    border-radius: 0;
    border: none;
  }

  .activity-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .activity-icon {
    font-size: 20px;
  }

  .activity-title {
    font-weight: 700;
    font-size: 14px;
  }

  .activity-tag {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 4px;
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
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 600;
    color: #334155;
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.15s ease, border-color 0.15s ease;
  }

  .action-btn:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
  }

  .iframe-wrapper {
    width: 100%;
    height: 480px;
    background-color: #ffffff;
    position: relative;
  }

  .is-fullscreen .iframe-wrapper {
    flex: 1;
    height: calc(100vh - 82px);
  }

  .activity-iframe {
    width: 100%;
    height: 100%;
    border: none;
    display: block;
  }

  .activity-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 14px;
    font-size: 12px;
  }

  .footer-hint {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
</style>
