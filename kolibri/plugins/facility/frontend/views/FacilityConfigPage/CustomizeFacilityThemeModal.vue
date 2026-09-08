<template>
  <KModal
    :title="customizeThemeTitle$()"
    :submitText="coreString('saveAction')"
    :cancelText="coreString('cancelAction')"
    size="large"
    @submit="handleSubmit"
    @cancel="$emit('cancel')"
  >
    <div class="theme-modal-body">
      <p class="modal-description" :style="{ color: $themeTokens.annotation }">
        {{ customizeThemeDescription$() }}
      </p>

      <!-- Real-Time Live Preview -->
      <div class="preview-card" :style="{ border: `1px solid ${$themeTokens.fineLine}` }">
        <div class="preview-label" :style="{ color: $themeTokens.annotation }">
          {{ livePreviewLabel$() }}
        </div>
        <!-- Mini Header Bar Preview -->
        <div
          class="mini-app-bar"
          :style="{
            backgroundColor: formTheme.header_background || '#0f172a',
            color: formTheme.header_text_color || '#ffffff',
          }"
        >
          <div class="mini-app-bar-left">
            <KIcon icon="menu" class="mini-icon" :style="{ fill: formTheme.header_text_color || '#ffffff' }" />
            <img
              v-if="formTheme.logo_url"
              :src="formTheme.logo_url"
              alt="Logo"
              class="mini-logo"
            >
            <span class="mini-title">
              {{ formTheme.header_title || facilityName || defaultSchoolTitle$() }}
            </span>
          </div>
          <div class="mini-app-bar-right">
            <span
              class="mini-badge"
              :style="{
                backgroundColor: formTheme.primary_color || '#2563eb',
                color: '#ffffff',
              }"
            >
              {{ activeBadge$() }}
            </span>
          </div>
        </div>

        <!-- Mini Sign-In Box Preview -->
        <div class="mini-signin-preview" :style="{ backgroundColor: $themeTokens.surface }">
          <img
            v-if="formTheme.logo_url"
            :src="formTheme.logo_url"
            alt="Logo"
            class="mini-signin-logo"
          >
          <div class="mini-signin-title" :style="{ color: formTheme.primary_color || '#1e293b' }">
            {{ formTheme.sign_in_title || formTheme.header_title || facilityName || defaultSchoolTitle$() }}
          </div>
          <div v-if="formTheme.sign_in_subtext" class="mini-signin-subtext" :style="{ color: $themeTokens.annotation }">
            {{ formTheme.sign_in_subtext }}
          </div>
        </div>
      </div>

      <!-- Color Presets -->
      <div class="form-section">
        <h3 class="section-title">{{ colorPresetsLabel$() }}</h3>
        <p class="section-subtitle" :style="{ color: $themeTokens.annotation }">
          {{ choosePresetDesc$() }}
        </p>
        <div class="preset-chips">
          <button
            v-for="preset in colorPresets"
            :key="preset.id"
            type="button"
            class="preset-chip"
            :class="{ active: activePresetId === preset.id }"
            @click="applyPreset(preset)"
          >
            <span class="preset-color-dot" :style="{ backgroundColor: preset.bg }"></span>
            <span class="preset-name">{{ preset.name }}</span>
          </button>
        </div>
      </div>

      <!-- School Name & Header Title -->
      <div class="form-section">
        <h3 class="section-title">{{ schoolHeaderTitleLabel$() }}</h3>
        <KTextbox
          v-model="formTheme.header_title"
          :label="schoolNameInputLabel$()"
          :placeholder="schoolNamePlaceholder$()"
        />
      </div>

      <!-- School Logo Section -->
      <div class="form-section">
        <h3 class="section-title">{{ schoolLogoLabel$() }}</h3>
        <p class="section-subtitle" :style="{ color: $themeTokens.annotation }">
          {{ schoolLogoDesc$() }}
        </p>

        <div class="logo-upload-row">
          <div class="logo-preview-box" :style="{ border: `1px dashed ${$themeTokens.fineLine}` }">
            <img
              v-if="formTheme.logo_url"
              :src="formTheme.logo_url"
              alt="School Logo"
              class="uploaded-logo-preview"
            >
            <div v-else class="logo-placeholder" :style="{ color: $themeTokens.annotation }">
              {{ noLogoUploaded$() }}
            </div>
          </div>

          <div class="logo-actions">
            <label class="file-upload-button">
              <input
                type="file"
                accept="image/png,image/jpeg,image/svg+xml,image/webp,image/gif"
                style="display: none;"
                @change="handleLogoFileUpload"
              >
              <KButton
                :text="uploadLogoButton$()"
                appearance="raised-button"
                :primary="false"
                icon="upload"
                @click.prevent="$event.target.parentElement.querySelector('input').click()"
              />
            </label>

            <KButton
              v-if="formTheme.logo_url"
              :text="removeLogoButton$()"
              appearance="basic-flat-button"
              :primary="false"
              icon="clear"
              @click="formTheme.logo_url = ''"
            />
          </div>
        </div>

        <div class="url-input-wrapper">
          <KTextbox
            v-model="formTheme.logo_url"
            :label="orEnterLogoUrlLabel$()"
            placeholder="https://example.com/school-crest.png"
          />
        </div>
      </div>

      <!-- Custom Colors -->
      <div class="form-section">
        <h3 class="section-title">{{ customColorsLabel$() }}</h3>
        <div class="color-pickers-grid">
          <!-- Header Background -->
          <div class="color-picker-item">
            <label class="color-label">{{ headerBgColorLabel$() }}</label>
            <div class="color-input-combo">
              <input
                v-model="formTheme.header_background"
                type="color"
                class="native-color-picker"
              >
              <input
                v-model="formTheme.header_background"
                type="text"
                class="hex-text-input"
                placeholder="#0f172a"
              >
            </div>
          </div>

          <!-- Header Text Color -->
          <div class="color-picker-item">
            <label class="color-label">{{ headerTextColorLabel$() }}</label>
            <div class="color-input-combo">
              <input
                v-model="formTheme.header_text_color"
                type="color"
                class="native-color-picker"
              >
              <input
                v-model="formTheme.header_text_color"
                type="text"
                class="hex-text-input"
                placeholder="#ffffff"
              >
            </div>
          </div>

          <!-- Primary Brand Color -->
          <div class="color-picker-item">
            <label class="color-label">{{ primaryBrandColorLabel$() }}</label>
            <div class="color-input-combo">
              <input
                v-model="formTheme.primary_color"
                type="color"
                class="native-color-picker"
              >
              <input
                v-model="formTheme.primary_color"
                type="text"
                class="hex-text-input"
                placeholder="#2563eb"
              >
            </div>
          </div>
        </div>
      </div>

      <!-- Sign In Page Customization -->
      <div class="form-section">
        <h3 class="section-title">{{ signInBrandingLabel$() }}</h3>
        <KTextbox
          v-model="formTheme.sign_in_title"
          :label="signInTitleLabel$()"
          :placeholder="signInTitlePlaceholder$()"
        />
        <KTextbox
          v-model="formTheme.sign_in_subtext"
          :label="signInGreetingLabel$()"
          :placeholder="signInGreetingPlaceholder$()"
        />
      </div>

      <!-- Reset Option -->
      <div class="reset-section">
        <KButton
          :text="resetToDefaultsButton$()"
          appearance="basic-flat-button"
          :primary="false"
          @click="handleReset"
        />
      </div>
    </div>
  </KModal>
