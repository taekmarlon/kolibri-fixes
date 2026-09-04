<template>

  <div>
    <transition name="delay-entry">
      <PostSetupModalGroup
        v-if="welcomeModalVisible && isLearner && !picturePasswordPending"
        isOnMyOwnUser
        @cancel="hideWelcomeModal"
      />
    </transition>
    <LearnAppBarPage
      :appBarTitle="learnString('learnLabel')"
      :loading="pageLoading"
    >
      <div
        v-if="!pageLoading"
        role="main"
      >
        <ResourceSyncingUiAlert
          v-if="missingResources"
          @syncComplete="hydrateHomePage"
        />
        <!-- Live Class in Session Alert Banner (When any enrolled class is live) -->
        <div
          v-if="activeLiveClass"
          class="home-live-class-alert"
          style="background: #f0fdf4; border: 2px solid #22c55e; border-radius: 12px; padding: 18px 24px; margin-top: 16px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; box-shadow: 0 4px 18px rgba(34, 197, 94, 0.22);"
        >
          <div style="display: flex; align-items: center; gap: 16px;">
            <div class="live-dot-wrapper">
              <span class="pulse-ring"></span>
              <span class="pulse-dot"></span>
            </div>
            <div>
              <div style="display: inline-block; font-size: 11px; font-weight: 800; color: #166534; background: #bbf7d0; padding: 2px 8px; border-radius: 9999px; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">
                🟢 LIVE IN SESSION NOW
              </div>
              <h2 style="margin: 0; font-size: 18px; font-weight: 800; color: #15803d;">
                {{ activeLiveClass.name }} is Live!
              </h2>
              <p style="margin: 4px 0 0; font-size: 14px; color: #166534;">
                Your teacher has started this class meeting. Join now to participate in live video, audio, and discussion.
              </p>
            </div>
          </div>
          <KButton
            text="Join Live Class Now ➔"
            :primary="true"
            appearance="raised-button"
            icon="openNewTab"
            style="background-color: #16a34a; color: #ffffff; font-weight: bold; font-size: 15px;"
            :to="{ name: ClassesPageNames.CLASS_LIVE_CLASS, params: { classId: activeLiveClass.id } }"
          />
        </div>
        <YourClasses
          v-if="displayClasses"
          class="section"
          :classes="classes"
          data-testid="classes"
          short
        />
        <ContinueLearning
          v-if="continueLearning"
          class="section"
          :fromClasses="continueLearningFromClasses"
          :data-testid="
            continueLearningFromClasses
              ? 'continueLearningFromClasses'
              : 'continueLearningOnYourOwn'
          "
        />
        <AssignedCoursesCards
          v-if="hasActiveClassesCourses"
          class="section"
          :courses="activeClassesCourses"
          displayClassName
          recent
          data-testid="recentCourses"
        />
        <AssignedLessonsCards
          v-if="hasActiveClassesLessons"
          class="section"
          :lessons="activeClassesLessons"
          displayClassName
          recent
          data-testid="recentLessons"
        />
        <AssignedQuizzesCards
          v-if="hasActiveClassesQuizzes"
          class="section"
          :quizzes="activeClassesQuizzes"
          displayClassName
          recent
          data-testid="recentQuizzes"
        />
        <ExploreChannels
          v-if="displayExploreChannels"
          :channels="channels"
          class="section"
          data-testid="exploreChannels"
          :short="
            Boolean(
              displayClasses ||
                hasActiveClassesCourses ||
                continueLearning ||
                hasActiveClassesLessons ||
                hasActiveClassesQuizzes,
            )
          "
        />
      </div>
    </LearnAppBarPage>
  </div>

</template>


