import { ref } from 'vue';

const isPlaying = ref(false);
const currentSpeakingId = ref(null);

export default function useSpeechSynthesis() {
  const isSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

  function cleanTextForSpeech(raw) {
    if (!raw) return '';
    return raw
      // Strip markdown code blocks & math
      .replace(/```[\s\S]*?```/g, 'Code block omitted.')
      .replace(/`([^`]+)`/g, '$1')
      // Strip LaTeX delimiters and commands
      .replace(/\$\$[\s\S]*?\$\$/g, '')
      .replace(/\$([^\$]+)\$/g, '$1')
      .replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, '$1 over $2')
      .replace(/\\[a-zA-Z]+/g, ' ')
      // Strip markdown links and images
      .replace(/!\[([^\]]*)\]\([^)]+\)/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      // Strip markdown headers, bold, italics, quotes
      .replace(/[#*~_>]/g, ' ')
      // Clean multiple spaces and trim
      .replace(/\s+/g, ' ')
      .trim();
  }

  function speak(text, { id = null, gradeLevel = 'elementary' } = {}) {
    if (!isSupported) return;

    // Stop any ongoing speech first
    window.speechSynthesis.cancel();

    if (isPlaying.value && currentSpeakingId.value === id) {
      isPlaying.value = false;
      currentSpeakingId.value = null;
      return;
    }

    const clean = cleanTextForSpeech(text);
    if (!clean) return;

    const utterance = new window.SpeechSynthesisUtterance(clean);

    // Grade-adaptive speech settings
    if (gradeLevel === 'pre_elem') {
      utterance.rate = 0.88; // Slightly slower, encouraging pace for kids
      utterance.pitch = 1.15; // Cheerful, warm tone
    } else if (gradeLevel === 'secondary') {
      utterance.rate = 1.05; // Efficient, clear pace
      utterance.pitch = 1.0;
    } else {
      utterance.rate = 0.95; // Friendly standard cadence
      utterance.pitch = 1.05;
    }

    // Try to pick an English voice or native locale voice if available
    const voices = window.speechSynthesis.getVoices();
    if (voices && voices.length) {
      const preferred = voices.find(
        v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('Jenny'))
      ) || voices.find(v => v.lang.startsWith('en'));
      if (preferred) {
        utterance.voice = preferred;
      }
    }

    utterance.onstart = () => {
      isPlaying.value = true;
      currentSpeakingId.value = id;
    };

    utterance.onend = () => {
      isPlaying.value = false;
      currentSpeakingId.value = null;
    };

    utterance.onerror = () => {
      isPlaying.value = false;
      currentSpeakingId.value = null;
    };

    window.speechSynthesis.speak(utterance);
  }

  function stop() {
    if (isSupported) {
      window.speechSynthesis.cancel();
      isPlaying.value = false;
      currentSpeakingId.value = null;
    }
  }

  return {
    isSupported,
    isPlaying,
    currentSpeakingId,
    speak,
    stop,
    cleanTextForSpeech,
  };
}
