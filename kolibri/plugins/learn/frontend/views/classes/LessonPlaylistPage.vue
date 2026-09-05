<template>

  <LearnAppBarPage
    :appBarTitle="learnString('learnLabel')"
    :loading="pageLoading"
  >
    <div
      v-if="!pageLoading"
      role="main"
    >
      <KBreadcrumbs
        :items="breadcrumbs"
        :ariaLabel="learnString('classesAndAssignmentsLabel')"
      />
      <section class="lesson-details">
        <div>
          <ContentIcon
            kind="lesson"
            class="lesson-icon"
          />
          <h1
            dir="auto"
            class="title"
          >
            {{ currentLesson.title }}
            <ProgressIcon
              v-if="lessonHasResources"
              class="progress-icon"
              :progress="lessonProgress"
            />
          </h1>
        </div>
        <div v-if="currentLesson.description !== ''">
          <h3>{{ $tr('teacherNote') }}</h3>
          <p dir="auto">
            {{ currentLesson.description }}
          </p>
        </div>
        <ResourceSyncingUiAlert v-if="hasMissingResources" />
      </section>

      <section
        v-if="lessonHasResources"
        class="content-cards"
      >
        <HybridLearningLessonCard
          v-for="content in contentNodes"
          :key="content.id"
          :content="content"
          class="content-card"
          :isMobile="windowIsSmall"
          :link="content.is_custom ? customResourceLink(content) : genContentLinkBackLinkCurrentPage(content.id, true)"
        />
      </section>
      <p
        v-else
        class="no-resources-message"
      >
        {{ $tr('noResourcesInLesson') }}
      </p>
    </div>
    <KCircularLoader v-else />
  </LearnAppBarPage>

</template>