</template>

<script>
  import { ref, reactive, computed } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';

  const themeModalStrings = createTranslator('CustomizeFacilityThemeModalStrings', {
    customizeThemeTitle: {
      message: 'Customize School Theme & Branding',
      context: 'Title of the modal to configure facility theme',
    },
    customizeThemeDescription: {
      message: 'Personalize the school header, custom logo, brand colors, and student portal greeting for this facility.',
      context: 'Subtitle in the facility theme modal',
    },
    livePreviewLabel: {
      message: 'Live Visual Preview',
      context: 'Label above the real-time preview card',
    },
    defaultSchoolTitle: {
      message: 'School Name',
      context: 'Placeholder school title in preview',
    },
    activeBadge: {
      message: 'Portal Active',
      context: 'Sample badge in preview bar',
    },
    colorPresetsLabel: {
      message: 'School Color Presets',
      context: 'Label for preset colors',
    },
    choosePresetDesc: {
      message: 'Select a curated academic color scheme or customize below.',
      context: 'Help text for color presets',
    },
    schoolHeaderTitleLabel: {
      message: 'Header Title / School Name',
      context: 'Section header for school name',
    },
    schoolNameInputLabel: {
      message: 'School or Campus Name for Header',
      context: 'Input label',
    },
    schoolNamePlaceholder: {
      message: 'e.g. Springfield High School',
      context: 'Input placeholder',
    },
    schoolLogoLabel: {
      message: 'School Emblem or Logo',
      context: 'Section header for school logo',
    },
    schoolLogoDesc: {
      message: 'Upload your school crest, institution emblem, or official logo (PNG, JPG, SVG, WebP).',
      context: 'Help text for logo upload',
    },
    uploadLogoButton: {
      message: 'Upload Logo Image',
      context: 'Button to upload an image',
    },
    removeLogoButton: {
      message: 'Remove Logo',
      context: 'Button to remove current logo',
    },
    noLogoUploaded: {
      message: 'No custom logo uploaded yet',
      context: 'Placeholder when no logo is set',
    },
    orEnterLogoUrlLabel: {
      message: 'Or provide an Image URL',
      context: 'Input label for URL',
    },
    customColorsLabel: {
      message: 'Custom Color Palette',
      context: 'Section title for custom colors',
    },
    headerBgColorLabel: {
      message: 'Header Background Color',
      context: 'Label for header background color picker',
    },
    headerTextColorLabel: {
      message: 'Header Text & Icons Color',
      context: 'Label for header text color picker',
    },
    primaryBrandColorLabel: {
      message: 'Primary Brand Color (Buttons & Highlights)',
      context: 'Label for primary brand color picker',
    },
    signInBrandingLabel: {
      message: 'Sign-In Portal Branding',
      context: 'Section title for sign-in page customization',
    },
    signInTitleLabel: {
      message: 'Sign-In Card Heading',
      context: 'Label for sign in title',
    },
    signInTitlePlaceholder: {
      message: 'e.g. Springfield High School Portal',
      context: 'Placeholder for sign in title',
    },
    signInGreetingLabel: {
      message: 'Welcome Message / Greeting Subtext',
      context: 'Label for welcome greeting',
    },
    signInGreetingPlaceholder: {
      message: 'e.g. Empowering minds through digital learning',
      context: 'Placeholder for greeting subtext',
    },
    resetToDefaultsButton: {
      message: 'Reset Theme to Defaults',
      context: 'Button to reset custom theme',
    },
  });

  export default {
    name: 'CustomizeFacilityThemeModal',
    mixins: [commonCoreStrings],
    props: {
      facilityName: {
        type: String,
        default: '',
      },
      currentTheme: {
        type: Object,
        default: () => ({}),
      },
    },
    emits: ['submit', 'cancel'],
    setup(props, { emit }) {
      const {
        customizeThemeTitle$,
        customizeThemeDescription$,
        livePreviewLabel$,
        defaultSchoolTitle$,
        activeBadge$,
        colorPresetsLabel$,
        choosePresetDesc$,
        schoolHeaderTitleLabel$,
        schoolNameInputLabel$,
        schoolNamePlaceholder$,
        schoolLogoLabel$,
        schoolLogoDesc$,
        uploadLogoButton$,
        removeLogoButton$,
        noLogoUploaded$,
        orEnterLogoUrlLabel$,
        customColorsLabel$,
        headerBgColorLabel$,
        headerTextColorLabel$,
        primaryBrandColorLabel$,
        signInBrandingLabel$,
        signInTitleLabel$,
        signInTitlePlaceholder$,
        signInGreetingLabel$,
        signInGreetingPlaceholder$,
        resetToDefaultsButton$,
      } = themeModalStrings;

      const formTheme = reactive({
        header_title: props.currentTheme.header_title || props.facilityName || '',
        header_background: props.currentTheme.header_background || '#1e3a8a',
        header_text_color: props.currentTheme.header_text_color || '#ffffff',
        primary_color: props.currentTheme.primary_color || '#2563eb',
        logo_url: props.currentTheme.logo_url || '',
        sign_in_title: props.currentTheme.sign_in_title || '',
        sign_in_subtext: props.currentTheme.sign_in_subtext || '',
        sign_in_background: props.currentTheme.sign_in_background || '',
      });

      const colorPresets = [
        {
          id: 'navy',
          name: 'Academic Navy',
          bg: '#1e3a8a',
          text: '#ffffff',
          primary: '#2563eb',
        },
        {
          id: 'forest',
          name: 'Emerald Forest',
          bg: '#14532d',
          text: '#ffffff',
          primary: '#16a34a',
        },
        {
          id: 'crimson',
          name: 'Crimson Red',
          bg: '#881337',
          text: '#ffffff',
          primary: '#e11d48',
        },
        {
          id: 'purple',
          name: 'Royal Purple',
          bg: '#581c87',
          text: '#ffffff',
          primary: '#9333ea',
        },
        {
          id: 'amber',
          name: 'Earth Amber',
          bg: '#78350f',
          text: '#ffffff',
          primary: '#d97706',
        },
        {
          id: 'slate',
          name: 'Midnight Slate',
          bg: '#0f172a',
          text: '#ffffff',
          primary: '#3b82f6',
        },
        {
          id: 'clean',
          name: 'Clean White',
          bg: '#ffffff',
          text: '#0f172a',
          primary: '#2563eb',
        },
      ];

      const activePresetId = computed(() => {
        const found = colorPresets.find(
          p =>
            p.bg.toLowerCase() === (formTheme.header_background || '').toLowerCase() &&
            p.primary.toLowerCase() === (formTheme.primary_color || '').toLowerCase(),
        );
        return found ? found.id : null;
      });

      function applyPreset(preset) {
        formTheme.header_background = preset.bg;
        formTheme.header_text_color = preset.text;
        formTheme.primary_color = preset.primary;
      }

      function handleLogoFileUpload(event) {
        const file = event.target.files && event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = e => {
          formTheme.logo_url = e.target.result;
        };
        reader.readAsDataURL(file);
      }

      function handleReset() {
        formTheme.header_title = '';
        formTheme.header_background = '';
        formTheme.header_text_color = '';
        formTheme.primary_color = '';
        formTheme.logo_url = '';
        formTheme.sign_in_title = '';
        formTheme.sign_in_subtext = '';
        formTheme.sign_in_background = '';
      }

      function handleSubmit() {
        emit('submit', { ...formTheme });
      }

      return {
        formTheme,
        colorPresets,
        activePresetId,
        applyPreset,
        handleLogoFileUpload,
        handleReset,
        handleSubmit,
        customizeThemeTitle$,
        customizeThemeDescription$,
        livePreviewLabel$,
        defaultSchoolTitle$,
        activeBadge$,
        colorPresetsLabel$,
        choosePresetDesc$,
        schoolHeaderTitleLabel$,
        schoolNameInputLabel$,
        schoolNamePlaceholder$,
        schoolLogoLabel$,
        schoolLogoDesc$,
        uploadLogoButton$,
        removeLogoButton$,
        noLogoUploaded$,
        orEnterLogoUrlLabel$,
        customColorsLabel$,
        headerBgColorLabel$,
        headerTextColorLabel$,
        primaryBrandColorLabel$,
        signInBrandingLabel$,
        signInTitleLabel$,
        signInTitlePlaceholder$,
        signInGreetingLabel$,
        signInGreetingPlaceholder$,
        resetToDefaultsButton$,
      };
    },
  };
