<template>

  <KPageContainer class="block">
    <KGrid>
      <KGridItem
        :layout8="{ span: showAllLink ? 5 : 7 }"
        :layout12="{ span: showAllLink ? 8 : 10 }"
      >
        <h2>
          <slot name="title"></slot>
        </h2>
      </KGridItem>
      <KGridItem
        :layout="{ alignment: 'right' }"
        :layout8="{ span: showAllLink ? 3 : 1 }"
        :layout12="{ span: showAllLink ? 4 : 2 }"
      >
        <div class="block-header-actions">
          <KRouterLink
            v-if="showAllLink"
            appearance="flat-button"
            :text="allLinkText"
            :to="allLinkRoute"
            class="btn"
          />
          <SectionToggleButton
            :isExpanded="isExpanded"
            @click="toggleExpand"
          />
        </div>
      </KGridItem>
    </KGrid>
    <transition name="section-collapse">
      <div v-show="isExpanded" class="block-body">
        <slot></slot>
      </div>
    </transition>
  </KPageContainer>

</template>


<script>

  import SectionToggleButton from 'kolibri-common/components/SectionToggleButton';
  import useCollapsible from 'kolibri-common/composables/useCollapsible';
  import commonCoach from '../../common';

  export default {
    name: 'Block',
    components: {
      SectionToggleButton,
    },
    mixins: [commonCoach],
    props: {
      allLinkText: {
        type: String,
        required: true,
      },
      allLinkRoute: {
        type: Object,
        required: true,
      },
      showAllLink: {
        type: Boolean,
        default: true,
      },
      storageKey: {
        type: String,
        default: null,
      },
    },
    setup(props) {
      const key =
        props.storageKey ||
        (props.allLinkText
          ? `coach_block_${props.allLinkText.toLowerCase().replace(/[^a-z0-9]/g, '_')}`
          : null);
      const { isExpanded, toggleExpand } = useCollapsible(key, true);

      return {
        isExpanded,
        toggleExpand,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .block {
    margin-top: 16px;
  }

  .block-header-actions {
    display: inline-flex;
    align-items: center;
    justify-content: flex-end;
  }

  .btn {
    position: relative;
    top: 4px;
    right: -8px;
    // Override inline-table rule to get focus outline to show.
    // May not be safe to do everywhere, since it could cause
    // vertical alignment issues like in #5606
    display: inline-block !important;
  }

  .section-collapse-enter-active,
  .section-collapse-leave-active {
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
  }

  .section-collapse-enter-from,
  .section-collapse-leave-to {
    opacity: 0;
    transform: translateY(-8px);
  }

</style>
