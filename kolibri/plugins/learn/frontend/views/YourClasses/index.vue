<template>

  <section>
    <KFixedGrid :numCols="3">
      <KFixedGridItem :span="2">
        <h2 :style="{ marginTop: 0 }">
          <KLabeledIcon
            icon="classes"
            :label="$tr('yourClassesHeader')"
          />
        </h2>
      </KFixedGridItem>
      <KFixedGridItem
        :span="1"
        alignment="right"
      >
        <div class="classes-header-actions">
          <KRouterLink
            v-if="displayAllClassesLink"
            :text="coreString('viewAll')"
            :to="allClassesLink"
            data-testid="viewAllLink"
          />
          <SectionToggleButton
            :isExpanded="isExpanded"
            @click="toggleExpand"
          />
        </div>
      </KFixedGridItem>
    </KFixedGrid>

    <transition name="section-collapse">
      <div v-show="isExpanded">
        <CardGrid
          v-if="classes && classes.length > 0"
          :gridType="2"
        >
          <CardLink
            v-for="c in visibleClasses"
            :key="c.id"
            data-testid="classLink"
            :to="classAssignmentsLink(c.id)"
          >
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
              <h3
                dir="auto"
                :style="{ margin: 0, fontWeight: isClassLive(c.id) ? 'bold' : 'normal', color: isClassLive(c.id) ? '#15803d' : 'inherit' }"
              >
                {{ c.name }}
              </h3>
              <span
                v-if="isClassLive(c.id)"
                style="display: inline-flex; align-items: center; gap: 4px; font-size: 11px; font-weight: 800; color: #166534; background: #bbf7d0; padding: 2px 8px; border-radius: 9999px; text-transform: uppercase;"
              >
                <span style="width: 8px; height: 8px; border-radius: 50%; background: #22c55e; display: inline-block;"></span>
                LIVE
              </span>
            </div>
          </CardLink>
        </CardGrid>

        <KCircularLoader v-else-if="loading" />

        <p v-else-if="!loading">
          {{ $tr('noClasses') }}
        </p>
      </div>
    </transition>
  </section>

</template>


<script>

  import { onMounted, onBeforeUnmount } from 'vue';
  import { useTimeoutPoll } from '@vueuse/core';
  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';
  import useLiveSessions from 'kolibri-common/composables/useLiveSessions';
  import SectionToggleButton from 'kolibri-common/components/SectionToggleButton';
  import useCollapsible from 'kolibri-common/composables/useCollapsible';
  import { PageNames, ClassesPageNames } from '../../constants';
  import { classAssignmentsLink } from '../classes/classPageLinks';
  import CardGrid from '../cards/CardGrid';
  import CardLink from '../cards/CardLink';

  /**
   * Shows learner's classes.
   */
  export default {
    name: 'YourClasses',
    components: {
      CardGrid,
      CardLink,
      SectionToggleButton,
    },
    mixins: [commonCoreStrings],
    setup() {
      const { isExpanded, toggleExpand } = useCollapsible('learn_your_classes', true);
      const { fetchLiveSessions, isClassLive } = useLiveSessions();
      onMounted(() => {
        fetchLiveSessions();
      });
      const livePolling = useTimeoutPoll(fetchLiveSessions, 2000);
      onBeforeUnmount(livePolling.pause);
      return {
        isExpanded,
        toggleExpand,
        isClassLive,
      };
    },
    props: {
      classes: {
        type: Array,
        required: true,
      },
      /**
       * If there is more than four classes, only first four of them
       * and "View all" link will be displayed if `true`
       */
      short: {
        type: Boolean,
        required: false,
        default: false,
      },
      loading: {
        type: Boolean,
        default: null,
      },
    },
    data() {
      return {
        classAssignmentsLink,
      };
    },
    computed: {
      visibleClasses() {
        if (!this.classes) {
          return [];
        }
        if (this.short) {
          return this.classes.slice(0, 4);
        }
        return this.classes;
      },
      allClassesLink() {
        return { name: ClassesPageNames.ALL_CLASSES };
      },
      displayAllClassesLink() {
        return this.classes && this.classes.length > this.visibleClasses.length;
      },
    },
    $trs: {
      yourClassesHeader: {
        message: 'Your classes',
        context: 'Refers to the classes the learner is enrolled in.',
      },
      noClasses: {
        message: 'You are not enrolled in any classes',
        context:
          'Message that a learner sees in the Learn > CLASSES section and in the Learn > HOME section if they are not enrolled in any classes.',
      },
    },
  };

</script>


<style lang="scss" scoped>

  .classes-header-actions {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: flex-end;
  }

  .section-collapse-enter-active,
  .section-collapse-leave-active {
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
  }

  .section-collapse-enter,
  .section-collapse-enter-from,
  .section-collapse-leave-to {
    opacity: 0;
    transform: translateY(-8px);
  }

</style>
