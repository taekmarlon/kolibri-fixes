<template>

  <LearnAppBarPage
    :appBarTitle="learnString('learnLabel')"
    :loading="pageLoading"
  >
    <KCircularLoader v-if="pageLoading" />
    <div
      v-else
      role="main"
    >
      <KBreadcrumbs
        :items="breadcrumbs"
        :ariaLabel="learnString('classesAndAssignmentsLabel')"
      />
      <h1 class="classroom-name">
        <KLabeledIcon
          icon="classes"
          :label="className"
        />
      </h1>

      <!-- Live Classroom Banner -->
      <div
        class="live-class-card"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
        }"
      >
        <div class="live-card-left">
          <KIcon icon="group" class="live-card-icon" :style="{ color: $themeTokens.primary }" />
          <div>
            <h2 class="live-card-title" :style="{ color: $themeTokens.text }">
              {{ $tr('liveClassTitle') }}
            </h2>
            <p class="live-card-desc" :style="{ color: $themeTokens.annotation }">
              {{ $tr('liveClassSubtext') }}
            </p>
          </div>
        </div>
        <KButton
          :text="$tr('joinLiveClassButton')"
          :primary="true"
          appearance="raised-button"
          icon="group"
          :to="{ name: ClassesPageNames.CLASS_LIVE_CLASS, params: { classId } }"
        />
      </div>

      <!-- AI Tutor Study Assistant Banner (When enabled) -->
      <div
        v-if="isAiEnabled"
        class="live-class-card ai-tutor-banner"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
        }"
      >
        <div class="live-card-left">
          <KIcon icon="practice" class="live-card-icon" :style="{ color: $themeTokens.primary }" />
          <div>
            <h2 class="live-card-title" :style="{ color: $themeTokens.text }">
              {{ $tr('aiTutorCardTitle') }}
            </h2>
            <p class="live-card-desc" :style="{ color: $themeTokens.annotation }">
              {{ $tr('aiTutorCardDesc') }}
            </p>
          </div>
        </div>
        <KButton
          :text="$tr('askAiTutorButton')"
          :primary="false"
          appearance="raised-button"
          icon="practice"
          :to="{ name: PageNames.AI_TUTOR }"
        />
      </div>

      <AssignedCoursesCards :courses="activeCourses" />
      <AssignedLessonsCards
        :lessons="activeLessons"
        :style="{ marginTop: '44px' }"
      />
      <AssignedQuizzesCards
        :quizzes="activeQuizzes"
        :style="{ marginTop: '44px' }"
      />
    </div>
  </LearnAppBarPage>

</template>


<script>

  import { computed, onBeforeUnmount } from 'vue';
  import { useTimeoutPoll } from '@vueuse/core';
  import KBreadcrumbs from 'kolibri-design-system/lib/KBreadcrumbs';
  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';

  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import { PageNames, ClassesPageNames } from '../../constants';

  import useLearnerResources from '../../composables/useLearnerResources';
  import useAiTutor from 'kolibri-common/composables/useAiTutor';
  import commonLearnStrings from '../commonLearnStrings';
  import LearnAppBarPage from '../LearnAppBarPage';
  import AssignedCoursesCards from './AssignedCoursesCards';
  import AssignedQuizzesCards from './AssignedQuizzesCards';
  import AssignedLessonsCards from './AssignedLessonsCards';

  export default {
    name: 'ClassAssignmentsPage',
    metaInfo() {
      return {
        title: this.$tr('documentTitle'),
      };
    },
    components: {
      AssignedCoursesCards,
      AssignedQuizzesCards,
      AssignedLessonsCards,
      KBreadcrumbs,
      LearnAppBarPage,
    },
    mixins: [commonCoreStrings, commonLearnStrings],
    setup(props) {
      const {
        fetchClass,
        getClass,
        getClassActiveCourses,
        getClassActiveLessons,
        getClassActiveQuizzes,
      } = useLearnerResources();

      const { isAiEnabled } = useAiTutor();

      const className = computed(() => {
        return (getClass(props.classId) || {}).name;
      });

      const activeCourses = computed(() => {
        return getClassActiveCourses(props.classId);
      });

      const activeLessons = computed(() => {
        return getClassActiveLessons(props.classId);
      });

      const activeQuizzes = computed(() => {
        return getClassActiveQuizzes(props.classId);
      });

      const polling = useTimeoutPoll(
        () => fetchClass(props.classId),
        30000, // poll every 30 seconds
      );

      onBeforeUnmount(polling.pause);

      return {
        className,
        activeCourses,
        activeLessons,
        activeQuizzes,
        pageLoading,
        ClassesPageNames,
        PageNames,
        isAiEnabled,
      };
    },
    props: {
      classId: {
        type: String,
        required: true,
      },
    },
    computed: {
      breadcrumbs() {
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
            text: this.className,
            link: { name: ClassesPageNames.CLASS_ASSIGNMENTS },
          },
        ];
      },
    },
    $trs: {
      documentTitle: {
        message: 'Class assignments',
        context:
          'Page/tab title displayed for the Learn page when the learner is enrolled in a class. This is where the learners can see the list of lessons and quizzes coaches have opened and made available for them.',
      },
      liveClassTitle: {
        message: 'Live Virtual Classroom',
        context: 'Title for live classroom card on learner class assignments page',
      },
      liveClassSubtext: {
        message: 'Join live video sessions and discussions hosted by your teacher.',
        context: 'Description for live classroom card',
      },
      joinLiveClassButton: {
        message: 'Join Live Class',
        context: 'Button to join the live virtual meeting',
      },
      aiTutorCardTitle: {
        message: 'AI Personal Study Assistant',
        context: 'Title for AI tutor card on learner class assignments page',
      },
      aiTutorCardDesc: {
        message: 'Ask questions, get step-by-step math solutions, and understand tricky concepts anytime.',
        context: 'Description for AI tutor card',
      },
      askAiTutorButton: {
        message: 'Ask AI Tutor',
        context: 'Button to open AI tutor chat',
      },
    },
  };

</script>


<style lang="scss" scoped>

  .classroom-name {
    margin-bottom: 24px;
  }

  .live-class-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 24px;
    border-radius: 8px;
    margin-bottom: 36px;
    gap: 16px;
    flex-wrap: wrap;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  }

  .live-card-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .live-card-icon {
    font-size: 32px;
  }

  .live-card-title {
    margin: 0 0 4px 0;
    font-size: 1.15rem;
    font-weight: bold;
  }

  .live-card-desc {
    margin: 0;
    font-size: 0.9rem;
  }

</style>