<script>

  import { mapMutations, mapState } from 'vuex';
  import KBreadcrumbs from 'kolibri-design-system/lib/KBreadcrumbs';
  import useKResponsiveWindow from 'kolibri-design-system/lib/composables/useKResponsiveWindow';
  import ProgressIcon from 'kolibri-common/components/labels/ProgressIcon';
  import ContentIcon from 'kolibri-common/components/labels/ContentIcon';
  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';
  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import ResourceSyncingUiAlert from '../ResourceSyncingUiAlert';
  import useContentLink from '../../composables/useContentLink';
  import useContentNodeProgress from '../../composables/useContentNodeProgress';
  import { PageNames, ClassesPageNames } from '../../constants';
  import commonLearnStrings from '../commonLearnStrings';
  import LearnAppBarPage from '../LearnAppBarPage';
  import HybridLearningLessonCard from '../HybridLearningLessonCard';
  import { LearningActivities } from 'kolibri/constants';

  export default {
    name: 'LessonPlaylistPage',
    metaInfo() {
      return {
        title: this.currentLesson.title,
      };
    },
    components: {
      KBreadcrumbs,
      HybridLearningLessonCard,
      ContentIcon,
      ProgressIcon,
      LearnAppBarPage,
      ResourceSyncingUiAlert,
    },
    mixins: [commonCoreStrings, commonLearnStrings],
    setup() {
      const { genContentLinkBackLinkCurrentPage } = useContentLink();
      const { contentNodeProgressMap } = useContentNodeProgress();
      const { windowIsSmall } = useKResponsiveWindow();
      return {
        contentNodeProgressMap,
        genContentLinkBackLinkCurrentPage,
        pageLoading,
        windowIsSmall,
      };
    },
    computed: {
      ...mapState('lessonPlaylist', ['contentNodesMap', 'currentLesson']),
      hasMissingResources() {
        if (this.currentLesson && this.currentLesson.missing_resource) {
          return true;
        }
        const nonCustomResources = this.lessonResources.filter(r => !r.is_custom);
        const nonCustomNodes = this.contentNodes.filter(n => !n.is_custom);
        return nonCustomResources.length > nonCustomNodes.length;
      },
      contentNodes() {
        return this.lessonResources
          .map(r => {
            if (this.contentNodesMap && this.contentNodesMap[r.contentnode_id]) {
              return this.contentNodesMap[r.contentnode_id];
            }
            if (r.contentnode) {
              return r.contentnode;
            }
            if (r.is_custom) {
              const kind =
                r.resource_type === 'youtube'
                  ? 'video'
                  : r.resource_type === 'image'
                  ? 'image'
                  : r.resource_type === 'html5'
                  ? 'html5'
                  : 'document';
              return {
                id: r.contentnode_id,
                content_id: r.content_id,
                title: r.title || 'Custom Resource',
                description: r.description || '',
                kind,
                is_custom: true,
                is_leaf: true,
                num_coach_contents: 0,
                thumbnail: r.thumbnail || (r.resource_type === 'image' ? r.file_url : null),
                learning_activities: [
                  kind === 'video'
                    ? LearningActivities.WATCH
                    : kind === 'html5'
                    ? LearningActivities.EXPLORE
                    : LearningActivities.READ,
                ],
                resource_type: r.resource_type,
                url: r.url,
                file_url: r.file_url,
                file_name: r.file_name,
                file_size: r.file_size,
                content: r.content,
              };
            }
            return null;
          })
          .filter(Boolean);
      },
      lessonResources() {
        return (this.currentLesson && this.currentLesson.resources) || [];
      },
      lessonHasResources() {
        return this.lessonResources.length > 0;
      },
      lessonHasResourcesAvailable() {
        return this.contentNodes.length > 0;
      },
      lessonProgress() {
        if (this.lessonHasResourcesAvailable) {
          // HACK: Infer the Learner's progress by summing the progress_fractions
          // on all the ContentNodes
          const total = Object.values(this.contentNodesMap).reduce(
            (tot, node) => tot + (this.contentNodeProgressMap[node.content_id] || 0),
            0,
          );
          if (total === 0) {
            return null;
          }
          return total / this.contentNodes.length;
        }

        return undefined;
      },
      breadcrumbs() {
        const classroom = this.currentLesson && this.currentLesson.classroom;
        const classId = (classroom && classroom.id) || this.$route.params.classId;
        const classroomName = (classroom && classroom.name) || 'Class';
        return [
          {
            text: this.coreString('homeLabel'),
            link: { name: PageNames.HOME },
          },
          {
            text: this.coreString('classesLabel'),
            link: { name: ClassesPageNames.ALL_CLASSES },
          },
          {
            text: classroomName,
            link: {
              name: ClassesPageNames.CLASS_ASSIGNMENTS,
              params: { classId },
            },
          },
          {
            text: (this.currentLesson && this.currentLesson.title) || 'Lesson',
          },
        ];
      },
      customResourceLink() {
        return content => ({
          name: ClassesPageNames.LESSON_CUSTOM_RESOURCE,
          params: {
            classId:
              (this.currentLesson &&
                this.currentLesson.classroom &&
                this.currentLesson.classroom.id) ||
              this.$route.params.classId,
            lessonId:
              (this.currentLesson && this.currentLesson.id) || this.$route.params.lessonId,
            resourceId: content.id,
          },
        });
      },
    },
    beforeDestroy() {
      /* If we are going anywhere except for content we unset the lesson */

      if (this.$route.name !== PageNames.TOPICS_CONTENT) {
        this.SET_CURRENT_LESSON({});
      }
    },
    methods: {
      ...mapMutations('lessonPlaylist', ['SET_CURRENT_LESSON']),
    },
    $trs: {
      noResourcesInLesson: {
        message: 'There are no resources in this lesson',
        context:
          "This text displays in the learner's 'Lessons' section if the coach has not added any resources to the lesson.",
      },
      teacherNote: {
        message: 'Coach note',
        context:
          'Label for the field where the coach can add notes for their learners regarding the resource.',
      },
    },
  };

</script>


<style lang="scss" scoped>

  .lesson-details {
    margin-bottom: 32px;
  }

  .title {
    display: inline-block;
  }

  .content-cards {
    max-width: 100%;
  }

  .content-card {
    margin-bottom: 16px;
  }

  .no-resources-message {
    padding: 48px 0;
    font-weight: bold;
    text-align: center;
  }

  .lesson-icon {
    display: inline-block;
    margin-right: 0.5em;
    font-size: 1.8em;

    ::v-deep .ui-icon {
      margin-bottom: 12px;
      vertical-align: middle;
    }
  }

  .progress-icon {
    display: inline-block;
    margin-right: 0.5em;
    font-size: 1.8em;

    ::v-deep .ui-icon {
      margin-top: 4px;
      vertical-align: middle;
    }
  }

</style>
