<template>

  <section>
    <KFixedGrid :numCols="3">
      <KFixedGridItem :span="2">
        <h2 :style="{ marginTop: 0 }">
          <KLabeledIcon
            icon="channel"
            :label="$tr('header')"
          />
        </h2>
      </KFixedGridItem>
      <KFixedGridItem
        :span="1"
        alignment="right"
      >
        <div class="explore-header-actions">
          <KRouterLink
            v-if="displayAllChannelsLink"
            :text="coreString('viewAll')"
            :to="allChannelsLink"
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
        <CardGrid :gridType="1">
          <BaseChannelCard
            v-for="(channel, idx) in visibleChannels"
            :key="idx"
            data-testid="channelLink"
            :channel="channel"
            :to="getChannelLink(channel)"
          />
        </CardGrid>
      </div>
    </transition>
  </section>

</template>


<script>

  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';
  import SectionToggleButton from 'kolibri-common/components/SectionToggleButton';
  import useCollapsible from 'kolibri-common/composables/useCollapsible';
  import { PageNames } from '../../../constants';
  import CardGrid from '../../cards/CardGrid';
  import BaseChannelCard from '../../cards/BaseChannelCard';

  export default {
    name: 'ExploreChannels',
    components: {
      CardGrid,
      BaseChannelCard,
      SectionToggleButton,
    },
    mixins: [commonCoreStrings],
    setup() {
      const { isExpanded, toggleExpand } = useCollapsible('learn_explore_channels', true);
      return {
        isExpanded,
        toggleExpand,
      };
    },
    props: {
      channels: {
        type: Array,
        required: true,
      },
      /**
       * If there are more than four channels, only first four of them
       * and "View all" link will be displayed if `true`
       */
      short: {
        type: Boolean,
        required: false,
        default: false,
      },
    },
    computed: {
      visibleChannels() {
        if (!this.channels) {
          return [];
        }
        if (this.short) {
          return this.channels.slice(0, 3);
        }
        return this.channels;
      },
      displayAllChannelsLink() {
        return this.channels && this.channels.length > this.visibleChannels.length;
      },
      allChannelsLink() {
        return { name: PageNames.LIBRARY };
      },
    },
    methods: {
      getChannelLink(channel) {
        return {
          name: PageNames.TOPICS_TOPIC,
          params: {
            id: channel.root,
          },
          query: {
            last: PageNames.HOME,
          },
        };
      },
    },
    $trs: {
      header: {
        message: 'Explore channels',
        context: "Heading in the 'Learn' section where users can view channels.",
      },
    },
  };

</script>


<style lang="scss" scoped>

  .explore-header-actions {
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
