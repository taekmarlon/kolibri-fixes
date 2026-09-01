<template>

  <LearnAppBarPage
    :appBarTitle="learnString('learnLabel')"
    :loading="pageLoading"
  >
    <KCircularLoader v-if="pageLoading" />
    <div v-else role="main" class="learner-live-page">
      <KBreadcrumbs
        :items="breadcrumbs"
        :ariaLabel="learnString('classesAndAssignmentsLabel')"
      />

      <!-- Active Meeting View -->
      <div v-if="meetingActive" class="active-meeting-wrapper">
        <LiveMeeting
          :roomName="classRoomName"
          :meetingTitle="pageTitle"
          @leave="leaveMeeting"
        />
      </div>

      <!-- Pre-Join Lobby -->
      <div v-else class="lobby-card" :style="{ backgroundColor: $themeTokens.surface, border: `1px solid ${$themeTokens.fineLine}` }">
        <div class="lobby-header">
          <KIcon icon="group" class="header-icon" :style="{ color: $themeTokens.primary }" />
          <div>
            <h1 class="class-title" :style="{ color: $themeTokens.text }">
              {{ pageTitle }}
            </h1>
            <p class="class-subtitle" :style="{ color: $themeTokens.annotation }">
              {{ lobbySubtitle$({ className: className || defaultClass$() }) }}
            </p>
          </div>
        </div>

        <div class="lobby-details">
          <div class="detail-item">
            <span class="detail-label" :style="{ color: $themeTokens.annotation }">
              {{ roomCodeLabel$() }}:
            </span>
            <code class="code-badge" :style="{ backgroundColor: $themePalette.grey.v_200, color: $themeTokens.text }">
              {{ classRoomName }}
            </code>
          </div>
          <div class="detail-item">
            <span class="detail-label" :style="{ color: $themeTokens.annotation }">
              {{ studentNameLabel$() }}:
            </span>
            <span :style="{ color: $themeTokens.text, fontWeight: 'bold' }">
              {{ userDisplayName }}
            </span>
          </div>
        </div>

        <div class="lobby-actions">
          <KButton
            :text="launchWindowButton$()"
            :primary="true"
            appearance="raised-button"
            icon="openNewTab"
            @click="launchWindow"
          />
          <KButton
            :text="joinClassButton$()"
            :primary="false"
            appearance="flat-button"
            icon="group"
            @click="joinMeeting"
          />
          <KButton
            :text="backToClassButton$()"
            :primary="false"
            appearance="flat-button"
            :to="{ name: ClassesPageNames.CLASS_ASSIGNMENTS, params: { classId } }"
          />
        </div>
      </div>
    </div>
  </LearnAppBarPage>

</template>


<script>

  import { ref, computed, onMounted } from 'vue';
  import KBreadcrumbs from 'kolibri-design-system/lib/KBreadcrumbs';
  import { createTranslator } from 'kolibri/utils/i18n';
  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import LiveMeeting from 'kolibri-common/components/LiveMeeting';
  import useUser from 'kolibri/composables/useUser';
  import commonLearnStrings from '../commonLearnStrings';
  import LearnAppBarPage from '../LearnAppBarPage';
  import useLearnerResources from '../../composables/useLearnerResources';
  import { ClassesPageNames } from '../../constants';

  const learnerLiveStrings = createTranslator('LearnerLiveClassStrings', {
    liveClassHeader: {
      message: '{className} — Live Class',
      context: 'Heading for student live class page',
    },
    defaultClass: {
      message: 'Class',
      context: 'Fallback class title',
    },
    lobbySubtitle: {
      message: 'Join the live interactive video lesson with your teacher and classmates in {className}.',
      context: 'Description on student live class lobby',
    },
    roomCodeLabel: {
      message: 'Meeting Room',
      context: 'Label for meeting room code',
    },
    studentNameLabel: {
      message: 'Joining as',
      context: 'Label indicating the learner display name',
    },
    launchWindowButton: {
      message: 'Join Live Class (Unlimited Window)',
      context: 'Button to join live video meeting in external window with no limits',
    },
    joinClassButton: {
      message: 'Join In-Page',
      context: 'Button to enter the video conference in page',
    },
    backToClassButton: {
      message: 'Back to Class',
      context: 'Button to return to class assignments list',
    },
  });

  export default {
    name: 'LearnerLiveClassPage',
    components: {
      KBreadcrumbs,
      LearnAppBarPage,
      LiveMeeting,
    },
    mixins: [commonLearnStrings],
    props: {
      classId: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      const { full_name, username } = useUser();
      const { getClass, fetchClass } = useLearnerResources();
      const meetingActive = ref(false);

      const {
        liveClassHeader$,
        defaultClass$,
        lobbySubtitle$,
        roomCodeLabel$,
        studentNameLabel$,
        launchWindowButton$,
        joinClassButton$,
        backToClassButton$,
      } = learnerLiveStrings;

      const currentClass = computed(() => {
        return getClass(props.classId) || {};
      });

      const className = computed(() => {
        return currentClass.value.name || '';
      });

      const classRoomName = computed(() => {
        return `kolibri_class_${props.classId}`;
      });

      const userDisplayName = computed(() => {
        return full_name.value || username.value || 'Student';
      });

      const pageTitle = computed(() => {
        return className.value
          ? liveClassHeader$({ className: className.value })
          : liveClassHeader$({ className: defaultClass$() });
      });

      const breadcrumbs = computed(() => [
        {
          text: learnerLiveStrings.learnString('classesLabel'),
          link: { name: ClassesPageNames.ALL_CLASSES },
        },
        {
          text: className.value || defaultClass$(),
          link: { name: ClassesPageNames.CLASS_ASSIGNMENTS, params: { classId: props.classId } },
        },
        {
          text: defaultClass$(),
        },
      ]);

      onMounted(() => {
        fetchClass(props.classId).then(() => {
          pageLoading.value = false;
        });
      });

      function launchWindow() {
        const name = encodeURIComponent(userDisplayName.value);
        const directUrl = `https://meet.jit.si/${classRoomName.value}#userInfo.displayName="${name}"&config.startWithAudioMuted=true&config.prejoinPageEnabled=false`;
        window.open(directUrl, '_blank');
      }

      function joinMeeting() {
        meetingActive.value = true;
      }

      function leaveMeeting() {
        meetingActive.value = false;
      }

      return {
        pageLoading,
        meetingActive,
        classRoomName,
        className,
        userDisplayName,
        pageTitle,
        breadcrumbs,
        ClassesPageNames,
        liveClassHeader$,
        defaultClass$,
        lobbySubtitle$,
        roomCodeLabel$,
        studentNameLabel$,
        launchWindowButton$,
        joinClassButton$,
        backToClassButton$,
        launchWindow,
        joinMeeting,
        leaveMeeting,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .learner-live-page {
    padding: 16px 0;
  }

  .active-meeting-wrapper {
    margin-top: 16px;
    width: 100%;
    min-height: 680px;
  }

  .lobby-card {
    margin-top: 24px;
    padding: 32px;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    max-width: 600px;
  }

  .lobby-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
  }

  .header-icon {
    font-size: 40px;
  }

  .class-title {
    margin: 0 0 4px 0;
    font-size: 1.35rem;
    font-weight: bold;
  }

  .class-subtitle {
    margin: 0;
    font-size: 0.95rem;
    line-height: 1.4;
  }

  .lobby-details {
    margin-bottom: 28px;
  }

  .detail-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    font-size: 0.95rem;
  }

  .code-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-family: monospace;
    font-weight: bold;
  }

  .lobby-actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

</style>
