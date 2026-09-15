<template>

  <KModal
    :title="modalTitle$()"
    :submitText="saveAction$()"
    :cancelText="cancelAction$()"
    :submitDisabled="isSubmitDisabled || isSubmitting"
    size="large"
    @submit="handleSubmit"
    @cancel="$emit('close')"
  >
    <div class="interactive-activity-creator-modal">
      <!-- Target Lesson Selection -->
      <div
        class="lesson-target-bar mb-16"
        :style="{
          backgroundColor: $themePalette.grey.v_100,
          border: `1px solid ${$themeTokens.fineLine}`,
          borderRadius: '8px',
          padding: '16px',
        }"
      >
        <h3 :style="{ margin: '0 0 8px', color: $themeTokens.text }">
          {{ assignmentTargetTitle$() }}
        </h3>
        <p :style="{ margin: '0 0 12px', color: $themeTokens.annotation, fontSize: '0.9rem' }">
          {{ assignmentTargetSubtitle$() }}
        </p>

        <div class="target-select-row">
          <KSelect
            v-model="selectedLessonOption"
            :label="targetLessonLabel$()"
            :options="lessonOptions"
            :inline="true"
          />
        </div>

        <div
          v-if="isCreatingNewLesson"
          class="mt-12"
        >
          <KTextbox
            v-model="newLessonTitle"
            :label="newLessonTitleLabel$()"
            :placeholder="newLessonTitlePlaceholder$()"
          />
        </div>
      </div>

      <!-- Mode Selector: Studio vs Quick Templates vs Upload .h5p -->
      <div
        class="mode-selector mb-16"
        :style="{
          display: 'flex',
          gap: '8px',
          borderBottom: `1px solid ${$themeTokens.fineLine}`,
          paddingBottom: '12px',
        }"
      >
        <KButton
          :text="h5pStudioModeLabel$()"
          icon="html5"
          :appearance="h5pMode === 'hub' ? 'raised-button' : 'flat-button'"
          :primary="h5pMode === 'hub'"
          @click="h5pMode = 'hub'"
        />
        <KButton
          :text="h5pQuickModeLabel$()"
          icon="plus"
          :appearance="h5pMode === 'create' ? 'raised-button' : 'flat-button'"
          :primary="h5pMode === 'create'"
          @click="h5pMode = 'create'"
        />
        <KButton
          :text="uploadH5PModeLabel$()"
          icon="document"
          :appearance="h5pMode === 'upload' ? 'raised-button' : 'flat-button'"
          :primary="h5pMode === 'upload'"
          @click="h5pMode = 'upload'"
        />
      </div>

      <!-- Mode A: Official H5P Authoring Studio (All 50+ Types) -->
      <div
        v-if="h5pMode === 'hub'"
        class="h5p-hub-studio-wrapper"
      >
        <div
          class="h5p-hub-header-banner"
          :style="{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: $themePalette.grey.v_100,
            border: `1px solid ${$themeTokens.fineLine}`,
            borderRadius: '6px',
            padding: '10px 16px',
            marginBottom: '12px',
          }"
        >
          <div>
            <h4 :style="{ margin: '0 0 2px', color: $themeTokens.text }">
              {{ h5pStudioHeaderTitle$() }}
            </h4>
            <p :style="{ margin: 0, color: $themeTokens.annotation, fontSize: '0.85rem' }">
              {{ h5pStudioHeaderSubtitle$() }}
            </p>
          </div>
          <KButton
            :text="refreshStudioLabel$()"
            icon="refresh"
            appearance="flat-button"
            @click="reloadH5PEditor"
          />
        </div>

        <div
          v-if="isSavingH5P"
          class="h5p-saving-banner"
          :style="{
            textAlign: 'center',
            padding: '20px',
            backgroundColor: $themeTokens.surface,
            borderRadius: '8px',
            border: `1px solid ${$themeTokens.fineLine}`,
            marginBottom: '12px',
          }"
        >
          <KCircularLoader :delay="false" />
          <p :style="{ marginTop: '8px', fontWeight: 'bold', color: $themeTokens.text }">
            {{ savingNotice$() }}
          </p>
        </div>

        <div
          class="h5p-studio-container"
          style="position: relative; width: 100%; min-height: 720px;"
        >
          <div
            v-if="isIframeLoading"
            class="h5p-loading-banner"
            :style="{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 10,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: $themeTokens.surface,
              borderRadius: '8px',
              border: `1px solid ${$themeTokens.fineLine}`,
            }"
          >
            <KCircularLoader :delay="false" />
            <p :style="{ marginTop: '16px', fontWeight: '500', color: $themeTokens.annotation }">
              {{ h5pLoadingNotice$() }}
            </p>
          </div>

          <iframe
            ref="h5pEditorIframe"
            :src="h5pEditorUrl"
            class="h5p-hub-iframe"
            style="width: 100%; height: 720px; border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff;"
            allow="fullscreen; geolocation; microphone; camera; midi"
            @load="onIframeLoaded"
          ></iframe>
        </div>
      </div>

      <!-- Mode B: Quick Activity Builder -->
      <div v-else-if="h5pMode === 'create'">
        <H5PActivityBuilder ref="activityBuilderRef" />
      </div>

      <!-- Mode C: Upload .h5p File -->
      <div v-else>
        <p :style="{ color: $themeTokens.annotation }">
          {{ h5pUploadDesc$() }}
        </p>

        <button
          type="button"
          class="drop-zone"
          :style="{
            borderColor: selectedH5PFile ? $themeTokens.primary : $themeTokens.fineLine,
            backgroundColor: selectedH5PFile ? $themePalette.grey.v_100 : $themeTokens.surface,
          }"
          @click="triggerFileInput"
        >
          <input
            ref="h5pInput"
            type="file"
            class="hidden-file-input"
            :aria-label="selectH5PPrompt$()"
            accept=".h5p,.zip"
            @change="onFileSelected"
          >
          <KIcon
            icon="html5"
            class="upload-icon"
          />
          <p
            v-if="!selectedH5PFile"
            class="drop-text"
          >
            {{ selectH5PPrompt$() }}
          </p>
          <div
            v-else
            class="file-info-badge"
          >
            <span class="file-name">{{ selectedH5PFile.name }}</span>
            <span
              class="file-size"
              :style="{ color: $themeTokens.annotation }"
            >
              ({{ formatFileSize(selectedH5PFile.size) }})
            </span>
          </div>
        </button>

        <div
          v-if="selectedH5PFile"
          class="mt-16"
        >
          <KTextbox
            v-model="h5pTitle"
            :label="titleLabel$()"
            class="mb-16"
          />
          <KTextbox
            v-model="h5pDescription"
            :label="descriptionLabel$()"
            :textArea="true"
            class="mb-16"
          />
        </div>
      </div>

      <!-- Submitting Overlay -->
      <div
        v-if="isSubmitting"
        class="submitting-overlay"
      >
        <KCircularLoader :delay="false" />
        <p>{{ savingNotice$() }}</p>
      </div>
    </div>
  </KModal>

