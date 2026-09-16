<template>

  <KModal
    :title="isQuizMode ? modalQuizTitle$() : modalTitle$()"
    :submitText="isQuizMode ? saveQuizAction$() : saveAction$()"
    :cancelText="cancelAction$()"
    :submitDisabled="isSubmitDisabled || isSubmitting"
    size="large"
    @submit="handleSubmit"
    @cancel="$emit('close')"
  >
    <div class="interactive-activity-creator-modal">
      <!-- Target Assignment Selection -->
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
          {{ isQuizMode ? assignmentTargetQuizTitle$() : assignmentTargetTitle$() }}
        </h3>
        <p :style="{ margin: '0 0 12px', color: $themeTokens.annotation, fontSize: '0.9rem' }">
          {{ isQuizMode ? assignmentTargetQuizSubtitle$() : assignmentTargetSubtitle$() }}
        </p>

        <div
          v-if="!isQuizMode"
          class="target-select-row"
        >
          <KSelect
            v-model="selectedTargetOption"
            :label="targetLessonLabel$()"
            :options="targetOptions"
            :inline="true"
          />
        </div>

        <div
          v-if="isCreatingNewTarget || isQuizMode"
          class="mt-12"
        >
          <KTextbox
            v-model="newTargetTitle"
            :label="isQuizMode ? newQuizTitleLabel$() : newLessonTitleLabel$()"
            :placeholder="isQuizMode ? newQuizTitlePlaceholder$() : newLessonTitlePlaceholder$()"
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
  import { useRouter, useRoute } from 'vue-router/composables';
  import client from 'kolibri/client';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useSnackbar from 'kolibri/composables/useSnackbar';
  import LessonResource from 'kolibri-common/apiResources/LessonResource';
  import ExamResource from 'kolibri-common/apiResources/ExamResource';
  import H5PActivityBuilder from '../lessons/LessonSummaryPage/H5PActivityBuilder';
  import { PageNames } from '../../constants';

  const strings = createTranslator('InteractiveActivityCreatorModalStrings', {
    modalTitle: {
      message: 'Create Interactive Activity',
      context: 'Modal header title',
    },
    modalQuizTitle: {
      message: 'Create Interactive Quiz Activity',
      context: 'Modal header title when creating a quiz',
    },
    saveAction: {
      message: 'Save & Assign Activity',
      context: 'Submit button',
    },
    saveQuizAction: {
      message: 'Save & Assign Quiz',
      context: 'Submit button when creating a quiz',
    },
    cancelAction: {
      message: 'Cancel',
      context: 'Cancel button',
    },
    assignmentTargetTitle: {
      message: 'Lesson Assignment',
      context: 'Section title',
    },
    assignmentTargetQuizTitle: {
      message: 'Quiz Assignment',
      context: 'Section title when assigning to quiz',
    },
    assignmentTargetSubtitle: {
      message: 'Choose whether to assign this interactive activity to an existing lesson or create a new lesson.',
      context: 'Section subtitle',
    },
    assignmentTargetQuizSubtitle: {
      message: 'Choose whether to assign this interactive activity as a new quiz or add to an existing quiz.',
      context: 'Section subtitle when assigning to quiz',
    },
    targetLessonLabel: {
      message: 'Assign To',
      context: 'Dropdown label',
    },
    newLessonOptionLabel: {
      message: '+ Create as New Lesson',
      context: 'Dropdown option to create a new lesson',
    },
    newQuizOptionLabel: {
      message: '+ Create as New Quiz',
      context: 'Dropdown option to create a new quiz',
    },
    newLessonTitleLabel: {
      message: 'New Lesson Title (Optional)',
      context: 'Textbox label',
    },
    newQuizTitleLabel: {
      message: 'New Quiz Title (Optional)',
      context: 'Textbox label for new quiz title',
    },
    newLessonTitlePlaceholder: {
      message: 'Leave blank to use the activity title',
      context: 'Textbox placeholder',
    },
    newQuizTitlePlaceholder: {
      message: 'Leave blank to use the activity title',
      context: 'Textbox placeholder for new quiz title',
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
    quizSuccessNotice: {
      message: 'Interactive quiz successfully created and assigned!',
      context: 'Snackbar success message for quiz',
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
      quizzes: {
        type: Array,
        default: () => [],
      },
      isQuizMode: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['close', 'created'],
    setup(props, { emit }) {
      const router = useRouter();
      const route = useRoute();
      const { createSnackbar } = useSnackbar();

      const effectiveClassId = computed(() => {
        return (
          props.classId ||
          (route && route.params && route.params.classId) ||
          ''
        );
      });

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

      let savingTimeout = null;
      function clearSavingTimeout() {
        if (savingTimeout) {
          clearTimeout(savingTimeout);
          savingTimeout = null;
        }
      }

      function getUniqueQuizTitle(baseTitle) {
        const title = (baseTitle || '').trim() || 'Interactive Quiz';
        const existingTitles = new Set(
          (props.quizzes || []).map(q => (q.title || '').trim().toLowerCase()),
        );
        if (!existingTitles.has(title.toLowerCase())) {
          return title;
        }
        let counter = 2;
        while (existingTitles.has(`${title.toLowerCase()} (${counter})`)) {
          counter++;
        }
        return `${title} (${counter})`;
      }

      function getH5PEditorTitle() {
        try {
          if (h5pEditorIframe.value && h5pEditorIframe.value.contentWindow) {
            const doc = h5pEditorIframe.value.contentWindow.document;
            const editorIframe = doc.querySelector('.h5p-editor-iframe');
            const targetDoc = (editorIframe && editorIframe.contentDocument) || doc;
            const titleInput = targetDoc.querySelector(
              '.h5p-metadata-title input, input.h5peditor-text, input[name="title"], #h5peditor-uploader-title',
            );
            if (titleInput && titleInput.value && titleInput.value.trim()) {
              return titleInput.value.trim();
            }
          }
        } catch (e) {}
        return '';
      }

      function extractErrorMessage(err) {
        let detailMsg = '';
        const errData =
          (err && err.response && err.response.data) ||
          (err && err.data) ||
          (err && err.message) ||
          err;

        if (typeof errData === 'string') {
          detailMsg = errData;
        } else if (errData && errData.detail) {
          detailMsg = errData.detail;
        } else if (Array.isArray(errData) && errData.length > 0) {
          const first = errData[0];
          detailMsg = first.metadata?.message || first.message || JSON.stringify(first);
        } else if (errData && typeof errData === 'object') {
          const firstKey = Object.keys(errData)[0];
          const val = errData[firstKey];
          detailMsg = `${firstKey}: ${Array.isArray(val) ? val[0] : val}`;
        }
        return detailMsg || strings.errorNotice$();
      }

      function reloadH5PEditor() {
        isIframeLoading.value = true;
        h5pEditorUrl.value = `/h5p/new?t=${Date.now()}`;
      }

      function onIframeLoaded() {
        setTimeout(() => {
          isIframeLoading.value = false;
        }, 3000);
      }

      function generateHexId() {
        return 'xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx'.replace(/[xy]/g, c => {
          const r = (Math.random() * 16) | 0;
          const v = c === 'x' ? r : (r & 0x3) | 0x8;
          return v.toString(16);
        });
      }

      // Target selection (Lesson vs Quiz)
      const newTargetTitle = ref('');
      const targetOptions = computed(() => {
        if (props.isQuizMode) {
          return [{ label: strings.newQuizOptionLabel$(), value: '__new__' }];
        }
        const list = [{ label: strings.newLessonOptionLabel$(), value: '__new__' }];
        if (props.lessons && props.lessons.length) {
          props.lessons.forEach(l => {
            list.push({ label: l.title, value: l.id });
          });
        }
        return list;
      });

      const selectedTargetOption = ref(targetOptions.value[0]);

      const isCreatingNewTarget = computed(() => {
        return (
          selectedTargetOption.value && selectedTargetOption.value.value === '__new__'
        );
      });

      async function saveQuizFromQuestions(quizTitle, questions) {
        const rawTitle = newTargetTitle.value.trim() || quizTitle || 'Interactive Quiz';
        const finalTitle = getUniqueQuizTitle(rawTitle);
        const cid = effectiveClassId.value;

        if (!cid) {
          createSnackbar('Class ID is required to create a quiz.');
          isSubmitting.value = false;
          isSavingH5P.value = false;
          return;
        }

        const newExam = await ExamResource.saveModel({
          data: {
            title: finalTitle,
            collection: cid,
            assignments: [cid],
            active: true,
            draft: false,
            data_model_version: 3,
            question_sources: [
              {
                section_title: 'Section 1',
                description: '',
                questions,
              },
            ],
          },
        });

        createSnackbar(strings.quizSuccessNotice$());
        emit('created', { quizId: newExam.id });
        emit('close');

        if (router) {
          router.push({
            name: PageNames.EXAM_SUMMARY,
            params: {
              classId: cid,
              quizId: newExam.id,
            },
          });
        }
      }

      async function handleH5PContentSaved(contentId, title) {
        isSavingH5P.value = true;
        try {
          const activityTitle = title ? title.trim() : 'H5P Interactive Activity';

          if (props.isQuizMode) {
            let fileUrl = '';
            let bundleContent = '';
            let fileSize = 0;
            try {
              const exportRes = await client({
                url: '/api/exams/exam/export_h5p/',
                method: 'POST',
                data: {
                  h5p_content_id: String(contentId),
                  title: activityTitle,
                },
              });
              if (exportRes && exportRes.data) {
                fileUrl = exportRes.data.file_url || '';
                bundleContent = exportRes.data.content || '';
                fileSize = exportRes.data.file_size || 0;
              }
            } catch (exportErr) {
              // Fallback to dynamic player URL if export fails
            }

            const exerciseId = generateHexId();
            const qId = generateHexId();
            const q = {
              item: `${exerciseId}:${qId}`,
              exercise_id: exerciseId,
              question_id: qId,
              title: activityTitle,
              counter_in_exercise: 1,
              is_custom: true,
              question_type: 'h5p',
              h5p_content_id: String(contentId),
              h5p_url: `/h5p/play/${contentId}`,
              file_url: fileUrl,
              file_size: fileSize,
              content: bundleContent,
              prompt: activityTitle,
              options: [],
              answer_key: [],
              point_value: 10,
            };
            await saveQuizFromQuestions(activityTitle, [q]);
            return;
          }

          let targetLessonId;
          if (isCreatingNewTarget.value) {
            const finalLessonTitle =
              newTargetTitle.value.trim() || activityTitle || 'Interactive Lesson';

            const newLesson = await LessonResource.saveModel({
              data: {
                title: finalLessonTitle,
                collection: effectiveClassId.value,
                assignments: [effectiveClassId.value],
                active: true,
                resources: [],
              },
            });
            targetLessonId = newLesson.id;
          } else {
            targetLessonId = selectedTargetOption.value.value;
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

          if (isCreatingNewTarget.value && router) {
            router.push({
              name: PageNames.LESSON_SUMMARY,
              params: {
                classId: effectiveClassId.value,
                lessonId: targetLessonId,
              },
            });
          }
        } catch (err) {
          createSnackbar(extractErrorMessage(err));
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
            clearSavingTimeout();
            handleH5PContentSaved(event.data.contentId, event.data.title);
          } else if (event.data.type === 'KOLIBRI_H5P_VALIDATION_ERROR') {
            clearSavingTimeout();
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
        clearSavingTimeout();
        window.removeEventListener('message', onWindowMessage);
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
                const extracted = getH5PEditorTitle();
                if (extracted && !newTargetTitle.value) {
                  newTargetTitle.value = extracted;
                }
                isSubmitting.value = true;
                clearSavingTimeout();
                savingTimeout = setTimeout(() => {
                  if (isSubmitting.value) {
                    isSubmitting.value = false;
                    isSavingH5P.value = false;
                    createSnackbar(strings.errorNotice$());
                  }
                }, 25000);
                saveBtn.click();
                return;
              }
            } catch (e) {
              isSubmitting.value = false;
              createSnackbar(extractErrorMessage(e));
            }
          }
          return;
        }

        isSubmitting.value = true;
        try {
          const activityTitle =
            h5pMode.value === 'create'
              ? activityBuilderRef.value.title.trim()
              : h5pTitle.value.trim();

          if (props.isQuizMode) {
            if (h5pMode.value === 'create') {
              const builder = activityBuilderRef.value;
              let questions = [];

              if (builder.selectedType.value === 'quiz') {
                questions = (builder.questions || []).map((bq, idx) => {
                  const exerciseId = generateHexId();
                  const qId = generateHexId();
                  if (bq.type.value === 'true_false') {
                    const optTrueId = `opt_${generateHexId().substring(0, 8)}`;
                    const optFalseId = `opt_${generateHexId().substring(0, 8)}`;
                    return {
                      item: `${exerciseId}:${qId}`,
                      exercise_id: exerciseId,
                      question_id: qId,
                      title: `Question ${idx + 1}`,
                      counter_in_exercise: 1,
                      is_custom: true,
                      question_type: 'true_false',
                      prompt: bq.prompt || `True or False Question ${idx + 1}`,
                      options: [
                        { id: optTrueId, text: 'True', image: '' },
                        { id: optFalseId, text: 'False', image: '' },
                      ],
                      answer_key: [bq.tfAnswer === true ? optTrueId : optFalseId],
                      point_value: 1,
                      explanation: bq.explanation || '',
                      case_sensitive: false,
                    };
                  } else if (bq.type.value === 'fill_blank') {
                    return {
                      item: `${exerciseId}:${qId}`,
                      exercise_id: exerciseId,
                      question_id: qId,
                      title: `Question ${idx + 1}`,
                      counter_in_exercise: 1,
                      is_custom: true,
                      question_type: 'short_answer',
                      prompt: bq.prompt || bq.blankText || `Fill in the blank ${idx + 1}`,
                      options: [],
                      answer_key: [bq.blankAnswer || ''],
                      point_value: 1,
                      explanation: bq.explanation || '',
                      case_sensitive: false,
                    };
                  } else {
                    const opts = (bq.options || []).map((opt, oIdx) => ({
                      id: `opt_${generateHexId().substring(0, 8)}`,
                      text: opt.text || `Option ${oIdx + 1}`,
                      image: '',
                      _isCorrect: opt.isCorrect,
                    }));
                    const answerKey = opts.filter(o => o._isCorrect).map(o => o.id);
                    return {
                      item: `${exerciseId}:${qId}`,
                      exercise_id: exerciseId,
                      question_id: qId,
                      title: `Question ${idx + 1}`,
                      counter_in_exercise: 1,
                      is_custom: true,
                      question_type: 'multiple_choice',
                      prompt: bq.prompt || `Question ${idx + 1}`,
                      options: opts.map(({ id, text, image }) => ({ id, text, image })),
                      answer_key: answerKey.length > 0 ? answerKey : (opts[0] ? [opts[0].id] : []),
                      point_value: 1,
                      explanation: bq.explanation || '',
                      case_sensitive: false,
                    };
                  }
                });
              } else {
                const exerciseId = generateHexId();
                const qId = generateHexId();
                questions = [
                  {
                    item: `${exerciseId}:${qId}`,
                    exercise_id: exerciseId,
                    question_id: qId,
                    title: activityTitle,
                    counter_in_exercise: 1,
                    is_custom: true,
                    question_type: 'interactive',
                    content: builder.compiledHtml,
                    prompt: activityTitle,
                    options: [],
                    answer_key: [],
                    point_value: 10,
                  },
                ];
              }

              await saveQuizFromQuestions(activityTitle, questions);
              return;
            } else {
              // Upload .h5p file for quiz
              const formData = new FormData();
              formData.append('file', selectedH5PFile.value);

              const resp = await client({
                url: '/api/exams/exam/upload_h5p/',
                method: 'POST',
                data: formData,
                headers: { 'Content-Type': 'multipart/form-data' },
              });

              const { file_url, file_size } = resp.data;
              const exerciseId = generateHexId();
              const qId = generateHexId();
              const questions = [
                {
                  item: `${exerciseId}:${qId}`,
                  exercise_id: exerciseId,
                  question_id: qId,
                  title: activityTitle,
                  counter_in_exercise: 1,
                  is_custom: true,
                  question_type: 'h5p',
                  file_url: file_url,
                  file_size: file_size || 0,
                  prompt: activityTitle,
                  description: h5pDescription.value.trim(),
                  options: [],
                  answer_key: [],
                  point_value: 10,
                },
              ];

              await saveQuizFromQuestions(activityTitle, questions);
              return;
            }
          }

          let targetLessonId;
          if (isCreatingNewTarget.value) {
            const finalLessonTitle =
              newTargetTitle.value.trim() || activityTitle || 'Interactive Lesson';

            const newLesson = await LessonResource.saveModel({
              data: {
                title: finalLessonTitle,
                collection: effectiveClassId.value,
                assignments: [effectiveClassId.value],
                active: true,
                resources: [],
              },
            });
            targetLessonId = newLesson.id;
          } else {
            targetLessonId = selectedTargetOption.value.value;
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

          if (isCreatingNewTarget.value && router) {
            router.push({
              name: PageNames.LESSON_SUMMARY,
              params: {
                classId: effectiveClassId.value,
                lessonId: targetLessonId,
              },
            });
          }
        } catch (err) {
          createSnackbar(extractErrorMessage(err));
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
        newTargetTitle,
        targetOptions,
        selectedTargetOption,
        isCreatingNewTarget,
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
