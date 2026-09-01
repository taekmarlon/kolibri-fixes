import { ref, computed } from 'vue';
import Lockr from 'lockr';

const RECENT_ROOMS_KEY = 'kolibri_recent_live_rooms';

export default function useLiveMeeting() {
  const activeRoom = ref(null);
  const recentRooms = ref(Lockr.get(RECENT_ROOMS_KEY) || []);

  function generateRoomId(prefix = 'kolibri', identifier = '') {
    const randomSuffix = Math.random().toString(36).substring(2, 8);
    const cleanId = identifier ? identifier.replace(/[^a-zA-Z0-9]/g, '_') : '';
    return `${prefix}_${cleanId ? cleanId + '_' : ''}${randomSuffix}`;
  }

  function saveRecentRoom(roomInfo) {
    const rooms = Lockr.get(RECENT_ROOMS_KEY) || [];
    const filtered = rooms.filter(r => r.roomId !== roomInfo.roomId);
    filtered.unshift({
      ...roomInfo,
      lastJoined: new Date().toISOString(),
    });
    // Keep max 10 recent rooms
    const trimmed = filtered.slice(0, 10);
    Lockr.set(RECENT_ROOMS_KEY, trimmed);
    recentRooms.value = trimmed;
  }

  function removeRecentRoom(roomId) {
    const rooms = Lockr.get(RECENT_ROOMS_KEY) || [];
    const filtered = rooms.filter(r => r.roomId !== roomId);
    Lockr.set(RECENT_ROOMS_KEY, filtered);
    recentRooms.value = filtered;
  }

  return {
    activeRoom,
    recentRooms: computed(() => recentRooms.value),
    generateRoomId,
    saveRecentRoom,
    removeRecentRoom,
  };
}
