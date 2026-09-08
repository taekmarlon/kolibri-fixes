<template>

  <div
    class="phiedu-emoji-picker"
    :style="{
      backgroundColor: $themeTokens.surface,
      color: $themeTokens.text,
      borderColor: $themeTokens.fineLine,
    }"
  >
    <!-- Quick Reactions -->
    <div
      class="quick-reactions"
      :style="{ borderBottomColor: $themeTokens.fineLine }"
    >
      <button
        v-for="emoji in quickEmojis"
        :key="emoji"
        type="button"
        class="emoji-btn quick-emoji"
        @click="$emit('select', emoji)"
      >
        {{ emoji }}
      </button>
    </div>

    <!-- Category Tabs -->
    <div
      class="category-tabs"
      :style="{ borderBottomColor: $themeTokens.fineLine }"
    >
      <button
        v-for="(cat, idx) in categories"
        :key="cat.name"
        type="button"
        class="cat-tab"
        :class="{ active: activeCategoryIndex === idx }"
        :style="activeCategoryIndex === idx ? { borderBottomColor: $themeTokens.primary } : {}"
        @click="activeCategoryIndex = idx"
      >
        {{ cat.icon }}
      </button>
    </div>

    <!-- Emoji Grid -->
    <div class="emoji-grid-wrapper">
      <div class="emoji-grid">
        <button
          v-for="emoji in currentCategoryEmojis"
          :key="emoji"
          type="button"
          class="emoji-btn grid-emoji"
          @click="$emit('select', emoji)"
        >
          {{ emoji }}
        </button>
      </div>
    </div>
  </div>

</template>


<script>

  import { ref, computed } from 'vue';

  const QUICK_EMOJIS = ['👍', '❤️', '😂', '😮', '😢', '🙏', '🔥', '🎉'];

  const CATEGORIES = [
    {
      name: 'Smileys',
      icon: '😀',
      emojis: [
        '😀',
        '😃',
        '😄',
        '😁',
        '😆',
        '😅',
        '🤣',
        '😂',
        '🙂',
        '🙃',
        '😉',
        '😊',
        '😇',
        '🥰',
        '😍',
        '🤩',
        '😘',
        '😗',
        '😚',
        '😋',
        '😛',
        '😜',
        '🤪',
        '😝',
        '🤗',
        '🤭',
        '🤫',
        '🤔',
        '🤐',
        '🤨',
        '😐',
        '😑',
        '😶',
        '😏',
        '😒',
        '🙄',
        '😬',
        '😮‍💨',
        '🤥',
        '😌',
        '😔',
        '😪',
        '🤤',
        '😴',
        '😷',
        '🤒',
        '🤕',
        '🤢',
        '🤮',
        '🤧',
        '🥵',
        '🥶',
        '🥴',
        '😵',
        '🤯',
        '🤠',
        '🥳',
        '🥸',
        '😎',
        '🤓',
        '🧐',
        '😕',
        '😟',
        '🙁',
        '😮',
        '😯',
        '😲',
        '😳',
        '🥺',
        '😦',
        '😧',
        '😨',
        '😰',
        '😥',
        '😢',
        '😭',
        '😱',
        '😖',
        '😣',
        '😞',
        '😓',
        '😩',
        '😫',
        '🥱',
        '😤',
        '😡',
        '😠',
        '🤬',
      ],
    },
    {
      name: 'Gestures',
      icon: '👍',
      emojis: [
        '👍',
        '👎',
        '👌',
        '🤌',
        '🤏',
        '✌️',
        '🤞',
        '🫰',
        '🤟',
        '🤘',
        '🤙',
        '👈',
        '👉',
        '👆',
        '🖕',
        '👇',
        '☝️',
        '✋',
        '🤚',
        '🖐️',
        '🖖',
        '👋',
        '🤙',
        '🫱',
        '👏',
        '🙌',
        '👐',
        '🤲',
        '🤝',
        '🙏',
        '✍️',
        '💅',
        '💪',
        '🦾',
        '🦿',
        '🦵',
        '🦶',
        '👂',
        '🦻',
        '👃',
        '🧠',
        '🫀',
        '🫁',
        '🦷',
        '🦴',
        '👀',
        '👁️',
        '👅',
      ],
    },
    {
      name: 'Hearts & Sparks',
      icon: '❤️',
      emojis: [
        '❤️',
        '🧡',
        '💛',
        '💚',
        '💙',
        '💜',
        '🤎',
        '🖤',
        '🤍',
        '💔',
        '❤️‍🔥',
        '❤️‍🩹',
        '❣️',
        '💕',
        '💞',
        '💓',
        '💗',
        '💖',
        '💘',
        '💝',
        '💟',
        '✨',
        '⭐',
        '🌟',
        '💫',
        '🔥',
        '💥',
        '💯',
        '💢',
        '💬',
        '💭',
        '🗯️',
      ],
    },
    {
      name: 'Activities & School',
      icon: '📚',
      emojis: [
        '📚',
        '📖',
        '✏️',
        '📝',
        '🖍️',
        '🖊️',
        '🖋️',
        '📐',
        '📏',
        '🎒',
        '🎓',
        '🏫',
        '🔬',
        '🔭',
        '🧪',
        '🧬',
        '💡',
        '🏆',
        '🥇',
        '🥈',
        '🥉',
        '🏅',
        '🎯',
        '🎨',
        '⚽',
        '🏀',
        '🏈',
        '⚾',
        '🎾',
        '🏐',
        '🏉',
        '🥏',
      ],
    },
  ];

  export default {
    name: 'ChatEmojiPicker',
    emits: ['select'],
    setup() {
      const activeCategoryIndex = ref(0);

      const currentCategoryEmojis = computed(() => {
        return CATEGORIES[activeCategoryIndex.value]?.emojis || [];
      });

      return {
        quickEmojis: QUICK_EMOJIS,
        categories: CATEGORIES,
        activeCategoryIndex,
        currentCategoryEmojis,
      };
    },
  };

</script>


<style scoped>

  .phiedu-emoji-picker {
    z-index: 10005;
    display: flex;
    flex-direction: column;
    width: 280px;
    height: 260px;
    overflow: hidden;
    user-select: none;
    border: 1px solid;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
  }

  .quick-reactions {
    display: flex;
    justify-content: space-around;
    padding: 6px 4px;
    background-color: rgba(0, 0, 0, 0.02);
    border-bottom: 1px solid;
  }

  .category-tabs {
    display: flex;
    padding: 0 4px;
    border-bottom: 1px solid;
  }

  .cat-tab {
    flex: 1;
    padding: 6px 0;
    font-size: 16px;
    cursor: pointer;
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    transition: background-color 0.15s;
  }

  .cat-tab:hover {
    background-color: rgba(0, 0, 0, 0.04);
  }

  .emoji-grid-wrapper {
    flex: 1;
    padding: 6px;
    overflow-y: auto;
  }

  .emoji-grid {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 4px;
  }

  .emoji-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 4px;
    font-size: 18px;
    cursor: pointer;
    background: transparent;
    border: 0;
    border-radius: 6px;
    transition:
      transform 0.1s,
      background-color 0.15s;
  }

  .emoji-btn:hover {
    background-color: rgba(0, 0, 0, 0.08);
    transform: scale(1.18);
  }

  .quick-emoji {
    font-size: 20px;
  }

</style>
