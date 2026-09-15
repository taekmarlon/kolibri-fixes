import { ref, onMounted } from 'vue';

export default function useCollapsible(storageKey = null, defaultExpanded = true) {
  const isExpanded = ref(defaultExpanded);

  onMounted(() => {
    if (storageKey && typeof window !== 'undefined' && window.localStorage) {
      try {
        const stored = localStorage.getItem(`kolibri_section_${storageKey}`);
        if (stored !== null) {
          isExpanded.value = stored === 'true';
        }
      } catch (e) {
        // Handle localStorage disabled or private browsing quota limits
      }
    }
  });

  function toggleExpand() {
    isExpanded.value = !isExpanded.value;
    if (storageKey && typeof window !== 'undefined' && window.localStorage) {
      try {
        localStorage.setItem(`kolibri_section_${storageKey}`, String(isExpanded.value));
      } catch (e) {
        // Ignore quota/access errors
      }
    }
  }

  function expand() {
    isExpanded.value = true;
    if (storageKey && typeof window !== 'undefined' && window.localStorage) {
      try {
        localStorage.setItem(`kolibri_section_${storageKey}`, 'true');
      } catch (e) {
        // Ignore
      }
    }
  }

  function collapse() {
    isExpanded.value = false;
    if (storageKey && typeof window !== 'undefined' && window.localStorage) {
      try {
        localStorage.setItem(`kolibri_section_${storageKey}`, 'false');
      } catch (e) {
        // Ignore
      }
    }
  }

  return {
    isExpanded,
    toggleExpand,
    expand,
    collapse,
  };
}
