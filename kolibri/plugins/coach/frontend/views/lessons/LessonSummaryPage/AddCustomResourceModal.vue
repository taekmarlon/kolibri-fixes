<template>

  <KModal
    :title="modalTitle$()"
    :submitText="addResourceButton$()"
    :cancelText="cancelButton$()"
    :submitDisabled="isSubmitDisabled || isSubmitting"
    size="large"
    @submit="handleSubmit"
    @cancel="$emit('close')"
  >
    <div class="add-custom-resource-modal">
      <!-- Tabs Navigation -->
      <div
        class="tab-button-group"
        :style="{ borderBottom: `1px solid ${$themeTokens.fineLine}` }"
      >
        <KButton
          :text="tabFilesLabel$()"
          icon="document"
          :appearance="activeTab === 'file' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'file'"
          class="tab-btn"
          @click="activeTab = 'file'"
        />
        <KButton
          :text="tabYoutubeLabel$()"
          icon="video"
          :appearance="activeTab === 'youtube' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'youtube'"
          class="tab-btn"
          @click="activeTab = 'youtube'"
        />
        <KButton
          :text="tabHtml5Label$()"
          icon="html5"
          :appearance="activeTab === 'html5' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'html5'"
          class="tab-btn"
          @click="activeTab = 'html5'"
        />
        <KButton
          :text="tabAiLabel$()"
          icon="hint"
          :appearance="activeTab === 'ai' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'ai'"
          class="tab-btn"
          @click="activeTab = 'ai'"
        />
      </div>

      <!-- TAB 1: UPLOAD FILE (PDF, Images, Docs) -->
      <div
        v-if="activeTab === 'file'"
        class="tab-content"
      >
        <p :style="{ color: $themeTokens.annotation }">
          {{ uploadFileDesc$() }}
        </p>

        <button
          type="button"
          class="drop-zone"
          :style="{
            borderColor: selectedFile ? $themeTokens.primary : $themeTokens.fineLine,
            backgroundColor: selectedFile ? $themePalette.grey.v_100 : $themeTokens.surface,
          }"
          @click="triggerFileInput('fileInput')"
        >
          <input
            ref="fileInput"
            type="file"
            class="hidden-file-input"
            :aria-label="uploadResourceFileLabel$()"
            accept=".pdf,.png,.jpg,.jpeg,.gif,.webp,.svg,.docx,.doc,.txt,.pptx,.xlsx,.odt,.csv,.md"
            @change="onFileSelected($event, 'file')"
          >
          <KIcon
            icon="document"
            class="upload-icon"
          />
          <p
            v-if="!selectedFile"
            class="drop-text"
          >
            {{ selectFilePrompt$() }}
          </p>
          <div
            v-else
            class="file-info-badge"
          >
            <span class="file-name">{{ selectedFile.name }}</span>
            <span
              class="file-size"
              :style="{ color: $themeTokens.annotation }"
            >
              ({{ formatFileSize(selectedFile.size) }})
            </span>
          </div>
        </button>

        <KTextbox
          v-model="fileTitle"
          :label="titleLabel$()"
          :invalid="Boolean(fileTitleError)"
          :invalidText="fileTitleError"
          class="mt-16"
        />

        <KTextbox
          v-model="fileDescription"
          :label="descriptionLabel$()"
          :textArea="true"
          class="mt-16"
        />
      </div>

      <!-- TAB 2: YOUTUBE VIDEO -->
      <div
        v-if="activeTab === 'youtube'"
        class="tab-content"
      >
        <p :style="{ color: $themeTokens.annotation }">
          {{ youtubeDesc$() }}
        </p>

        <KTextbox
          v-model="youtubeUrl"
          :label="youtubeUrlLabel$()"
          placeholder="https://www.youtube.com/watch?v=..."
          :invalid="Boolean(youtubeUrlError)"
          :invalidText="youtubeUrlError"
        />

        <KTextbox
          v-model="youtubeTitle"
          :label="titleLabel$()"
          :invalid="Boolean(youtubeTitleError)"
          :invalidText="youtubeTitleError"
          class="mt-16"
        />

        <KTextbox
          v-model="youtubeDescription"
          :label="descriptionLabel$()"
          :textArea="true"
          class="mt-16"
        />

        <!-- Live In-Kolibri YouTube Preview -->
        <div
          v-if="isValidYoutubeUrl"
          class="mt-16 video-preview"
        >
          <h4 :style="{ color: $themeTokens.text, marginBottom: '8px' }">
            {{ videoPreviewLabel$() }}
          </h4>
          <YouTubePlayer
            :url="youtubeUrl"
            :title="youtubeTitle || 'Video Preview'"
          />
        </div>
      </div>

      <!-- TAB 3: HTML5 PACKAGE -->
      <div
        v-if="activeTab === 'html5'"
        class="tab-content"
      >
        <p :style="{ color: $themeTokens.annotation }">
          {{ html5Desc$() }}
        </p>

        <button
          type="button"
          class="drop-zone"
          :style="{
            borderColor: selectedHtml5File ? $themeTokens.primary : $themeTokens.fineLine,
            backgroundColor: selectedHtml5File ? $themePalette.grey.v_100 : $themeTokens.surface,
          }"
          @click="triggerFileInput('html5Input')"
        >
          <input
            ref="html5Input"
            type="file"
            class="hidden-file-input"
            :aria-label="uploadHtml5ZipLabel$()"
            accept=".zip,.html,.htm"
            @change="onFileSelected($event, 'html5')"
          >
          <KIcon
            icon="html5"
            class="upload-icon"
          />
          <p
            v-if="!selectedHtml5File"
            class="drop-text"
          >
            {{ selectHtml5Prompt$() }}
          </p>
          <div
            v-else
            class="file-info-badge"
          >
            <span class="file-name">{{ selectedHtml5File.name }}</span>
            <span
              class="file-size"
              :style="{ color: $themeTokens.annotation }"
            >
              ({{ formatFileSize(selectedHtml5File.size) }})
            </span>
          </div>
        </button>

        <KTextbox
          v-model="html5Title"
          :label="titleLabel$()"
          :invalid="Boolean(html5TitleError)"
          :invalidText="html5TitleError"
          class="mt-16"
        />

        <KTextbox
          v-model="html5Description"
          :label="descriptionLabel$()"
          :textArea="true"
          class="mt-16"
        />
      </div>

      <!-- TAB 4: AI GENERATOR -->
      <div
        v-if="activeTab === 'ai'"
        class="tab-content"
      >
        <p :style="{ color: $themeTokens.annotation }">
          {{ aiDesc$() }}
        </p>

        <KTextbox
          v-model="aiTopic"
          :label="aiTopicLabel$()"
          :placeholder="aiTopicPlaceholder$()"
          :invalid="Boolean(aiTopicError)"
          :invalidText="aiTopicError"
          :disabled="isGeneratingAi"
        />

        <div class="mt-16 row-2">
          <KSelect
            v-model="aiGrade"
            :label="gradeLevelLabel$()"
            :options="gradeOptions"
            :disabled="isGeneratingAi"
          />
          <KSelect
            v-model="aiFormat"
            :label="materialTypeLabel$()"
            :options="formatOptions"
            :disabled="isGeneratingAi"
          />
        </div>

        <div class="d-flex mt-16">
          <KButton
            :text="isGeneratingAi ? aiGenerating$() : aiGenerateButton$()"
            :primary="true"
            appearance="raised-button"
            icon="hint"
            :disabled="!aiTopic.trim() || isGeneratingAi"
            @click="handleGenerateAiContent"
          />
        </div>

        <div
          v-if="isGeneratingAi"
          class="ai-loading mt-16"
        >
          <KCircularLoader :delay="false" />
          <span class="loading-msg">{{ aiGeneratingText$() }}</span>
        </div>

        <div
          v-if="aiContent && !isGeneratingAi"
          class="mt-16"
        >
          <KTextbox
            v-model="aiTitle"
            :label="titleLabel$()"
            class="mb-16"
          />
          <h4 :style="{ color: $themeTokens.text, marginBottom: '8px' }">
            {{ generatedContentLabel$() }}
          </h4>
          <KTextbox
            v-model="aiContent"
            :textArea="true"
            :label="aiContentLabel$()"
            rows="10"
          />
        </div>
      </div>

      <!-- Submitting Indicator -->
      <div
        v-if="isSubmitting"
        class="submitting-overlay"
      >
        <KCircularLoader :delay="false" />
        <p>{{ savingResource$() }}</p>
      </div>
    </div>
  </KModal>

