/**
 * Utilities for PHIEDU live video meeting sessions.
 * Ensures all live rooms use PHIEDU room identifiers and that Jitsi branding/watermarks are completely hidden.
 */

export function buildLiveMeetingUrl({
  domain = 'meet.jit.si',
  roomName = '',
  displayName = 'PHIEDU User',
  subject = 'PHIEDU Live Class',
  startWithAudioMuted = false,
} = {}) {
  const cleanRoom = String(roomName || '').replace(/[^a-zA-Z0-9-_]/g, '_');
  const encodedName = encodeURIComponent(displayName || 'PHIEDU User');
  const encodedSubject = encodeURIComponent(subject || 'PHIEDU Live Class');

  const configParams = [
    `userInfo.displayName="${encodedName}"`,
    `config.subject="${encodedSubject}"`,
    `config.prejoinPageEnabled=false`,
    `config.prejoinConfig.enabled=false`,
    `config.hideLogo=true`,
    `config.disableDeepLinking=true`,
    `config.startWithAudioMuted=${Boolean(startWithAudioMuted)}`,
    `interfaceConfig.SHOW_JITSI_WATERMARK=false`,
    `interfaceConfig.SHOW_WATERMARK_FOR_GUESTS=false`,
    `interfaceConfig.SHOW_BRAND_WATERMARK=false`,
    `interfaceConfig.SHOW_POWERED_BY=false`,
    `interfaceConfig.DEFAULT_LOGO_URL=""`,
  ].join('&');

  return `https://${domain}/${cleanRoom}#${configParams}`;
}

/**
 * Sanitizes a classroom name or topic for use in live meeting URLs and room IDs.
 * Converts spaces and special punctuation into clean underscores.
 * Example: 'Grade 1 Sec-Diamond' -> 'Grade_1_Sec_Diamond'
 */
export function sanitizeRoomName(name) {
  if (!name) return '';
  return String(name)
    .trim()
    .replace(/[^a-zA-Z0-9\s_-]/g, '')
    .replace(/[\s-]+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '');
}

/**
 * Returns a short, human-readable room name for a given classroom.
 * Format: PHIEDU_<SanitizedClassName>
 * Example:
 *   - getClassRoomName('86ed...', 'Grade 1 Sec-Diamond') => 'PHIEDU_Grade_1_Sec_Diamond'
 *   - getClassRoomName('021b...', 'Room1') => 'PHIEDU_Room1'
 *   - getClassRoomName('86ed42b381532536a4b0d14cf77a5917') => 'PHIEDU_86ED42'
 */
export function getClassRoomName(classId, className = '') {
  if (className && String(className).trim()) {
    const clean = sanitizeRoomName(className);
    if (clean) {
      return `PHIEDU_${clean}`;
    }
  }
  if (classId) {
    const cleanId = String(classId).replace(/[^a-zA-Z0-9]/g, '');
    const shortId = cleanId.length > 8 ? cleanId.slice(0, 6).toUpperCase() : cleanId;
    return `PHIEDU_${shortId}`;
  }
  return 'PHIEDU_Live';
}
