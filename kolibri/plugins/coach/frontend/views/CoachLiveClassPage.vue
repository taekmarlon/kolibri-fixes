<template>

  <CoachAppBarPage :loading="pageLoading">
    <KPageContainer>
      <!-- Active Live Meeting View -->
      <div v-if="meetingActive" class="active-meeting-wrapper">
        <LiveMeeting
          :roomName="activeRoomName"
          :meetingTitle="activeMeetingTitle"
          @leave="endMeeting"
        />
      </div>

      <!-- Live Class Lobby / Dashboard -->
      <div v-else class="lobby-container">
        <div class="lobby-header">
          <h1 class="title" :style="{ color: $themeTokens.text }">
            {{ liveClassTitle$() }}
          </h1>
          <p class="description" :style="{ color: $themeTokens.annotation }">
            {{ liveClassDescription$({ className: className || defaultClass$() }) }}
          </p>
        </div>

        <KGrid gutter="24" class="lobby-grid">
          <!-- Main Class Room Card -->
          <KGridItem :layout12="{ span: 7 }">
            <div
              class="room-card"
              :style="{
                backgroundColor: $themeTokens.surface,
                border: `1px solid ${$themeTokens.fineLine}`,
              }"
            >
              <div class="room-card-header">
                <KIcon icon="group" class="card-icon" :style="{ color: $themeTokens.primary }" />
                <div>
                  <h2 class="card-title" :style="{ color: $themeTokens.text }">
                    {{ className ? classMeetingTitle$({ className }) : instantMeetingTitle$() }}
                  </h2>
                  <span class="card-subtitle" :style="{ color: $themeTokens.annotation }">
                    {{ classRoomSubtext$() }}
                  </span>
                </div>
              </div>

              <div class="room-details">
                <div class="info-row">
                  <span class="label" :style="{ color: $themeTokens.annotation }">
                    {{ roomCodeLabel$() }}:
                  </span>
                  <code class="code-badge" :style="{ backgroundColor: $themePalette.grey.v_200, color: $themeTokens.text }">
                    {{ defaultClassRoomName }}
                  </code>
                </div>
                <div class="info-row">
                  <span class="label" :style="{ color: $themeTokens.annotation }">
                    {{ featuresLabel$() }}:
                  </span>
                  <span :style="{ color: $themeTokens.text }">
                    {{ featuresList$() }}
                  </span>
                </div>
              </div>

              <div class="room-actions">
                <KButton
                  :text="startClassMeetingButton$()"
                  :primary="true"
                  appearance="raised-button"
                  icon="group"
                  @click="startMeeting(defaultClassRoomName, className ? classMeetingTitle$({ className }) : liveClassTitle$())"
                />
              </div>
            </div>
          </KGridItem>

          <!-- Custom Room Card -->
          <KGridItem :layout12="{ span: 5 }">
            <div
              class="room-card custom-card"
              :style="{
                backgroundColor: $themeTokens.surface,
                border: `1px solid ${$themeTokens.fineLine}`,
              }"
            >
              <h3 class="custom-title" :style="{ color: $themeTokens.text }">
                {{ customRoomTitle$() }}
              </h3>
              <p class="custom-desc" :style="{ color: $themeTokens.annotation }">
                {{ customRoomDesc$() }}
              </p>

              <KTextbox
                v-model="customRoomInput"
                :label="customRoomInputLabel$()"
                :placeholder="customRoomPlaceholder$()"
                :invalid="Boolean(customRoomError)"
                :invalidText="customRoomError"
              />

              <div class="custom-actions">
                <KButton
                  :text="startCustomMeetingButton$()"
                  :primary="false"
                  appearance="flat-button"
                  @click="startCustomMeeting"
                />
              </div>
            </div>
          </KGridItem>
        </KGrid>
      </div>
    </KPageContainer>
  </CoachAppBarPage>

</template>