</template>


<script>

  import { ref, computed } from 'vue';
  import client from 'kolibri/client';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useSnackbar from 'kolibri/composables/useSnackbar';
  import useAiTutor from 'kolibri-common/composables/useAiTutor';
  import YouTubePlayer from 'kolibri-common/components/YouTubePlayer';

  const modalStrings = createTranslator('AddCustomResourceModalStrings', {
    modalTitle: {
      message: 'Add Custom Resource to Lesson',
      context: 'Modal header title',
    },
    addResourceButton: {
      message: 'Add to Lesson',
      context: 'Submit button',
    },
    cancelButton: {
      message: 'Cancel',
      context: 'Cancel button',
    },
    tabFilesLabel: {
      message: 'Upload File',
      context: 'Tab label for files',
    },
    tabYoutubeLabel: {
      message: 'YouTube Video',
      context: 'Tab label for YouTube videos',
    },
    tabHtml5Label: {
      message: 'HTML5 Package',
      context: 'Tab label for HTML5 packages',
    },
    tabAiLabel: {
      message: 'Generate with AI',
      context: 'Tab label for AI generated notes',
    },
    uploadFileDesc: {
      message: 'Upload documents, PDFs, pictures, or notes for your learners to view.',
      context: 'Tab description',
    },
    selectFilePrompt: {
      message: 'Click or drop a file here (.pdf, .png, .jpg, .docx, .txt, etc.)',
      context: 'File drop area text',
    },
    youtubeDesc: {
      message: 'Paste a YouTube video link. It will play safely inside Kolibri for your learners.',
      context: 'YouTube tab description',
    },
    youtubeUrlLabel: {
      message: 'YouTube Video URL',
      context: 'URL textbox label',
    },
    videoPreviewLabel: {
      message: 'Video Preview',
      context: 'Preview title',
    },
    html5Desc: {
      message: 'Upload an interactive HTML5 simulation or activity (.zip or .html).',
      context: 'HTML5 tab description',
    },
    selectHtml5Prompt: {
      message: 'Click or drop a .zip or .html file here',
      context: 'HTML5 drop area text',
    },
    aiDesc: {
      message: 'Create structured study guides, summaries, or practice notes instantly with AI.',
      context: 'AI tab description',
    },
    aiTopicLabel: {
      message: 'Topic or Concept',
      context: 'Input label',
    },
    aiTopicPlaceholder: {
      message: 'e.g. Introduction to Photosynthesis, Civil War Timeline, Solving Linear Equations',
      context: 'Input placeholder',
    },
    gradeLevelLabel: {
      message: 'Target Level',
      context: 'Grade dropdown label',
    },
    materialTypeLabel: {
      message: 'Resource Style',
      context: 'Format dropdown label',
    },
    aiGenerateButton: {
      message: 'Generate Material with AI',
      context: 'Generate button',
    },
    aiGenerating: {
      message: 'Generating...',
      context: 'Button generating text',
    },
    aiGeneratingText: {
      message: 'Crafting comprehensive study notes with AI...',
      context: 'Loading text',
    },
    generatedContentLabel: {
      message: 'Generated Resource (Markdown)',
      context: 'Textarea header',
    },
    aiContentLabel: {
      message: 'Edit Content',
      context: 'Textarea label',
    },
    titleLabel: {
      message: 'Resource Title',
      context: 'Title textbox label',
    },
    descriptionLabel: {
      message: 'Description or Coach Instructions (Optional)',
      context: 'Description label',
    },
    savingResource: {
      message: 'Saving resource to lesson...',
      context: 'Saving status',
    },
    successNotice: {
      message: 'Resource successfully added to lesson!',
      context: 'Snackbar success message',
    },
    errorNotice: {
      message: 'Could not add resource. Please check the inputs and try again.',
      context: 'Snackbar error message',
    },
    uploadResourceFileLabel: {
      message: 'Upload resource file',
      context: 'Accessibility label for file input',
    },
    uploadHtml5ZipLabel: {
      message: 'Upload HTML5 zip package',
      context: 'Accessibility label for HTML5 file input',
    },
  });

  export default {
    name: 'AddCustomResourceModal',
    components: {
      YouTubePlayer,
    },
    setup(props, { emit }) {
      const { createSnackbar } = useSnackbar();
      const { generateLesson } = useAiTutor();

      const activeTab = ref('file');
      const isSubmitting = ref(false);

      // File Tab State
      const selectedFile = ref(null);
      const fileTitle = ref('');
      const fileDescription = ref('');
      const fileTitleError = ref('');
      const fileInput = ref(null);

      // YouTube Tab State
      const youtubeUrl = ref('');
      const youtubeTitle = ref('');
      const youtubeDescription = ref('');
      const youtubeUrlError = ref('');
      const youtubeTitleError = ref('');

      // HTML5 Tab State
      const selectedHtml5File = ref(null);
      const html5Title = ref('');
      const html5Description = ref('');
      const html5TitleError = ref('');
      const html5Input = ref(null);

      // AI Tab State
      const aiTopic = ref('');
      const aiGrade = ref('elementary');
      const aiFormat = ref('notes');
      const aiContent = ref('');
      const aiTitle = ref('');
      const aiTopicError = ref('');
      const isGeneratingAi = ref(false);

      const gradeOptions = [
        { label: 'Elementary School', value: 'elementary' },
        { label: 'Middle School', value: 'middle' },
        { label: 'High School', value: 'high' },
        { label: 'Higher Education / Adult', value: 'college' },
      ];

      const formatOptions = [
        { label: 'Comprehensive Study Notes & Key Definitions', value: 'notes' },
        { label: 'Brief Summary & Key Takeaways', value: 'summary' },
        { label: 'Practice Questions & Discussion Prompts', value: 'practice' },
      ];

      const isValidYoutubeUrl = computed(() => {
        const u = youtubeUrl.value.trim();
        return u.includes('youtube.com') || u.includes('youtu.be');
      });

      const isSubmitDisabled = computed(() => {
        if (activeTab.value === 'file') {
          return !selectedFile.value || !fileTitle.value.trim();
        }
        if (activeTab.value === 'youtube') {
          return !isValidYoutubeUrl.value || !youtubeTitle.value.trim();
        }
        if (activeTab.value === 'html5') {
          return !selectedHtml5File.value || !html5Title.value.trim();
        }
        if (activeTab.value === 'ai') {
          return !aiContent.value.trim() || !aiTitle.value.trim();
        }
        return true;
      });

      function formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
      }

      function triggerFileInput(refName) {
        if (refName === 'fileInput' && fileInput.value) {
          fileInput.value.click();
        } else if (refName === 'html5Input' && html5Input.value) {
          html5Input.value.click();
        }
      }

      function onFileSelected(event, type) {
        const file = event.target.files && event.target.files[0];
        if (!file) return;

        const baseName = file.name.replace(/\.[^/.]+$/, '');

        if (type === 'file') {
          selectedFile.value = file;
          if (!fileTitle.value) {
            fileTitle.value = baseName;
          }
        } else if (type === 'html5') {
          selectedHtml5File.value = file;
          if (!html5Title.value) {
            html5Title.value = baseName;
          }
        }
      }

      async function handleGenerateAiContent() {
        if (!aiTopic.value.trim()) {
          aiTopicError.value = 'Please enter a topic';
          return;
        }
        aiTopicError.value = '';
        isGeneratingAi.value = true;
        try {
          const result = await generateLesson(aiTopic.value, aiGrade.value, '45');
          aiContent.value = result || `# ${aiTopic.value}\n\nKey Concepts and Learning Notes.`;
          aiTitle.value = `AI Study Guide: ${aiTopic.value}`;
        } catch (err) {
          aiContent.value = `# ${aiTopic.value}\n\n### Summary\nOverview of ${aiTopic.value} for students.\n\n### Key Points\n- Point 1\n- Point 2\n\n### Review Questions\n1. Explain the main idea in your own words.`;
          aiTitle.value = `Study Notes: ${aiTopic.value}`;
        } finally {
          isGeneratingAi.value = false;
        }
      }

      async function handleSubmit() {
        isSubmitting.value = true;
        try {
          const endpointUrl = `/api/lessons/lesson/${props.lessonId}/custom_resource/`;
          let response;

          if (activeTab.value === 'file' || activeTab.value === 'html5') {
            const formData = new FormData();
            const file = activeTab.value === 'file' ? selectedFile.value : selectedHtml5File.value;
            const title = activeTab.value === 'file' ? fileTitle.value : html5Title.value;
            const desc =
              activeTab.value === 'file' ? fileDescription.value : html5Description.value;

            formData.append('file', file);
            formData.append('title', title);
            formData.append('description', desc);
            formData.append('resource_type', activeTab.value === 'html5' ? 'html5' : '');

            response = await client({
              url: endpointUrl,
              method: 'POST',
              data: formData,
              headers: { 'Content-Type': 'multipart/form-data' },
            });
          } else if (activeTab.value === 'youtube') {
            response = await client({
              url: endpointUrl,
              method: 'POST',
              data: {
                resource_type: 'youtube',
                title: youtubeTitle.value,
                description: youtubeDescription.value,
                url: youtubeUrl.value,
              },
            });
          } else if (activeTab.value === 'ai') {
            response = await client({
              url: endpointUrl,
              method: 'POST',
              data: {
                resource_type: 'ai_text',
                title: aiTitle.value || `Study Notes: ${aiTopic.value}`,
                description: `AI-generated study material on ${aiTopic.value}`,
                content: aiContent.value,
              },
            });
          }

          createSnackbar(modalStrings.successNotice$());
          emit('added', response.data);
          emit('close');
        } catch (err) {
          createSnackbar(modalStrings.errorNotice$());
        } finally {
          isSubmitting.value = false;
        }
      }

      return {
        activeTab,
        isSubmitting,
        isSubmitDisabled,
        // File tab
        selectedFile,
        fileTitle,
        fileDescription,
        fileTitleError,
        fileInput,
        // YouTube tab
        youtubeUrl,
        youtubeTitle,
        youtubeDescription,
        youtubeUrlError,
        youtubeTitleError,
        isValidYoutubeUrl,
        // HTML5 tab
        selectedHtml5File,
        html5Title,
        html5Description,
        html5TitleError,
        html5Input,
        // AI tab
        aiTopic,
        aiGrade,
        aiFormat,
        aiContent,
        aiTitle,
        aiTopicError,
        isGeneratingAi,
        gradeOptions,
        formatOptions,
        // Methods
        formatFileSize,
        triggerFileInput,
        onFileSelected,
        handleGenerateAiContent,
        handleSubmit,
        // Strings
        ...modalStrings,
      };
    },
    props: {
      lessonId: {
        type: String,
        required: true,
      },
    },
    emits: ['close', 'added'],
  };