</script>

<style lang="scss" scoped>
  .theme-modal-body {
    max-height: 70vh;
    overflow-y: auto;
    padding: 8px 4px;
  }

  .modal-description {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 14.5px;
    line-height: 1.5;
  }

  .preview-card {
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 24px;
    background: #f8fafc;
  }

  .preview-label {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
  }

  .mini-app-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  }

  .mini-app-bar-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .mini-icon {
    width: 20px;
    height: 20px;
  }

  .mini-logo {
    max-height: 28px;
    width: auto;
    border-radius: 3px;
    object-fit: contain;
  }

  .mini-title {
    font-size: 15px;
    font-weight: 700;
  }

  .mini-badge {
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
  }

  .mini-signin-preview {
    margin-top: 14px;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    text-align: center;
  }

  .mini-signin-logo {
    max-height: 48px;
    margin: 0 auto 8px;
    display: block;
    object-fit: contain;
  }

  .mini-signin-title {
    font-size: 16px;
    font-weight: 800;
  }

  .mini-signin-subtext {
    font-size: 13px;
    margin-top: 4px;
  }

  .form-section {
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid #e2e8f0;
  }

  .section-title {
    font-size: 16px;
    font-weight: 700;
    margin: 0 0 6px 0;
  }

  .section-subtitle {
    font-size: 13px;
    margin: 0 0 14px 0;
  }

  .preset-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
  }

  .preset-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 20px;
    border: 1.5px solid #cbd5e1;
    background: #ffffff;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    transition: all 0.15s ease;

    &:hover {
      border-color: #94a3b8;
    }

    &.active {
      border-color: #2563eb;
      background: #eff6ff;
      color: #1d4ed8;
      box-shadow: 0 1px 3px rgba(37, 99, 235, 0.2);
    }
  }

  .preset-color-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.15);
  }

  .logo-upload-row {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 12px;
  }

  .logo-preview-box {
    width: 100px;
    height: 70px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f1f5f9;
    overflow: hidden;
    padding: 6px;
  }

  .uploaded-logo-preview {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }

  .logo-placeholder {
    font-size: 11px;
    text-align: center;
    line-height: 1.3;
  }

  .logo-actions {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .url-input-wrapper {
    margin-top: 8px;
  }

  .color-pickers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 16px;
    margin-top: 12px;
  }

  .color-picker-item {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .color-label {
    font-size: 13px;
    font-weight: 600;
  }

  .color-input-combo {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .native-color-picker {
    width: 38px;
    height: 38px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    cursor: pointer;
    padding: 2px;
    background: #ffffff;
  }

  .hex-text-input {
    flex: 1;
    height: 38px;
    padding: 0 10px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-family: monospace;
    font-size: 14px;
  }

  .reset-section {
    padding-top: 12px;
    text-align: right;
  }
</style>
