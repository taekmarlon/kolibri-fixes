<template>

  <LearnAppBarPage
    :appBarTitle="learnString('learnLabel')"
    :loading="pageLoading"
  >
    <div role="main" class="live-meeting-page">
      <!-- Active Live Meeting -->
      <div v-if="meetingActive" class="active-meeting-wrapper">
        <LiveMeeting
          :roomName="currentRoomName"
          :meetingTitle="currentMeetingTitle"
          @leave="leaveMeeting"
        />
      </div>

      <!-- Meeting Lobby / Join Screen -->
      <div v-else class="meeting-lobby-container">
        <div class="lobby-intro">
          <h1 class="page-title" :style="{ color: $themeTokens.text }">
            {{ virtualMeetingTitle$() }}
          </h1>
          <p class="page-desc" :style="{ color: $themeTokens.annotation }">
            {{ virtualMeetingDesc$() }}
          </p>
        </div>

        <!-- Enrolled Class Live Rooms Card -->
        <div
          v-if="enrolledClassrooms.length"
          class="card class-rooms-card"
          :style="{
            backgroundColor: '#eff6ff',
            border: '1px solid #93c5fd',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '24px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
          }"
        >
          <div class="card-header" style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
            <KIcon icon="classes" class="header-icon" :style="{ color: '#1d4ed8', fontSize: '28px' }" />
            <div>
              <h2 class="card-title" :style="{ color: '#1e3a8a', margin: '0', fontSize: '18px', fontWeight: '800' }">
                🎓 Your Enrolled Class Live Rooms
              </h2>
              <p class="card-desc" :style="{ color: '#3b82f6', margin: '4px 0 0', fontSize: '13px' }">
                Join the live virtual classroom with your teacher and classmates with one click:
              </p>
            </div>
          </div>
          <div class="class-rooms-list" style="display: flex; flex-direction: column; gap: 10px;">
            <div
              v-for="classroom in enrolledClassrooms"
              :key="classroom.id"
              class="class-room-item"
              :style="{
                backgroundColor: '#ffffff',
                border: '1px solid #bfdbfe',
                borderRadius: '10px',
                padding: '14px 18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '12px',
              }"
            >
              <div>
                <div style="font-weight: 700; font-size: 15.5px; color: #1e293b;">
                  {{ classroom.name }} — Live Class
                </div>
                <div style="font-size: 12px; color: #64748b; margin-top: 2px;">
                  Room ID: <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px;">kolibri_class_{{ classroom.id }}</code>
                </div>
              </div>
              <KButton
                :text="`Join ${classroom.name} (Unlimited)`"
                :primary="true"
                appearance="raised-button"
                icon="openNewTab"
                @click="joinSpecificRoom(`kolibri_class_${classroom.id}`, `${classroom.name} — Live Class`)"
              />
            </div>
          </div>
        </div>

        <KGrid gutter="24" class="lobby-grid">
          <!-- Join / Create Room Card -->
          <KGridItem :layout12="{ span: 7 }">
            <div
              class="card join-card"
              :style="{
                backgroundColor: $themeTokens.surface,
                border: `1px solid ${$themeTokens.fineLine}`,
              }"
            >
              <div class="card-header">
                <KIcon icon="group" class="header-icon" :style="{ color: $themeTokens.primary }" />
                <div>
                  <h2 class="card-title" :style="{ color: $themeTokens.text }">
                    {{ joinOrCreateHeader$() }}
                  </h2>
                  <p class="card-desc" :style="{ color: $themeTokens.annotation }">
                    {{ joinOrCreateSubtext$() }}
                  </p>
                </div>
              </div>

              <div class="input-section">
                <KTextbox
                  v-model="roomInput"
                  :label="roomNameLabel$()"
                  :placeholder="roomNamePlaceholder$()"
                  :invalid="Boolean(roomError)"
                  :invalidText="roomError"
                  @keydown.enter="joinRoom"
                />

                <div class="user-info-badge" :style="{ backgroundColor: $themePalette.grey.v_200 }">
                  <span :style="{ color: $themeTokens.annotation }">{{ joiningAsLabel$() }}:</span>
                  <span :style="{ color: $themeTokens.text, fontWeight: 'bold' }">{{ userDisplayName }}</span>
                </div>
              </div>

              <div class="card-actions">
                <KButton
                  :text="joinMeetingButton$()"
                  :primary="true"
                  appearance="raised-button"
                  icon="openNewTab"
                  @click="joinRoom"
                />
                <KButton
                  :text="generateRandomButton$()"
                  :primary="false"
                  appearance="flat-button"
                  @click="generateRandomRoom"
                />
              </div>
            </div>
          </KGridItem>

          <!-- Recent Rooms Card -->
          <KGridItem :layout12="{ span: 5 }">
            <div
              class="card recent-card"
              :style="{
                backgroundColor: $themeTokens.surface,
                border: `1px solid ${$themeTokens.fineLine}`,
              }"
            >
              <h2 class="card-title" :style="{ color: $themeTokens.text }">
                {{ recentRoomsTitle$() }}
              </h2>
              <p class="card-desc" :style="{ color: $themeTokens.annotation }">
                {{ recentRoomsDesc$() }}
              </p>

              <div v-if="recentRooms.length" class="recent-list">
                <div
                  v-for="room in recentRooms"
                  :key="room.roomId"
                  class="recent-item"
                  :style="{ borderBottom: `1px solid ${$themeTokens.fineLine}` }"
                >
                  <div class="recent-info">
                    <span class="recent-room-title" :style="{ color: $themeTokens.text }">
                      {{ room.title || room.roomId }}
                    </span>
                    <span class="recent-room-id" :style="{ color: $themeTokens.annotation }">
                      {{ room.roomId }}
                    </span>
                  </div>
                  <KButton
                    :text="rejoinButton$()"
                    appearance="basic-flat-button"
                    :primary="false"
                    @click="joinSpecificRoom(room.roomId, room.title)"
                  />
                </div>
              </div>

              <div v-else class="empty-recent" :style="{ color: $themeTokens.annotation }">
                {{ noRecentRooms$() }}
              </div>
            </div>
          </KGridItem>
        </KGrid>
      </div>
    </div>
  </LearnAppBarPage>

