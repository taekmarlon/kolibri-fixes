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

export function getClassRoomName(classId) {
  return `phiedu_class_${classId || 'general'}`;
}
