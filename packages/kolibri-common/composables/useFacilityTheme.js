import { ref, computed, watch, set } from 'vue';
import themeConfig from 'kolibri/styles/themeConfig';
import FacilityDatasetResource from 'kolibri-common/apiResources/FacilityDatasetResource';
import useFacility from './useFacility';

// Retain base theme defaults so we can revert when a facility has no custom theme
const baseDefaults = {
  appBar: {
    background: themeConfig.appBar ? themeConfig.appBar.background : null,
    textColor: themeConfig.appBar ? themeConfig.appBar.textColor : null,
    headerTitle: null,
    primaryColor: null,
    topLogo: themeConfig.appBar && themeConfig.appBar.topLogo ? { ...themeConfig.appBar.topLogo } : null,
  },
  signIn: {
    title: themeConfig.signIn ? themeConfig.signIn.title : null,
    subtext: null,
    topLogo: themeConfig.signIn && themeConfig.signIn.topLogo ? { ...themeConfig.signIn.topLogo } : null,
    background: themeConfig.signIn ? themeConfig.signIn.background : null,
  },
  sideNav: {
    topLogo: themeConfig.sideNav && themeConfig.sideNav.topLogo ? { ...themeConfig.sideNav.topLogo } : null,
  },
  background: {
    image: null,
    opacity: null,
  },
};

/**
 * Applies a facility-specific theme to the global reactive themeConfig.
 * Updates the app bar header, logo, colors, sign-in branding, and side navigation.
 *
 * @param {Object} theme - Custom facility theme object
 */
export function applyFacilityTheme(theme = {}, facilityName = '') {
  const custom = theme || {};

  // 1. App Bar Header Styling
  if (custom.header_background) {
    set(themeConfig.appBar, 'background', custom.header_background);
  } else {
    set(themeConfig.appBar, 'background', baseDefaults.appBar.background);
  }

  if (custom.header_text_color) {
    set(themeConfig.appBar, 'textColor', custom.header_text_color);
  } else {
    set(themeConfig.appBar, 'textColor', baseDefaults.appBar.textColor);
  }

  const title = custom.header_title || facilityName || null;
  set(themeConfig.appBar, 'headerTitle', title);
  set(themeConfig.appBar, 'primaryColor', custom.primary_color || null);

  // 2. School Logo in App Bar, Side Nav, and Sign-In
  if (custom.logo_url) {
    set(themeConfig.appBar, 'topLogo', {
      src: custom.logo_url,
      alt: title || 'School Logo',
      style:
        'max-height: 40px; width: auto; max-width: 140px; object-fit: contain; margin-right: 12px; border-radius: 4px;',
    });
    set(themeConfig.sideNav, 'topLogo', {
      src: custom.logo_url,
      alt: title || 'School Logo',
      style:
        'max-height: 46px; width: auto; max-width: 150px; object-fit: contain; margin: 8px 0;',
    });
    set(themeConfig.signIn, 'topLogo', {
      src: custom.logo_url,
      alt: title || 'School Logo',
      style:
        'max-height: 88px; width: auto; max-width: 220px; object-fit: contain; margin-bottom: 12px;',
    });
  } else {
    set(themeConfig.appBar, 'topLogo', baseDefaults.appBar.topLogo);
    set(themeConfig.sideNav, 'topLogo', baseDefaults.sideNav.topLogo);
    set(themeConfig.signIn, 'topLogo', baseDefaults.signIn.topLogo);
  }

  // 3. Sign-In Page Customization
  if (custom.sign_in_title || title) {
    set(themeConfig.signIn, 'title', custom.sign_in_title || title);
  } else {
    set(themeConfig.signIn, 'title', baseDefaults.signIn.title);
  }

  set(themeConfig.signIn, 'subtext', custom.sign_in_subtext || null);

  if (custom.sign_in_background) {
    set(themeConfig.signIn, 'background', custom.sign_in_background);
  } else {
    set(themeConfig.signIn, 'background', baseDefaults.signIn.background);
  }

  // 4. Primary Brand Color CSS Variable
  if (typeof document !== 'undefined' && document.documentElement) {
    if (custom.primary_color) {
      document.documentElement.style.setProperty('--facility-brand-primary', custom.primary_color);
    } else {
      document.documentElement.style.removeProperty('--facility-brand-primary');
    }
  }

  // 5. Facility Background Image & Transparency
  const bgImage = custom.background_image_url || null;
  const bgOpacity =
    custom.background_opacity !== undefined && custom.background_opacity !== null
      ? Number(custom.background_opacity)
      : 0.2;

  if (themeConfig) {
    if (!themeConfig.background) {
      set(themeConfig, 'background', { image: null, opacity: null });
    }
    set(themeConfig.background, 'image', bgImage);
    set(themeConfig.background, 'opacity', bgImage ? bgOpacity : null);
  }

  if (typeof document !== 'undefined' && document.body) {
    let bgEl = document.getElementById('facility-theme-background-layer');
    if (bgImage) {
      if (!bgEl) {
        bgEl = document.createElement('div');
        bgEl.id = 'facility-theme-background-layer';
        bgEl.style.position = 'fixed';
        bgEl.style.top = '0';
        bgEl.style.left = '0';
        bgEl.style.width = '100vw';
        bgEl.style.height = '100vh';
        bgEl.style.zIndex = '-1';
        bgEl.style.pointerEvents = 'none';
        bgEl.style.backgroundPosition = 'center';
        bgEl.style.backgroundRepeat = 'no-repeat';
        bgEl.style.backgroundSize = 'cover';
        bgEl.style.transition = 'opacity 0.25s ease-in-out';
        document.body.prepend(bgEl);
      }
      bgEl.style.backgroundImage = `url("${bgImage}")`;
      bgEl.style.opacity = String(bgOpacity);
      bgEl.style.display = 'block';
    } else if (bgEl) {
      bgEl.style.display = 'none';
      bgEl.style.backgroundImage = 'none';
    }

    if (document.documentElement) {
      if (bgImage) {
        document.documentElement.style.setProperty('--facility-bg-opacity', String(bgOpacity));
      } else {
        document.documentElement.style.removeProperty('--facility-bg-opacity');
      }
    }
  }
}

