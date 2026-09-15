<template>

  <span
    class="user-avatar"
    :style="avatarContainerStyle"
  >
    <img
      v-if="hasValidImage"
      :src="imgSrc"
      :alt="altText"
      class="user-avatar-img"
      :style="avatarSizeStyle"
      @error="handleImageError"
    >
    <span
      v-else
      class="user-avatar-fallback"
      :style="fallbackStyle"
      aria-hidden="true"
    >
      <KIcon
        :icon="icon"
        :style="iconStyle"
      />
    </span>
  </span>

</template>


<script>

  import { computed, ref, watch } from 'vue';
  import { themeTokens } from 'kolibri-design-system/lib/styles/theme';

  export default {
    name: 'UserAvatar',
    props: {
      user: {
        type: Object,
        default: null,
      },
      picture: {
        type: String,
        default: null,
      },
      name: {
        type: String,
        default: '',
      },
      size: {
        type: Number,
        default: 24,
      },
      icon: {
        type: String,
        default: 'person',
      },
    },
    setup(props) {
      const imageError = ref(false);

      const imgSrc = computed(() => {
        return props.picture || props.user?.picture || null;
      });

      watch(imgSrc, () => {
        imageError.value = false;
      });

      const hasValidImage = computed(() => {
        return Boolean(imgSrc.value) && !imageError.value;
      });

      const altText = computed(() => {
        return props.name || props.user?.full_name || props.user?.username || '';
      });

      const avatarContainerStyle = computed(() => {
        const px = `${props.size}px`;
        return {
          width: px,
          height: px,
          minWidth: px,
          maxWidth: px,
        };
      });

      const avatarSizeStyle = computed(() => {
        const px = `${props.size}px`;
        return {
          width: px,
          height: px,
        };
      });

      const fallbackStyle = computed(() => {
        const $themeTokens = themeTokens();
        const px = `${props.size}px`;
        return {
          width: px,
          height: px,
          backgroundColor: $themeTokens.fineLine,
        };
      });

      const iconStyle = computed(() => {
        const $themeTokens = themeTokens();
        const iconSize = Math.max(14, Math.round(props.size * 0.7));
        return {
          fill: $themeTokens.annotation,
          width: `${iconSize}px`,
          height: `${iconSize}px`,
        };
      });

      function handleImageError() {
        imageError.value = true;
      }

      return {
        imgSrc,
        hasValidImage,
        altText,
        avatarContainerStyle,
        avatarSizeStyle,
        fallbackStyle,
        iconStyle,
        handleImageError,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .user-avatar {
    position: relative;
    display: inline-flex;
    flex-shrink: 0;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    vertical-align: middle;
    border-radius: 50%;
  }

  .user-avatar-img {
    display: block;
    object-fit: cover;
    border-radius: 50%;
  }

  .user-avatar-fallback {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }

</style>