</template>


<script>

  import { ref, computed, onMounted } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import LiveMeeting from 'kolibri-common/components/LiveMeeting';
  import useLiveMeeting from 'kolibri-common/composables/useLiveMeeting';
  import useUser from 'kolibri/composables/useUser';
  import { LearnerClassroomResource } from '../apiResources';
  import commonLearnStrings from './commonLearnStrings';
  import LearnAppBarPage from './LearnAppBarPage';

  const livePageStrings = createTranslator('LiveMeetingPageStrings', {
    virtualMeetingTitle: {
      message: 'Live Virtual Meeting',
      context: 'Page title for general live meeting page',
    },
    virtualMeetingDesc: {
      message: 'Start or join real-time interactive video meetings with audio, video, screen sharing, and live chat.',
      context: 'Subtitle for live meeting page',
    },
    joinOrCreateHeader: {
      message: 'Join or Create a Room',
      context: 'Header for join/create card',
    },
    joinOrCreateSubtext: {
      message: 'Enter any room name or topic to meet with peers or instructors.',
      context: 'Help text for join card',
    },
    roomNameLabel: {
      message: 'Room Name or Topic',
      context: 'Label for room name text field',
    },
    roomNamePlaceholder: {
      message: 'e.g. Science-Study-Group',
      context: 'Placeholder for room name input',
    },
    joiningAsLabel: {
      message: 'Joining as',
      context: 'Label indicating the user display name',
    },
    joinMeetingButton: {
      message: 'Join Meeting (Unlimited)',
      context: 'Button to join meeting',
    },
    generateRandomButton: {
      message: 'New Random Room',
      context: 'Button to generate random room ID',
    },
    recentRoomsTitle: {
      message: 'Recent Rooms',
      context: 'Header for recent rooms list',
    },
    recentRoomsDesc: {
      message: 'Quickly re-connect to rooms you previously joined.',
      context: 'Description for recent rooms card',
    },
    rejoinButton: {
      message: 'Join',
      context: 'Button to re-join a recent room',
    },
    noRecentRooms: {
      message: 'No recent rooms yet.',
      context: 'Message when user has no recent rooms',
    },
    enterRoomError: {
      message: 'Please enter a room name',
      context: 'Error message when input is empty',
    },
  });

  export default {
    name: 'LiveMeetingPage',
    components: {
      LearnAppBarPage,
      LiveMeeting,
    },
    mixins: [commonLearnStrings],
    setup() {
      const { full_name, username } = useUser();
      const { recentRooms, generateRoomId, saveRecentRoom } = useLiveMeeting();

      const {
        virtualMeetingTitle$,
        virtualMeetingDesc$,
        joinOrCreateHeader$,
        joinOrCreateSubtext$,
        roomNameLabel$,
        roomNamePlaceholder$,
        joiningAsLabel$,
        joinMeetingButton$,
        generateRandomButton$,
        recentRoomsTitle$,
        recentRoomsDesc$,
        rejoinButton$,
        noRecentRooms$,
        enterRoomError$,
      } = livePageStrings;

      const meetingActive = ref(false);
      const currentRoomName = ref('');
      const currentMeetingTitle = ref('');
      const roomInput = ref('');
      const roomError = ref('');
      const enrolledClassrooms = ref([]);

      onMounted(() => {
        LearnerClassroomResource.fetchCollection()
          .then(classes => {
            enrolledClassrooms.value = classes || [];
            if (classes && classes.length > 0 && !roomInput.value) {
              roomInput.value = `class_${classes[0].id}`;
            }
          })
          .catch(() => {
            enrolledClassrooms.value = [];
          });
      });

      const userDisplayName = computed(() => {
        return full_name.value || username.value || 'Guest User';
      });

      function joinRoom() {
        if (!roomInput.value.trim()) {
          if (enrolledClassrooms.value && enrolledClassrooms.value.length > 0) {
            const firstClass = enrolledClassrooms.value[0];
            joinSpecificRoom(`kolibri_class_${firstClass.id}`, `${firstClass.name} — Live Class`);
            return;
          }
          generateRandomRoom();
        }
        roomError.value = '';
        const cleanName = `kolibri_${roomInput.value.trim().replace(/[^a-zA-Z0-9-_]/g, '_')}`;
        joinSpecificRoom(cleanName, roomInput.value.trim());
      }

      function generateRandomRoom() {
        const randomId = generateRoomId('kolibri_room');
        roomInput.value = randomId.replace('kolibri_', '');
        roomError.value = '';
      }

      function joinSpecificRoom(roomId, title) {
        saveRecentRoom({
          roomId,
          title: title || roomId,
        });
        const cleanName = roomId.replace(/[^a-zA-Z0-9-_]/g, '_');
        const displayName = encodeURIComponent(userDisplayName.value);
        const directUrl = `https://meet.jit.si/${cleanName}#userInfo.displayName="${displayName}"&config.prejoinPageEnabled=false&config.startWithAudioMuted=false`;
        window.open(directUrl, '_blank');
      }

      function leaveMeeting() {
        meetingActive.value = false;
        currentRoomName.value = '';
        currentMeetingTitle.value = '';
      }

      return {
        pageLoading,
        meetingActive,
        currentRoomName,
        currentMeetingTitle,
        roomInput,
        roomError,
        enrolledClassrooms,
        joinSpecificRoom,
        joinRoom,
        generateRandomRoom,
        leaveMeeting,
        userDisplayName,
        recentRooms,
        virtualMeetingTitle$,
        virtualMeetingDesc$,
        joinOrCreateHeader$,
        joinOrCreateSubtext$,
        roomNameLabel$,
        roomNamePlaceholder$,
        joiningAsLabel$,
        joinMeetingButton$,
        generateRandomButton$,
        recentRoomsTitle$,
        recentRoomsDesc$,
        rejoinButton$,
        noRecentRooms$,
        joinRoom,
        generateRandomRoom,
        joinSpecificRoom,
        leaveMeeting,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .live-meeting-page {
    padding: 16px 0;
  }

  .active-meeting-wrapper {
    width: 100%;
    min-height: 700px;
  }

  .lobby-intro {
    margin-bottom: 24px;
  }

  .page-title {
    margin: 0 0 8px 0;
    font-size: 1.5rem;
    font-weight: bold;
  }

  .page-desc {
    margin: 0;
    font-size: 1rem;
  }

  .card {
    padding: 24px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
  }

  .header-icon {
    font-size: 36px;
  }

  .card-title {
    margin: 0 0 4px 0;
    font-size: 1.2rem;
    font-weight: bold;
  }

  .card-desc {
    margin: 0;
    font-size: 0.9rem;
  }

  .input-section {
    margin-bottom: 24px;
  }

  .user-info-badge {
    margin-top: 12px;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.9rem;
    display: flex;
    gap: 8px;
  }

  .card-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .recent-list {
    display: flex;
    flex-direction: column;
    margin-top: 16px;
  }

  .recent-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
  }

  .recent-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .recent-room-title {
    font-weight: bold;
    font-size: 0.95rem;
  }

  .recent-room-id {
    font-size: 0.8rem;
    font-family: monospace;
  }

  .empty-recent {
    margin-top: 24px;
    text-align: center;
    font-style: italic;
  }

</style>