/**
 * Composable providing facility theme state, active theme getters, and save/reset actions.
 */
export default function useFacilityTheme() {
  const {
    facilityConfig,
    facilityId,
    selectedFacilityId,
    currentFacilityName,
    fetchFacilityConfig,
    fetchFacility,
  } = useFacility();

  const targetFacilityId = selectedFacilityId || facilityId;

  const facilityTheme = computed(() => {
    return (
      (facilityConfig.value &&
        facilityConfig.value.extra_fields &&
        facilityConfig.value.extra_fields.theme) ||
      {}
    );
  });

  const hasCustomTheme = computed(() => {
    const t = facilityTheme.value;
    return Boolean(
      t.header_background ||
        t.header_title ||
        t.logo_url ||
        t.background_image_url ||
        t.primary_color ||
        t.sign_in_title ||
        t.sign_in_subtext,
    );
  });

  // Keep themeConfig in sync with facilityConfig changes
  watch(
    [facilityTheme, currentFacilityName],
    ([newTheme, name]) => {
      applyFacilityTheme(newTheme, name);
    },
    { immediate: true, deep: true },
  );

  // Auto-fetch facility dataset config if not loaded yet or when selected facility changes
  watch(
    targetFacilityId,
    newId => {
      if (newId) {
        fetchFacilityConfig(newId);
        if (fetchFacility) {
          fetchFacility(newId);
        }
      }
    },
    { immediate: true },
  );

  /**
   * Persists updated theme configuration to the facility dataset.
   * @param {string} datasetId - The ID of the facility dataset.
   * @param {Object} updatedTheme - The new theme settings object.
   * @returns {Promise<Object>}
   */
  async function saveFacilityTheme(datasetId, updatedTheme) {
    if (!datasetId) {
      throw new Error('datasetId is required to save facility theme');
    }

    const currentExtra = (facilityConfig.value && facilityConfig.value.extra_fields) || {};
    const newExtraFields = {
      ...currentExtra,
      theme: { ...updatedTheme },
    };

    const result = await FacilityDatasetResource.saveModel({
      id: datasetId,
      data: {
        extra_fields: newExtraFields,
      },
    });

    if (facilityConfig.value) {
      facilityConfig.value.extra_fields = newExtraFields;
    }

    applyFacilityTheme(updatedTheme);
    return result;
  }

  /**
   * Resets the facility theme back to system defaults.
   * @param {string} datasetId - The ID of the facility dataset.
   * @returns {Promise<Object>}
   */
  async function resetFacilityTheme(datasetId) {
    return saveFacilityTheme(datasetId, {});
  }

  return {
    facilityTheme,
    hasCustomTheme,
    currentFacilityName,
    selectedFacilityId,
    applyFacilityTheme,
    saveFacilityTheme,
    resetFacilityTheme,
    fetchFacilityConfig,
  };
}