</script>


<style lang="scss" scoped>

  .add-custom-resource-modal {
    padding-top: 8px;
  }

  .tab-button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding-bottom: 16px;
    margin-bottom: 16px;
  }

  .tab-btn {
    min-width: 130px;
  }

  .tab-content {
    animation: fade-in 0.2s ease-in-out;
  }

  .drop-zone {
    display: block;
    width: 100%;
    padding: 24px;
    font-family: inherit;
    text-align: center;
    cursor: pointer;
    border: 2px dashed;
    border-radius: 8px;
    transition: all 0.2s ease;

    &:hover {
      opacity: 0.9;
    }
  }

  .hidden-file-input {
    display: none;
  }

  .upload-icon {
    margin-bottom: 8px;
    font-size: 36px;
  }

  .drop-text {
    margin: 0;
    font-weight: 500;
  }

  .file-info-badge {
    display: inline-flex;
    gap: 8px;
    align-items: center;
    font-weight: 600;
  }

  .mt-16 {
    margin-top: 16px;
  }

  .mb-16 {
    margin-bottom: 16px;
  }

  .row-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .d-flex {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .ai-loading {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .submitting-overlay {
    padding: 16px;
    margin-top: 16px;
    text-align: center;
  }

  @keyframes fade-in {
    from {
      opacity: 0;
      transform: translateY(4px);
    }

    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

</style>
