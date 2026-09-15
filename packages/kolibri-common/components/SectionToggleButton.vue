<template>
  <button
    type="button"
    class="section-toggle-btn"
    :class="{ 'is-collapsed': !isExpanded }"
    :style="{
      backgroundColor: $themePalette.grey.v_200,
      borderColor: $themeTokens.fineLine,
      color: $themeTokens.text,
    }"
    :aria-expanded="isExpanded"
    :title="isExpanded ? collapseTooltip : expandTooltip"
    :aria-label="isExpanded ? collapseTooltip : expandTooltip"
    @click.stop="$emit('click')"
  >
    <KIcon
      :icon="isExpanded ? 'chevronUp' : 'chevronDown'"
      class="toggle-icon"
    />
  </button>
</template>

<script>
  export default {
    name: 'SectionToggleButton',
    props: {
      isExpanded: {
        type: Boolean,
        default: true,
      },
      collapseTooltip: {
        type: String,
        default: 'Collapse section',
      },
      expandTooltip: {
        type: String,
        default: 'Expand section',
      },
    },
    emits: ['click'],
  };
</script>

<style lang="scss" scoped>
  .section-toggle-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    border: 1px solid rgba(0, 0, 0, 0.12);
    cursor: pointer;
    padding: 0;
    margin-left: 8px;
    vertical-align: middle;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);

    &:hover {
      filter: brightness(0.92);
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    &:active {
      transform: translateY(0);
      box-shadow: none;
    }

    &:focus-visible {
      outline: 2px solid #2563eb;
      outline-offset: 2px;
    }
  }

  .toggle-icon {
    width: 18px;
    height: 18px;
  }
</style>