<script>

  import { ref, computed } from 'vue';
  import { mapState } from 'vuex';
  import { createTranslator } from 'kolibri/utils/i18n';
  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import LiveMeeting from 'kolibri-common/components/LiveMeeting';
  import useLiveMeeting from 'kolibri-common/composables/useLiveMeeting';
  import CoachAppBarPage from './CoachAppBarPage';
  import commonCoach from './common';

  const coachLiveStrings = createTranslator('CoachLiveClassStrings', {
    liveClassTitle: {
      message: 'Live Virtual Classrooms',
      context: 'Page heading for coach live classroom feature',
    },
    liveClassDescription: {
      message: 'Host interactive live video classes, group discussions, and presentations with learners in {className}.',
      context: 'Subtitle description for live classes',
    },
    defaultClass: {
      message: 'your class',
      context: 'Fallback class name',
    },
    classMeetingTitle: {
      message: '{className} — Live Class',
      context: 'Title of the class meeting room',
    },
    instantMeetingTitle: {
      message: 'Classroom Live Meeting',
      context: 'Title when no class name is specified',
    },
    classRoomSubtext: {
      message: 'Learners enrolled in this class can join this room from their Learn dashboard.',
      context: 'Help text explaining that learners join automatically',
    },
    roomCodeLabel: {
      message: 'Room ID',
      context: 'Label for meeting room code',
    },
    featuresLabel: {
      message: 'Included',
      context: 'Label for features included',
    },
    featuresList: {
      message: 'HD Video, Audio, Screen Sharing, Live Chat, Hand Raising',
      context: 'List of features in Jitsi meeting',
    },
    startClassMeetingButton: {
      message: 'Start Live Class Now',
      context: 'Button to begin live video class',
    },
    customRoomTitle: {
      message: 'Custom Meeting Topic',
      context: 'Header for custom meeting room creation',
    },
    customRoomDesc: {
      message: 'Create a specific breakout room or topic-based meeting.',
      context: 'Description for custom room input',
    },
    customRoomInputLabel: {
      message: 'Room Name or Topic',
      context: 'Input label for custom room name',
    },
    customRoomPlaceholder: {
      message: 'e.g. Math-Review-Q3',
      context: 'Placeholder for room name',
    },
    startCustomMeetingButton: {
      message: 'Start Custom Meeting',
      context: 'Button to start meeting with custom room name',
    },
    enterRoomNameError: {
      message: 'Please enter a room name',
      context: 'Validation error when input is blank',
    },
  });

  export default {
    name: 'CoachLiveClassPage',
    components: {
      CoachAppBarPage,
      LiveMeeting,
    },
    mixins: [commonCoach],
    setup() {
      const { saveRecentRoom } = useLiveMeeting();
      const meetingActive = ref(false);
      const activeRoomName = ref('');
      const activeMeetingTitle = ref('');
      const customRoomInput = ref('');
      const customRoomError = ref('');

      const {
        liveClassTitle$,
        liveClassDescription$,
        classMeetingTitle$,
        instantMeetingTitle$,
        classRoomSubtext$,
        roomCodeLabel$,
        featuresLabel$,
        featuresList$,
        startClassMeetingButton$,
        customRoomTitle$,
        customRoomDesc$,
        customRoomInputLabel$,
        customRoomPlaceholder$,
        startCustomMeetingButton$,
        enterRoomNameError$,
        defaultClass$,
      } = coachLiveStrings;

      return {
        pageLoading,
        meetingActive,
        activeRoomName,
        activeMeetingTitle,
        customRoomInput,
        customRoomError,
        saveRecentRoom,
        liveClassTitle$,
        liveClassDescription$,
        classMeetingTitle$,
        instantMeetingTitle$,
        classRoomSubtext$,
        roomCodeLabel$,
        featuresLabel$,
        featuresList$,
        startClassMeetingButton$,
        customRoomTitle$,
        customRoomDesc$,
        customRoomInputLabel$,
        customRoomPlaceholder$,
        startCustomMeetingButton$,
        enterRoomNameError$,
        defaultClass$,
      };
    },
    computed: {
      ...mapState('classSummary', { classId: 'id', className: 'name' }),
      defaultClassRoomName() {
        const id = this.classId || 'general';
        return `kolibri_class_${id}`;
      },
    },
    methods: {
      startMeeting(roomName, title) {
        this.activeRoomName = roomName;
        this.activeMeetingTitle = title;
        this.meetingActive = true;
        this.saveRecentRoom({
          roomId: roomName,
          title,
          classId: this.classId,
        });
      },
      startCustomMeeting() {
        if (!this.customRoomInput.trim()) {
          this.customRoomError = this.enterRoomNameError$();
          return;
        }
        this.customRoomError = '';
        const roomName = `kolibri_${this.customRoomInput.trim().replace(/[^a-zA-Z0-9-_]/g, '_')}`;
        this.startMeeting(roomName, this.customRoomInput.trim());
      },
      endMeeting() {
        this.meetingActive = false;
        this.activeRoomName = '';
        this.activeMeetingTitle = '';
      },
    },
  };

</script>


<style lang="scss" scoped>

  .lobby-container {
    padding: 16px 0;
  }

  .lobby-header {
    margin-bottom: 24px;
  }

  .title {
    margin: 0 0 8px 0;
    font-size: 1.5rem;
    font-weight: bold;
  }

  .description {
    margin: 0;
    font-size: 1rem;
    line-height: 1.5;
  }

  .room-card {
    padding: 24px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .room-card-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
  }

  .card-icon {
    font-size: 36px;
  }

  .card-title {
    margin: 0 0 4px 0;
    font-size: 1.25rem;
    font-weight: bold;
  }

  .card-subtitle {
    font-size: 0.9rem;
  }

  .room-details {
    margin-bottom: 24px;
  }

  .info-row {
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
    font-size: 0.95rem;
    font-weight: bold;
  }

  .room-actions {
    display: flex;
    gap: 12px;
  }

  .custom-card {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .custom-title {
    margin: 0;
    font-size: 1.15rem;
    font-weight: bold;
  }

  .custom-desc {
    margin: 0;
    font-size: 0.9rem;
  }

  .custom-actions {
    display: flex;
    justify-content: flex-end;
  }

  .active-meeting-wrapper {
    width: 100%;
    min-height: 700px;
  }

</style>