</template>


<script>

  import { ref, computed, onMounted, onUnmounted } from 'vue';
  import { useRouter } from 'vue-router/composables';
  import client from 'kolibri/client';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useSnackbar from 'kolibri/composables/useSnackbar';
  import LessonResource from 'kolibri-common/apiResources/LessonResource';
  import H5PActivityBuilder from '../lessons/LessonSummaryPage/H5PActivityBuilder';
  import { PageNames } from '../../constants';

  const strings = createTranslator('InteractiveActivityCreatorModalStrings', {
    modalTitle: {
      message: 'Create Interactive Activity',
      context: 'Modal header title',
    },
    saveAction: {
      message: 'Save & Assign Activity',
      context: 'Submit button',
    },
    cancelAction: {
      message: 'Cancel',
      context: 'Cancel button',
    },
    assignmentTargetTitle: {
      message: 'Lesson Assignment',
      context: 'Section title',
    },
    assignmentTargetSubtitle: {
      message: 'Choose whether to assign this interactive activity to an existing lesson or create a new lesson.',
      context: 'Section subtitle',
    },
    targetLessonLabel: {
      message: 'Assign To',
      context: 'Dropdown label',
    },
    newLessonOptionLabel: {
      message: '+ Create as New Lesson',
      context: 'Dropdown option to create a new lesson',
    },
    newLessonTitleLabel: {
      message: 'New Lesson Title (Optional)',
      context: 'Textbox label',
    },
    newLessonTitlePlaceholder: {
      message: 'Leave blank to use the activity title',
      context: 'Textbox placeholder',
    },
    h5pStudioModeLabel: {
      message: 'H5P Interactive Studio',
      context: 'Button label for full H5P Hub studio mode',
    },
    h5pQuickModeLabel: {
      message: 'Quick Templates',
      context: 'Button label for quick built-in templates',
    },
    h5pStudioHeaderTitle: {
      message: 'H5P Interactive Authoring Studio',
      context: 'Header title for H5P Hub',
    },
    h5pStudioHeaderSubtitle: {
      message: 'Visually author, configure, and assign any official interactive activity type.',
      context: 'Header subtitle for H5P Hub',
    },
    refreshStudioLabel: {
      message: 'Reset Studio',
      context: 'Button label to reload the studio iframe',
    },
    createInteractiveModeLabel: {
      message: 'In-System Activity Creator',
      context: 'Mode button label',
    },
    uploadH5PModeLabel: {
      message: 'Upload .h5p File',
      context: 'Mode button label',
    },
    h5pUploadDesc: {
      message: 'Upload an interactive .h5p activity file to assign to your learners.',
      context: 'Upload description',
    },
    selectH5PPrompt: {
      message: 'Click or drop a .h5p file here',
      context: 'File drop area text',
    },
    titleLabel: {
      message: 'Activity Title',
      context: 'Form label',
    },
    descriptionLabel: {
      message: 'Description (Optional)',
      context: 'Form label',
    },
    savingNotice: {
      message: 'Saving interactive activity...',
      context: 'Loading text',
    },
    h5pLoadingNotice: {
      message: 'Loading H5P Interactive Studio...',
      context: 'Loading text displayed while the interactive studio initializes',
    },
    validationPrompt: {
      message: 'Please select an interactive activity type and fill in the required fields before saving.',
      context: 'Snackbar warning when user attempts to save without selecting an activity',
    },
    successNotice: {
      message: 'Interactive activity successfully created and assigned!',
      context: 'Snackbar success message',
    },
    errorNotice: {
      message: 'Could not create activity. Please check inputs and try again.',
      context: 'Snackbar error message',
    },
    fileSizeExceededWarning: {
      message: 'File size ({size}) exceeds the 20MB maximum limit. Please choose a smaller file.',
      context: 'Warning message for large files',
    },
  });

  export default {
    name: 'InteractiveActivityCreatorModal',
    components: {
      H5PActivityBuilder,
    },
    props: {
      classId: {
        type: String,
        required: true,
      },
      lessons: {
        type: Array,
        default: () => [],
      },
    },
    emits: ['close', 'created'],
    setup(props, { emit }) {
      const router = useRouter();
      const { createSnackbar } = useSnackbar();

      const h5pMode = ref('hub');
      const activityBuilderRef = ref(null);
      const isSubmitting = ref(false);

      // Upload file state
      const selectedH5PFile = ref(null);
      const h5pTitle = ref('');
      const h5pDescription = ref('');
      const h5pInput = ref(null);

      // H5P Hub Studio state
      const h5pEditorIframe = ref(null);
      const isSavingH5P = ref(false);
      const isIframeLoading = ref(true);
      const h5pEditorUrl = ref('/h5p/new');

      function reloadH5PEditor() {
        isIframeLoading.value = true;
        h5pEditorUrl.value = `/h5p/new?t=${Date.now()}`;
      }

      function onIframeLoaded() {
        setTimeout(() => {
          isIframeLoading.value = false;
        }, 3000);
      }

      async function handleH5PContentSaved(contentId, title) {
        isSavingH5P.value = true;
        try {
          let targetLessonId;
          const activityTitle = title ? title.trim() : 'H5P Interactive Activity';

          if (isCreatingNewLesson.value) {
            const finalLessonTitle =
              newLessonTitle.value.trim() || activityTitle || 'Interactive Lesson';

            const newLesson = await LessonResource.saveModel({
              data: {
                title: finalLessonTitle,
                collection: props.classId,
                assignments: [props.classId],
                active: true,
                resources: [],
              },
            });
            targetLessonId = newLesson.id;
          } else {
            targetLessonId = selectedLessonOption.value.value;
          }

          const endpointUrl = `/api/lessons/lesson/${targetLessonId}/custom_resource/`;
          await client({
            url: endpointUrl,
            method: 'POST',
            data: {
              resource_type: 'h5p',
              h5p_content_id: String(contentId),
              title: activityTitle,
            },
          });

          createSnackbar(strings.successNotice$());
          emit('created', { lessonId: targetLessonId });
          emit('close');

          if (isCreatingNewLesson.value && router) {
            router.push({
              name: PageNames.LESSON_SUMMARY,
              params: {
                classId: props.classId,
                lessonId: targetLessonId,
              },
            });
          }
        } catch (err) {
          const detailMsg = err.response && err.response.data && err.response.data.detail;
          createSnackbar(detailMsg || strings.errorNotice$());
        } finally {
          isSavingH5P.value = false;
          isSubmitting.value = false;
        }
      }

      function onWindowMessage(event) {
        if (event.data) {
          if (event.data.type === 'KOLIBRI_H5P_READY') {
            isIframeLoading.value = false;
            try {
              if (h5pEditorIframe.value && h5pEditorIframe.value.contentWindow) {
                h5pEditorIframe.value.contentWindow.dispatchEvent(new Event('resize'));
              }
            } catch (e) {}
          } else if (event.data.type === 'KOLIBRI_H5P_SAVED') {
            handleH5PContentSaved(event.data.contentId, event.data.title);
          } else if (event.data.type === 'KOLIBRI_H5P_VALIDATION_ERROR') {
            isSubmitting.value = false;
            isSavingH5P.value = false;
            createSnackbar(event.data.message || strings.validationPrompt$());
          }
        }
      }

      onMounted(() => {
        window.addEventListener('message', onWindowMessage);
      });

      onUnmounted(() => {
        window.removeEventListener('message', onWindowMessage);
      });

      // Lesson target selection
      const newLessonTitle = ref('');
      const lessonOptions = computed(() => {
        const list = [
          { label: strings.newLessonOptionLabel$(), value: '__new__' },
        ];
        if (props.lessons && props.lessons.length) {
          props.lessons.forEach(l => {
            list.push({ label: l.title, value: l.id });
          });
        }
        return list;
      });

      const selectedLessonOption = ref(lessonOptions.value[0]);

      const isCreatingNewLesson = computed(() => {
        return selectedLessonOption.value && selectedLessonOption.value.value === '__new__';
      });

      const isSubmitDisabled = computed(() => {
        if (h5pMode.value === 'hub') {
          return false;
        }
        if (h5pMode.value === 'create') {
          return !activityBuilderRef.value || !activityBuilderRef.value.isValid;
        }
        return !selectedH5PFile.value || !h5pTitle.value.trim();
      });

      function formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
      }

      function triggerFileInput() {
        if (h5pInput.value) {
          h5pInput.value.click();
        }
      }

      function onFileSelected(event) {
        const file = event.target.files && event.target.files[0];
        if (!file) return;

        if (file.size > 20 * 1024 * 1024) {
          const warning = strings.fileSizeExceededWarning$({
            size: formatFileSize(file.size),
          });
          createSnackbar(warning);
          event.target.value = '';
          selectedH5PFile.value = null;
          return;
        }

        selectedH5PFile.value = file;
        if (!h5pTitle.value) {
          h5pTitle.value = file.name.replace(/\.[^/.]+$/, '');
        }
      }

      async function handleSubmit() {
        if (h5pMode.value === 'hub') {
          if (h5pEditorIframe.value && h5pEditorIframe.value.contentWindow) {
            try {
              const doc = h5pEditorIframe.value.contentWindow.document;

              // Check if an activity type has been selected or editor form is initialized
              const libraryInput = doc.querySelector('input[name="library"]');
              const editorIframe = doc.querySelector('.h5p-editor-iframe');
              const hasForm =
                editorIframe &&
                editorIframe.contentDocument &&
                editorIframe.contentDocument.querySelector('.h5peditor-form');

              if ((!libraryInput || !libraryInput.value) && !hasForm) {
                createSnackbar(strings.validationPrompt$());
                return;
              }

              const saveBtn = doc.querySelector('#save-h5p');
              if (saveBtn) {
                isSubmitting.value = true;
                saveBtn.click();
                return;
              }
            } catch (e) {
              isSubmitting.value = false;
              createSnackbar(strings.errorNotice$());
            }
          }
          return;
        }

        isSubmitting.value = true;
        try {
          let targetLessonId;
          const activityTitle =
            h5pMode.value === 'create'
              ? activityBuilderRef.value.title.trim()
              : h5pTitle.value.trim();

          if (isCreatingNewLesson.value) {
            const finalLessonTitle =
              newLessonTitle.value.trim() || activityTitle || 'Interactive Lesson';

            const newLesson = await LessonResource.saveModel({
              data: {
                title: finalLessonTitle,
                collection: props.classId,
                assignments: [props.classId],
                active: true,
                resources: [],
              },
            });
            targetLessonId = newLesson.id;
          } else {
            targetLessonId = selectedLessonOption.value.value;
          }

          const endpointUrl = `/api/lessons/lesson/${targetLessonId}/custom_resource/`;

          if (h5pMode.value === 'create') {
            const builder = activityBuilderRef.value;
            await client({
              url: endpointUrl,
              method: 'POST',
              data: {
                resource_type: 'h5p',
                title: builder.title.trim(),
                description: builder.description.trim(),
                content: builder.compiledHtml,
              },
            });
          } else {
            const formData = new FormData();
            formData.append('file', selectedH5PFile.value);
            formData.append('title', h5pTitle.value.trim());
            formData.append('description', h5pDescription.value.trim());
            formData.append('resource_type', 'h5p');

            await client({
              url: endpointUrl,
              method: 'POST',
              data: formData,
              headers: { 'Content-Type': 'multipart/form-data' },
            });
          }

          createSnackbar(strings.successNotice$());
          emit('created', { lessonId: targetLessonId });
          emit('close');

          if (isCreatingNewLesson.value && router) {
            router.push({
              name: PageNames.LESSON_SUMMARY,
              params: {
                classId: props.classId,
                lessonId: targetLessonId,
              },
            });
          }
        } catch (err) {
          const detailMsg = err.response && err.response.data && err.response.data.detail;
          createSnackbar(detailMsg || strings.errorNotice$());
        } finally {
          isSubmitting.value = false;
        }
      }

      return {
        h5pMode,
        activityBuilderRef,
        isSubmitting,
        selectedH5PFile,
        h5pTitle,
        h5pDescription,
        h5pInput,
        h5pEditorIframe,
        isSavingH5P,
        isIframeLoading,
        onIframeLoaded,
        h5pEditorUrl,
        reloadH5PEditor,
        newLessonTitle,
        lessonOptions,
        selectedLessonOption,
        isCreatingNewLesson,
        isSubmitDisabled,
        formatFileSize,
        triggerFileInput,
        onFileSelected,
        handleSubmit,
        ...strings,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .interactive-activity-creator-modal {
    position: relative;
    padding: 8px 0;
  }

  .target-select-row {
    max-width: 400px;
  }

  .drop-zone {
    width: 100%;
    padding: 40px 20px;
    border: 2px dashed #94a3b8;
    border-radius: 8px;
    text-align: center;
    cursor: pointer;
    background: transparent;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;

    &:hover {
      border-color: #0284c7;
      background-color: #f8fafc;
    }
  }

  .hidden-file-input {
    display: none;
  }

  .upload-icon {
    font-size: 40px;
    margin-bottom: 12px;
  }

  .drop-text {
    margin: 0;
    font-size: 1rem;
    font-weight: 500;
  }

  .file-info-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
  }

  .submitting-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.85);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 100;
    border-radius: 8px;
  }

  .mb-16 {
    margin-bottom: 16px;
  }

  .mt-12 {
    margin-top: 12px;
  }

  .mt-16 {
    margin-top: 16px;
  }

</style>
