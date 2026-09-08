<template>

  <div class="container">
    <div class="rel">
      <div
        class="phiedu-book-loader"
        role="img"
        :aria-label="$tr('kolibriLoading')"
      >
        <div class="phiedu-book">
          <div
            class="phiedu-book-cover left"
            :style="{ backgroundColor: $themeTokens.primary }"
          ></div>
          <div class="phiedu-book-base-page left"></div>
          <div class="phiedu-book-spine"></div>
          <div class="phiedu-page phiedu-page-1"></div>
          <div class="phiedu-page phiedu-page-2"></div>
          <div class="phiedu-page phiedu-page-3"></div>
          <div class="phiedu-book-base-page right"></div>
          <div
            class="phiedu-book-cover right"
            :style="{ backgroundColor: $themeTokens.primary }"
          ></div>
        </div>
        <div
          class="phiedu-loader-brand"
          :style="{ color: $themeTokens.primary }"
        >
          <span>PHIEDU</span>
          <span class="phiedu-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
      </div>
    </div>
  </div>

</template>


<script>

  export default {
    name: 'KolibriLoadingSnippet',
    $trs: {
      kolibriLoading: {
        message: 'PHIEDU loading',
        context: 'Indicates PHIEDU is loading',
      },
    },
  };

</script>


<style scoped>

  .container {
    width: 100%;
    height: 100%;
  }

  .rel {
    position: relative;
    width: 100%;
    height: 100%;
  }

  .phiedu-book-loader {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 220px;
    margin: 0 auto;
    animation: fadeIn 0.8s ease-in both;
    user-select: none;
  }

  .phiedu-book {
    position: relative;
    width: 108px;
    height: 76px;
    margin-bottom: 16px;
    perspective: 800px;
  }

  .phiedu-book-cover {
    position: absolute;
    top: 0;
    width: 52px;
    height: 76px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .phiedu-book-cover.left {
    left: 0;
    border-radius: 5px 0 0 5px;
    transform-origin: right center;
  }

  .phiedu-book-cover.right {
    right: 0;
    border-radius: 0 5px 5px 0;
    transform-origin: left center;
  }

  .phiedu-book-spine {
    position: absolute;
    top: -1px;
    left: 52px;
    z-index: 10;
    width: 4px;
    height: 78px;
    background: #0f172a;
    border-radius: 2px;
  }

  .phiedu-book-base-page {
    position: absolute;
    top: 4px;
    z-index: 2;
    width: 48px;
    height: 68px;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
  }

  .phiedu-book-base-page.left {
    left: 3px;
    border-right: none;
    border-radius: 3px 0 0 3px;
  }

  .phiedu-book-base-page.right {
    right: 3px;
    border-left: none;
    border-radius: 0 3px 3px 0;
  }

  .phiedu-page {
    position: absolute;
    top: 4px;
    left: 54px;
    z-index: 5;
    width: 48px;
    height: 68px;
    background: #ffffff;
    border: 1px solid #bfdbfe;
    border-left: none;
    border-radius: 0 3px 3px 0;
    animation: phieduPageFlip 1.8s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
    transform-origin: 0% 50%;
    transform-style: preserve-3d;
    backface-visibility: visible;
  }

  .phiedu-page-1 {
    animation-delay: 0.15s;
  }

  .phiedu-page-2 {
    animation-delay: 0.45s;
  }

  .phiedu-page-3 {
    animation-delay: 0.75s;
  }

  @keyframes phieduPageFlip {
    0% {
      background: #ffffff;
      opacity: 1;
      transform: rotateY(0deg);
    }
    45% {
      background: #f1f5f9;
      opacity: 1;
    }
    90% {
      background: #ffffff;
      opacity: 0.85;
      transform: rotateY(-180deg);
    }
    100% {
      opacity: 0;
      transform: rotateY(-180deg);
    }
  }

  .phiedu-loader-brand {
    display: flex;
    gap: 4px;
    align-items: baseline;
    justify-content: center;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 2px;
  }

  .phiedu-dots span {
    display: inline-block;
    animation: phieduBlink 1.4s infinite both;
  }

  .phiedu-dots span:nth-child(1) {
    animation-delay: 0.2s;
  }

  .phiedu-dots span:nth-child(2) {
    animation-delay: 0.4s;
  }

  .phiedu-dots span:nth-child(3) {
    animation-delay: 0.6s;
  }

  @keyframes phieduBlink {
    0%,
    80%,
    100% {
      opacity: 0.2;
      transform: scale(0.8);
    }
    40% {
      opacity: 1;
      transform: scale(1.2);
    }
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

</style>
