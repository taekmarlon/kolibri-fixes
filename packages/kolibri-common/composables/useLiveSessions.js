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
    if (!classId && !roomName) return Promise.resolve();
    return client({
      url: '/api/device/live_sessions/',
      method: 'POST',
      data: {
        class_id: classId || roomName,
        room_name: roomName || (classId ? `phiedu_class_${classId}` : ''),
        active,
      },
    })
      .then(() => {
        return fetchLiveSessions();
      })
      .catch(() => {});
  }

  function getVariants(id) {
    const str = String(id || '').trim().toLowerCase();
    if (!str) return [];
    const setOfVariants = new Set();
    setOfVariants.add(str);

    const alnum = str.replace(/[^a-z0-9]/g, '');
    if (alnum) setOfVariants.add(alnum);

    const prefixes = ['phiedu_class_', 'kolibri_class_', 'phiedu_room_', 'phiedu_', 'room_', 'class_'];
    for (const p of prefixes) {
      if (str.startsWith(p)) {
        const sub = str.slice(p.length);
        if (sub) {
          setOfVariants.add(sub);
          const subAlnum = sub.replace(/[^a-z0-9]/g, '');
          if (subAlnum) setOfVariants.add(subAlnum);
        }
      }
    }
    return Array.from(setOfVariants);
  }

  function isClassLive(classId) {
    if (!classId) return false;
    const targets = getVariants(classId);
    if (!targets.length) return false;

    for (const t of targets) {
      if (activeLiveSessions.value[t] && activeLiveSessions.value[t].active) {
        return true;
      }
    }

    for (const [key, session] of Object.entries(activeLiveSessions.value)) {
      if (session && session.active) {
        const keyVariants = getVariants(key);
        if (targets.some(t => keyVariants.includes(t))) {
          return true;
        }
      }
    }
    return false;
  }

  function isRoomLive(roomIdentifier) {
    return isClassLive(roomIdentifier);
  }

  const liveClassesCount = computed(() => {
    return Object.values(activeLiveSessions.value).filter(s => s && s.active).length;
  });

  return {
    activeLiveSessions,
    isFetchingSessions,
    fetchLiveSessions,
    setLiveSessionActive,
    isClassLive,
    isRoomLive,
    liveClassesCount,
  };
}
