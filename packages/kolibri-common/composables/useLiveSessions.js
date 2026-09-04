import { ref, computed } from 'vue';
import client from 'kolibri/client';

const activeLiveSessions = ref({});
const isFetchingSessions = ref(false);

export default function useLiveSessions() {
  function fetchLiveSessions() {
    isFetchingSessions.value = true;
    return client({
      url: '/api/device/live_sessions/',
      method: 'GET',
    })
      .then(response => {
        activeLiveSessions.value = response.data || {};
        isFetchingSessions.value = false;
        return activeLiveSessions.value;
      })
      .catch(() => {
        isFetchingSessions.value = false;
        return {};
      });
  }

  function setLiveSessionActive({ classId, roomName, active = true }) {
    if (!classId) return Promise.resolve();
    return client({
      url: '/api/device/live_sessions/',
      method: 'POST',
      data: {
        class_id: classId,
        room_name: roomName || `kolibri_class_${classId}`,
        active,
      },
    })
      .then(() => {
        if (active) {
          activeLiveSessions.value = {
            ...activeLiveSessions.value,
            [classId]: {
              active: true,
              room_name: roomName || `kolibri_class_${classId}`,
              class_id: classId,
            },
          };
        } else {
          const updated = { ...activeLiveSessions.value };
          delete updated[classId];
          activeLiveSessions.value = updated;
        }
      })
      .catch(() => {});
  }

  function isClassLive(classId) {
    if (!classId) return false;
    const session = activeLiveSessions.value[classId];
    return Boolean(session && session.active);
  }

  const liveClassesCount = computed(() => {
    return Object.keys(activeLiveSessions.value).length;
  });

  return {
    activeLiveSessions,
    isFetchingSessions,
    fetchLiveSessions,
    setLiveSessionActive,
    isClassLive,
    liveClassesCount,
  };
}