<script>

  import { computed, onMounted, onBeforeUnmount, getCurrentInstance } from 'vue';
  import { get, set, useSessionStorage, useTimeoutPoll } from '@vueuse/core';
  import client from 'kolibri/client';
  import urls from 'kolibri/urls';
  import useUser from 'kolibri/composables/useUser';
  import { handleApiError } from 'kolibri/utils/appError';
  import useChannels from 'kolibri-common/composables/useChannels';
  import ContentNodeResource from 'kolibri-common/apiResources/ContentNodeResource';
  import { mapState } from 'vuex';
  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import { PICTURE_PASSWORD_ASSIGNED_MODAL_PENDING } from 'kolibri-common/constants/Auth';
  import ResourceSyncingUiAlert from '../ResourceSyncingUiAlert';
  import useDeviceSettings from '../../composables/useDeviceSettings';
  import useLearnerResources, {
    setClasses,
    setResumableContentNodes,
  } from '../../composables/useLearnerResources';
  import useLiveSessions from 'kolibri-common/composables/useLiveSessions';
  import { setContentNodeProgress } from '../../composables/useContentNodeProgress';
  import { inClasses } from '../../composables/useCoreLearn';
  import { PageNames, ClassesPageNames } from '../../constants';
  import AssignedCoursesCards from '../classes/AssignedCoursesCards';
  import AssignedLessonsCards from '../classes/AssignedLessonsCards';
  import AssignedQuizzesCards from '../classes/AssignedQuizzesCards';
  import YourClasses from '../YourClasses';
  import LearnAppBarPage from '../LearnAppBarPage';
  import PostSetupModalGroup from '../../../../device/frontend/views/PostSetupModalGroup.vue';
  import commonLearnStrings from '../commonLearnStrings';
  import ContinueLearning from './ContinueLearning';
  import ExploreChannels from './ExploreChannels';

  /**
   * Home page contains useful suggestions for a learner, such as their
   * resources and quizzes in progress, classes, resources to explore, etc.
   * What sections are displayed depends on whether a learner
   * is signed in and also if they're a member of classes.
   */
  const welcomeDismissalKey = 'DEVICE_WELCOME_MODAL_DISMISSED';
  export default {
    name: 'HomePage',
    components: {
      AssignedCoursesCards,
      AssignedLessonsCards,
      AssignedQuizzesCards,
      YourClasses,
      ContinueLearning,
      ExploreChannels,
      LearnAppBarPage,
      ResourceSyncingUiAlert,
      PostSetupModalGroup,
    },
    mixins: [commonLearnStrings],
    setup() {
      const currentInstance = getCurrentInstance().proxy;
      const store = currentInstance.$store;
      const router = currentInstance.$router;
      const { isUserLoggedIn, currentUserId, isLearner } = useUser();
      const picturePasswordPending = useSessionStorage(
        PICTURE_PASSWORD_ASSIGNED_MODAL_PENDING,
        false,
      );
      const { canAccessUnassignedContent } = useDeviceSettings();
      const { localChannelsCache, fetchChannels } = useChannels();
      const {
        classes,
        activeClassesCourses,
        activeClassesLessons,
        activeClassesQuizzes,
        resumableClassesQuizzes,
        resumableClassesResources,
        resumableContentNodes,
        learnerFinishedAllClasses,
      } = useLearnerResources();

      const { fetchLiveSessions, isClassLive } = useLiveSessions();

      onMounted(() => {
        fetchLiveSessions();
      });

      const liveSessionPolling = useTimeoutPoll(fetchLiveSessions, 10000);
      onBeforeUnmount(liveSessionPolling.pause);

      const activeLiveClass = computed(() => {
        const classList = get(classes) || [];
        return classList.find(c => isClassLive(c.id)) || null;
      });

      const continueLearningFromClasses = computed(
        () =>
          (get(isUserLoggedIn) && get(resumableClassesQuizzes).length > 0) ||
          get(resumableClassesResources).length > 0,
      );
      const continueLearningOnYourOwn = computed(
        () =>
          get(isUserLoggedIn) &&
          get(learnerFinishedAllClasses) &&
          get(canAccessUnassignedContent) &&
          get(resumableContentNodes).length > 0,
      );

      const continueLearning = computed(
        () => get(continueLearningFromClasses) || get(continueLearningOnYourOwn),
      );

      const hasActiveClassesCourses = computed(
        () =>
          get(isUserLoggedIn) && get(activeClassesCourses) && get(activeClassesCourses).length > 0,
      );
      const hasActiveClassesLessons = computed(
        () =>
          get(isUserLoggedIn) && get(activeClassesLessons) && get(activeClassesLessons).length > 0,
      );
      const hasActiveClassesQuizzes = computed(
        () =>
          get(isUserLoggedIn) && get(activeClassesQuizzes) && get(activeClassesQuizzes).length > 0,
      );
      const hasChannels = computed(() => {
        return get(localChannelsCache).length > 0;
      });
      const displayExploreChannels = computed(() => {
        return (
          get(hasChannels) &&
          (!get(isUserLoggedIn) ||
            (get(learnerFinishedAllClasses) && get(canAccessUnassignedContent)))
        );
      });

      const displayClasses = computed(() => {
        return get(isUserLoggedIn) && (get(classes).length || !get(canAccessUnassignedContent));
      });

      const missingResources = computed(() => {
        return (
          get(activeClassesLessons).some(l => l.missing_resource) ||
          get(activeClassesQuizzes).some(q => q.missing_resource)
        );
      });

      function hydrateHomePage() {
        return client({ url: urls['kolibri:kolibri.plugins.learn:homehydrate']() }).then(
          response => {
            setClasses(response.data.classrooms);
            // Update our hydrated class membership boolean in case it has changed
            // since the learn page was opened.
            set(inClasses, Boolean(response.data.classrooms.length));
            const resumableResults = response.data.resumable_resources.results || [];
            setResumableContentNodes(
              resumableResults,
              response.data.resumable_resources.more || null,
            );
            ContentNodeResource.cacheData(resumableResults);
            for (const progress of response.data.resumable_resources_progress) {
              setContentNodeProgress(progress);
            }
          },
        );
      }

      fetchChannels().then(channels => {
        if (!channels.length) {
          router.replace({ name: PageNames.LIBRARY });
          return;
        }

        // force fetch classes and resumable content nodes to make sure that the home
        // page is up-to-date when navigating to other 'Learn' pages and then back
        // to the home page
        return hydrateHomePage()
          .then(() => {
            store.commit('SET_PAGE_NAME', PageNames.HOME);
            pageLoading.value = false;
          })
          .catch(error => {
            pageLoading.value = false;
            handleApiError({ error, reloadOnReconnect: true });
          });
      });

      return {
        channels: localChannelsCache,
        classes,
        activeClassesCourses,
        activeClassesLessons,
        activeClassesQuizzes,
        hasActiveClassesCourses,
        hasActiveClassesLessons,
        hasActiveClassesQuizzes,
        continueLearningFromClasses,
        continueLearning,
        displayExploreChannels,
        displayClasses,
        missingResources,
        hydrateHomePage,
        pageLoading,
        picturePasswordPending,
        userId: currentUserId,
        isLearner,
        activeLiveClass,
        ClassesPageNames,
      };
    },
    computed: {
      ...mapState({
        welcomeModalVisibleState: 'welcomeModalVisible',
      }),
      welcomeModalVisible() {
        return (
          this.welcomeModalVisibleState &&
          window.localStorage.getItem(`${welcomeDismissalKey}-${this.userId}`) !== 'true'
        );
      },
    },
    created() {
      const welcomeDismissalKey = 'DEVICE_WELCOME_MODAL_DISMISSED';
      if (window.sessionStorage.getItem(`${welcomeDismissalKey}-${this.userId}`) !== 'true') {
        this.$store.commit('SET_WELCOME_MODAL_VISIBLE', true);
      }
    },
    methods: {
      hideWelcomeModal() {
        window.localStorage.setItem(`${welcomeDismissalKey}-${this.userId}`, true);
        this.$store.commit('SET_WELCOME_MODAL_VISIBLE', false);
      },
    },
  };

</script>


<style lang="scss" scoped>

  .section:not(:first-child) {
    margin-top: 32px;
  }

  .section:first-child {
    margin-top: 16px;
  }

  .live-dot-wrapper {
    position: relative;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .pulse-dot {
    width: 14px;
    height: 14px;
    background-color: #22c55e;
    border-radius: 50%;
    z-index: 2;
  }

  .pulse-ring {
    position: absolute;
    width: 28px;
    height: 28px;
    background-color: rgba(34, 197, 94, 0.45);
    border-radius: 50%;
    animation: pulse-ring-anim 1.8s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
  }

  @keyframes pulse-ring-anim {
    0% {
      transform: scale(0.6);
      opacity: 0.9;
    }
    70% {
      transform: scale(1.6);
      opacity: 0;
    }
    100% {
      transform: scale(1.6);
      opacity: 0;
    }
  }

</style>
