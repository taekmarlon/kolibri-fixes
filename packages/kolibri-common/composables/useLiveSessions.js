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
        return fetchLiveSessions();
      })
      .catch(() => {});
  }

  function normalizeId(id) {
    return String(id || '')
      .replace(/[^a-zA-Z0-9]/g, '')
      .toLowerCase();
  }

  function isClassLive(classId) {
    if (!classId) return false;
    const target = normalizeId(classId);
    if (!target) return false;

    if (activeLiveSessions.value[classId] && activeLiveSessions.value[classId].active) {
      return true;
    }

    for (const [key, session] of Object.entries(activeLiveSessions.value)) {
      if (session && session.active && normalizeId(key) === target) {
        return true;
      }
    }
    return false;
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
