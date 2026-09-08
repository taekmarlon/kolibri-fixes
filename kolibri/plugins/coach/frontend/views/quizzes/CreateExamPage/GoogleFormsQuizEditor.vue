<template>

  <div class="google-forms-quiz-editor">
    <!-- Header Bar -->
    <div
      class="editor-header-banner"
      :style="{
        backgroundColor: $themeTokens.surface,
        borderBottom: `2px solid ${$themeTokens.primary}`,
      }"
    >
      <div class="header-left">
        <h3 :style="{ color: $themeTokens.text, margin: 0 }">
          {{ authorCustomQuestionsTitle$() }}
        </h3>
        <p
          :style="{ color: $themeTokens.annotation, margin: '4px 0 0' }"
          class="subtitle"
        >
          {{ authorCustomQuestionsSubtitle$() }}
        </p>
      </div>
      <div class="header-right">
        <span
          class="stats-badge"
          :style="{
            backgroundColor: $themePalette.grey.v_200,
            color: $themeTokens.text,
          }"
        >
          {{ totalQuestionsText }} • {{ totalPointsText }}
        </span>
        <KButton
          :text="addQuestionAction$()"
          icon="plus"
          :primary="true"
          appearance="raised-button"
          @click="addNewQuestion"
        />
      </div>
    </div>

    <!-- Questions List with Reordering -->
    <div
      v-if="localQuestions.length === 0"
      class="empty-state-card"
      :style="{
        backgroundColor: $themeTokens.surface,
        borderColor: $themeTokens.fineLine,
      }"
    >
      <div
        class="empty-icon-circle"
        :style="{ backgroundColor: $themePalette.grey.v_100 }"
      >
        <KIcon
          icon="quiz"
          class="large-icon"
        />
      </div>
      <h4>{{ noQuestionsYet$() }}</h4>
      <p :style="{ color: $themeTokens.annotation }">
        {{ clickToAddFirstQuestion$() }}
      </p>
      <KButton
        :text="addQuestionAction$()"
        icon="plus"
        :primary="true"
        appearance="raised-button"
        @click="addNewQuestion"
      />
    </div>

    <div
      v-else
      class="questions-cards-container"
    >
      <div
        v-for="(question, qIndex) in localQuestions"
        :key="question.item || `q-${qIndex}`"
        class="question-block-card"
        :class="{ 'is-active': activeQuestionIndex === qIndex }"
        :style="{
          backgroundColor: $themeTokens.surface,
          borderColor: activeQuestionIndex === qIndex ? $themeTokens.primary : $themeTokens.fineLine,
          borderLeft:
            activeQuestionIndex === qIndex
              ? `6px solid ${$themeTokens.primary}`
              : `1px solid ${$themeTokens.fineLine}`,
        }"
        @click="activeQuestionIndex = qIndex"
      >
        <!-- Card Top Bar: Drag & Order Controls -->
        <div
          class="card-top-bar"
          :style="{ borderBottom: `1px solid ${$themePalette.grey.v_200}` }"
        >
          <div class="order-controls">
            <span
              class="question-number-pill"
              :style="{
                backgroundColor:
                  activeQuestionIndex === qIndex
                    ? $themeTokens.primary
                    : $themePalette.grey.v_300,
                color:
                  activeQuestionIndex === qIndex ? $themeTokens.textInverted : $themeTokens.text,
              }"
            >
              {{ qIndex + 1 }}
            </span>
            <KIconButton
              icon="back"
              class="rotate-up"
              :ariaLabel="moveUpAction$()"
              :tooltip="moveUpAction$()"
              :disabled="qIndex === 0"
              size="small"
              @click.stop="moveQuestionUp(qIndex)"
            />
            <KIconButton
              icon="forward"
              class="rotate-down"
              :ariaLabel="moveDownAction$()"
              :tooltip="moveDownAction$()"
              :disabled="qIndex === localQuestions.length - 1"
              size="small"
              @click.stop="moveQuestionDown(qIndex)"
            />
          </div>

          <!-- Question Type Dropdown -->
          <div class="type-selector-wrapper">
            <select
              v-model="question.question_type"
              class="question-type-select"
              :style="{
                borderColor: $themeTokens.fineLine,
                backgroundColor: $themeTokens.surface,
                color: $themeTokens.text,
              }"
              @change="handleQuestionTypeChange(question)"
            >
              <option value="multiple_choice">
                {{ multipleChoiceLabel$() }}
              </option>
              <option value="checkboxes">
                {{ checkboxesLabel$() }}
              </option>
              <option value="short_answer">
                {{ shortAnswerLabel$() }}
              </option>
              <option value="true_false">
                {{ trueFalseLabel$() }}
              </option>
            </select>
          </div>
        </div>

        <!-- Question Prompt Row -->
        <div class="prompt-section">
          <div class="prompt-input-row">
            <KTextbox
              v-model="question.prompt"
              :label="questionPromptLabel$()"
              :placeholder="enterPromptPlaceholder$()"
              class="prompt-textbox"
              :textArea="true"
              rows="2"
              @input="onQuestionChange"
            />
            <div class="prompt-image-action">
              <KIconButton
                icon="image"
                :tooltip="uploadPromptImage$()"
                :ariaLabel="uploadPromptImage$()"
                @click.stop="triggerPromptImageUpload(question)"
              />
            </div>
          </div>

          <!-- Prompt Image Preview -->
          <div
            v-if="question.prompt_image"
            class="image-preview-box mt-8"
          >
            <img
              :src="question.prompt_image"
              alt="Prompt image"
              class="preview-img"
            >
            <KIconButton
              icon="clear"
              class="remove-image-btn"
              :tooltip="removeImage$()"
              :ariaLabel="removeImage$()"
              @click.stop="removePromptImage(question)"
            />
          </div>
        </div>

        <!-- Options Section for Multiple Choice / Checkboxes / True-False -->
        <div
          v-if="question.question_type !== 'short_answer'"
          class="options-container"
        >
          <div
            v-for="(option, optIndex) in question.options"
            :key="option.id || `opt-${optIndex}`"
            class="option-row"
          >
            <!-- Answer Key Toggle (Radio or Checkbox) -->
            <button
              type="button"
              class="answer-key-indicator"
              :title="markAsCorrectAnswer$()"
              @click.stop="toggleOptionAnswer(question, option)"
            >
              <KIcon
                v-if="question.question_type === 'multiple_choice' || question.question_type === 'true_false'"
                :icon="isOptionCorrect(question, option) ? 'radio_button_checked' : 'radio_button_unchecked'"
                :style="{
                  color: isOptionCorrect(question, option) ? '#16a34a' : $themeTokens.annotation,
                }"
              />
              <KIcon
                v-else
                :icon="isOptionCorrect(question, option) ? 'check_box' : 'check_box_outline_blank'"
                :style="{
                  color: isOptionCorrect(question, option) ? '#16a34a' : $themeTokens.annotation,
                }"
              />
            </button>

            <!-- Option Text -->
            <div class="option-text-field">
              <input
                v-model="option.text"
                type="text"
                class="option-input"
                :placeholder="`${optionPlaceholder$()} ${optIndex + 1}`"
                :disabled="question.question_type === 'true_false'"
                :style="{
                  borderColor: isOptionCorrect(question, option) ? '#16a34a' : $themeTokens.fineLine,
                  backgroundColor: $themeTokens.surface,
                  color: $themeTokens.text,
                }"
                @input="onQuestionChange"
              >
            </div>

            <!-- Option Image Upload -->
            <div class="option-image-action">
              <KIconButton
                icon="image"
                size="small"
                :tooltip="uploadOptionImage$()"
                :ariaLabel="uploadOptionImage$()"
                @click.stop="triggerOptionImageUpload(option)"
              />
            </div>

            <!-- Delete Option Button (disabled for True/False or when only 2 options) -->
            <KIconButton
              v-if="question.question_type !== 'true_false'"
              icon="clear"
              size="small"
              :tooltip="removeOption$()"
              :ariaLabel="removeOption$()"
              :disabled="question.options.length <= 2"
              @click.stop="removeOption(question, optIndex)"
            />

            <!-- Option Image Preview -->
            <div
              v-if="option.image"
              class="option-image-preview"
            >
              <img
                :src="option.image"
                alt="Choice image"
                class="option-thumb"
              >
              <KIconButton
                icon="clear"
                size="small"
                class="remove-opt-img"
                :tooltip="removeImage$()"
                :ariaLabel="removeImage$()"
                @click.stop="removeOptionImage(option)"
              />
            </div>
          </div>

          <!-- Add Option Button -->
          <div
            v-if="question.question_type !== 'true_false'"
            class="add-option-row mt-8"
          >
            <KButton
              :text="addOptionAction$()"
              icon="plus"
              appearance="flat-button"
              @click.stop="addOption(question)"
            />
          </div>
        </div>

        <!-- Short Answer Configuration -->
        <div
          v-else
          class="short-answer-container"
        >
          <p :style="{ color: $themeTokens.annotation, margin: '8px 0' }">
            {{ shortAnswerHelp$() }}
          </p>
          <div class="short-answer-inputs">
            <KTextbox
              :value="(question.answer_key || []).join(', ')"
              :label="correctAnswersLabel$()"
              :placeholder="correctAnswersPlaceholder$()"
              @input="val => updateShortAnswerKeys(question, val)"
            />
            <div class="case-toggle mt-8">
              <KCheckbox
                v-model="question.case_sensitive"
                :label="caseSensitiveLabel$()"
                @change="onQuestionChange"
              />
            </div>
          </div>
        </div>

        <!-- Card Bottom Settings: Points, Explanation, Duplicate, Delete -->
        <div
          class="card-bottom-bar"
          :style="{ borderTop: `1px solid ${$themePalette.grey.v_200}` }"
        >
          <div class="bottom-left-settings">
            <div class="points-field">
              <label :style="{ color: $themeTokens.annotation, marginRight: '8px' }">
                {{ pointsLabel$() }}:
              </label>
              <input
                v-model.number="question.point_value"
                type="number"
                min="1"
                max="100"
                class="points-input"
                :style="{
                  borderColor: $themeTokens.fineLine,
                  backgroundColor: $themeTokens.surface,
                  color: $themeTokens.text,
                }"
                @input="onQuestionChange"
              >
            </div>
            <div
              v-if="isOptionCorrectConfigured(question)"
              class="correct-indicator-pill"
            >
              <KIcon
                icon="check"
                class="check-icon"
              />
              <span>{{ answerKeySetNotice$() }}</span>
            </div>
            <div
              v-else
              class="warning-indicator-pill"
            >
              <KIcon
                icon="warning"
                class="warn-icon"
              />
              <span>{{ setAnswerKeyNotice$() }}</span>
            </div>
          </div>

          <div class="bottom-right-actions">
            <KIconButton
              icon="copy"
              :tooltip="duplicateQuestion$()"
              :ariaLabel="duplicateQuestion$()"
              @click.stop="duplicateQuestion(qIndex)"
            />
            <KIconButton
              icon="trash"
              :tooltip="deleteQuestion$()"
              :ariaLabel="deleteQuestion$()"
              @click.stop="deleteQuestion(qIndex)"
            />
          </div>
        </div>

        <!-- Optional Feedback / Explanation Accordion -->
        <div class="explanation-row mt-8">
          <KTextbox
            v-model="question.explanation"
            :label="explanationOptionalLabel$()"
            :placeholder="explanationPlaceholder$()"
            @input="onQuestionChange"
          />
        </div>
      </div>
    </div>

    <!-- Floating / Sticky Add Question Bar -->
    <div class="editor-footer-bar mt-16">
      <KButton
        :text="addQuestionAction$()"
        icon="plus"
        :primary="true"
        appearance="raised-button"
        class="add-question-large-btn"
        @click="addNewQuestion"
      />
    </div>

    <!-- Image Uploading Indicator Overlay -->
    <div
      v-if="isUploadingImage"
      class="upload-overlay"
    >
      <KCircularLoader :delay="false" />
      <span class="uploading-text">{{ uploadingImageNotice$() }}</span>
    </div>
  </div>

</template>


<script>

  import { ref, computed } from 'vue';
  import client from 'kolibri/client';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useSnackbar from 'kolibri/composables/useSnackbar';
  import { injectQuizCreation } from '../../../composables/useQuizCreation';

  const editorStrings = createTranslator('GoogleFormsQuizEditorStrings', {
    authorCustomQuestionsTitle: {
      message: 'Custom Question Builder (Google Forms Style)',
      context: 'Header title of Google Forms quiz builder',
    },
    authorCustomQuestionsSubtitle: {
      message:
        'Create questions with rich prompts, individual choice images, answer keys, and point values.',
      context: 'Subtitle of quiz editor',
    },
    addQuestionAction: {
      message: 'Add Question',
      context: 'Button label to add a new question',
    },
    noQuestionsYet: {
      message: 'No questions created yet',
      context: 'Empty state header',
    },
    clickToAddFirstQuestion: {
      message: 'Click Add Question to build your first question block.',
      context: 'Empty state message',
    },
    moveUpAction: {
      message: 'Move Question Up',
      context: 'Button tooltip',
    },
    moveDownAction: {
      message: 'Move Question Down',
      context: 'Button tooltip',
    },
    multipleChoiceLabel: {
      message: 'Multiple choice',
      context: 'Question type option',
    },
    checkboxesLabel: {
      message: 'Checkboxes (Multi-select)',
      context: 'Question type option',
    },
    shortAnswerLabel: {
      message: 'Short answer',
      context: 'Question type option',
    },
    trueFalseLabel: {
      message: 'True / False',
      context: 'Question type option',
    },
    questionPromptLabel: {
      message: 'Question Prompt',
      context: 'Textbox label',
    },
    enterPromptPlaceholder: {
      message: 'Type your question here...',
      context: 'Textbox placeholder',
    },
    uploadPromptImage: {
      message: 'Upload question image',
      context: 'Image button tooltip',
    },
    uploadOptionImage: {
      message: 'Upload image for this choice',
      context: 'Option image button tooltip',
    },
    removeImage: {
      message: 'Remove image',
      context: 'Remove button tooltip',
    },
    markAsCorrectAnswer: {
      message: 'Click to set as correct answer',
      context: 'Answer key tooltip',
    },
    optionPlaceholder: {
      message: 'Option',
      context: 'Choice placeholder',
    },
    addOptionAction: {
      message: 'Add Option',
      context: 'Add choice button',
    },
    removeOption: {
      message: 'Remove Option',
      context: 'Remove choice button',
    },
    shortAnswerHelp: {
      message: 'Specify acceptable answers separated by commas.',
      context: 'Short answer help text',
    },
    correctAnswersLabel: {
      message: 'Correct Answer(s)',
      context: 'Input label',
    },
    correctAnswersPlaceholder: {
      message: 'e.g. Paris, City of Light',
      context: 'Input placeholder',
    },
    caseSensitiveLabel: {
      message: 'Case-sensitive match',
      context: 'Checkbox label',
    },
    pointsLabel: {
      message: 'Points',
      context: 'Points input label',
    },
    answerKeySetNotice: {
      message: 'Answer key configured',
      context: 'Pill text when answer key is set',
    },
    setAnswerKeyNotice: {
      message: 'Click choice to select correct answer',
      context: 'Pill text warning answer key not set',
    },
    duplicateQuestion: {
      message: 'Duplicate question',
      context: 'Button tooltip',
    },
    deleteQuestion: {
      message: 'Delete question',
      context: 'Button tooltip',
    },
    explanationOptionalLabel: {
      message: 'Explanation & Feedback (Optional)',
      context: 'Textbox label',
    },
    explanationPlaceholder: {
      message: 'Explanation shown to learners after answering...',
      context: 'Textbox placeholder',
    },
    uploadingImageNotice: {
      message: 'Uploading image...',
      context: 'Loading text',
    },
    imageUploadSuccess: {
      message: 'Image uploaded successfully!',
      context: 'Snackbar success message',
    },
    imageUploadError: {
      message: 'Could not upload image. Please ensure it is a valid image under 10MB.',
      context: 'Snackbar error message',
    },
  });

  function generateHexId() {
    return 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[x]/g, () =>
      ((Math.random() * 16) | 0).toString(16),
    );
  }

  export default {
    name: 'GoogleFormsQuizEditor',
    setup() {
      const { createSnackbar } = useSnackbar();
      const { activeSectionIndex, activeSection, updateSection } = injectQuizCreation();

      const activeQuestionIndex = ref(0);
      const isUploadingImage = ref(false);

      // Initialize local questions from activeSection
      const localQuestions = ref(
        (activeSection.value?.questions || []).map(q => {
          if (!q.is_custom) {
            return q;
          }
          return {
            ...q,
            options: q.options ? [...q.options.map(o => ({ ...o }))] : [],
            answer_key: q.answer_key ? [...q.answer_key] : [],
          };
        }),
      );

      const totalQuestionsText = computed(() => {
        const count = localQuestions.value.length;
        return `${count} ${count === 1 ? 'question' : 'questions'}`;
      });

      const totalPointsText = computed(() => {
        const pts = localQuestions.value.reduce((acc, q) => acc + (Number(q.point_value) || 1), 0);
        return `${pts} ${pts === 1 ? 'point' : 'points'}`;
      });

      function syncToSection() {
        updateSection({
          sectionIndex: activeSectionIndex.value,
          questions: localQuestions.value.map(q => ({ ...q })),
        });
      }

      function onQuestionChange() {
        syncToSection();
      }

      function addNewQuestion() {
        const qId = generateHexId();
        const exerciseId = generateHexId();
        const opt1Id = `opt_${generateHexId().substring(0, 8)}`;
        const opt2Id = `opt_${generateHexId().substring(0, 8)}`;

        const newQ = {
          item: `${exerciseId}:${qId}`,
          exercise_id: exerciseId,
          question_id: qId,
          title: `Question ${localQuestions.value.length + 1}`,
          counter_in_exercise: 1,
          is_custom: true,
          question_type: 'multiple_choice',
          prompt: '',
          prompt_image: '',
          options: [
            { id: opt1Id, text: '', image: '' },
            { id: opt2Id, text: '', image: '' },
          ],
          answer_key: [opt1Id],
          point_value: 1,
          explanation: '',
          case_sensitive: false,
        };

        localQuestions.value.push(newQ);
        activeQuestionIndex.value = localQuestions.value.length - 1;
        syncToSection();
      }

      function handleQuestionTypeChange(question) {
        if (question.question_type === 'true_false') {
          const tId = `opt_${generateHexId().substring(0, 8)}`;
          const fId = `opt_${generateHexId().substring(0, 8)}`;
          question.options = [
            { id: tId, text: 'True', image: '' },
            { id: fId, text: 'False', image: '' },
          ];
          question.answer_key = [tId];
        } else if (question.question_type === 'short_answer') {
          question.options = [];
          question.answer_key = [];
        } else if (!question.options || question.options.length < 2) {
          const opt1Id = `opt_${generateHexId().substring(0, 8)}`;
          const opt2Id = `opt_${generateHexId().substring(0, 8)}`;
          question.options = [
            { id: opt1Id, text: '', image: '' },
            { id: opt2Id, text: '', image: '' },
          ];
          question.answer_key = [opt1Id];
        }
        syncToSection();
      }

      function addOption(question) {
        const optId = `opt_${generateHexId().substring(0, 8)}`;
        question.options.push({
          id: optId,
          text: '',
          image: '',
        });
        syncToSection();
      }

      function removeOption(question, optIndex) {
        const removed = question.options.splice(optIndex, 1)[0];
        if (removed && question.answer_key.includes(removed.id)) {
          question.answer_key = question.answer_key.filter(k => k !== removed.id);
        }
        syncToSection();
      }

      function toggleOptionAnswer(question, option) {
        if (
          question.question_type === 'multiple_choice' ||
          question.question_type === 'true_false'
        ) {
          question.answer_key = [option.id];
        } else if (question.question_type === 'checkboxes') {
          if (question.answer_key.includes(option.id)) {
            question.answer_key = question.answer_key.filter(id => id !== option.id);
          } else {
            question.answer_key.push(option.id);
          }
        }
        syncToSection();
      }

      function isOptionCorrect(question, option) {
        return (question.answer_key || []).includes(option.id);
      }

      function isOptionCorrectConfigured(question) {
        if (question.question_type === 'short_answer') {
          return question.answer_key && question.answer_key.length > 0;
        }
        return question.answer_key && question.answer_key.length > 0;
      }

      function updateShortAnswerKeys(question, val) {
        const keys = val
          .split(',')
          .map(s => s.trim())
          .filter(Boolean);
        question.answer_key = keys;
        syncToSection();
      }

      function moveQuestionUp(index) {
        if (index === 0) return;
        const temp = localQuestions.value[index];
        localQuestions.value.splice(index, 1);
        localQuestions.value.splice(index - 1, 0, temp);
        activeQuestionIndex.value = index - 1;
        syncToSection();
      }

      function moveQuestionDown(index) {
        if (index >= localQuestions.value.length - 1) return;
        const temp = localQuestions.value[index];
        localQuestions.value.splice(index, 1);
        localQuestions.value.splice(index + 1, 0, temp);
        activeQuestionIndex.value = index + 1;
        syncToSection();
      }

      function duplicateQuestion(index) {
        const source = localQuestions.value[index];
        const newExerciseId = generateHexId();
        const newQId = generateHexId();

        const optMap = {};
        const newOptions = (source.options || []).map(opt => {
          const newOptId = `opt_${generateHexId().substring(0, 8)}`;
          optMap[opt.id] = newOptId;
          return {
            ...opt,
            id: newOptId,
          };
        });

        const newAnswerKey = (source.answer_key || []).map(k => optMap[k] || k);

        const dup = {
          ...source,
          item: `${newExerciseId}:${newQId}`,
          exercise_id: newExerciseId,
          question_id: newQId,
          title: `${source.title} (Copy)`,
          options: newOptions,
          answer_key: newAnswerKey,
        };

        localQuestions.value.splice(index + 1, 0, dup);
        activeQuestionIndex.value = index + 1;
        syncToSection();
      }

      function deleteQuestion(index) {
        localQuestions.value.splice(index, 1);
        if (activeQuestionIndex.value >= localQuestions.value.length) {
          activeQuestionIndex.value = Math.max(0, localQuestions.value.length - 1);
        }
        syncToSection();
      }

      function pickImageFile(onSelected) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.png,.jpg,.jpeg,.gif,.webp,.svg';
        input.onchange = e => {
          const file = e.target.files && e.target.files[0];
          if (file) {
            onSelected(file);
          }
        };
        input.click();
      }

      async function uploadImageFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await client({
          url: '/api/exams/exam/upload_image/',
          method: 'POST',
          data: formData,
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data.url;
      }

      function triggerPromptImageUpload(question) {
        pickImageFile(async file => {
          isUploadingImage.value = true;
          try {
            const url = await uploadImageFile(file);
            question.prompt_image = url;
            syncToSection();
            createSnackbar(editorStrings.imageUploadSuccess$());
          } catch (err) {
            createSnackbar(editorStrings.imageUploadError$());
          } finally {
            isUploadingImage.value = false;
          }
        });
      }

      function removePromptImage(question) {
        question.prompt_image = '';
        syncToSection();
      }

      function triggerOptionImageUpload(option) {
        pickImageFile(async file => {
          isUploadingImage.value = true;
          try {
            const url = await uploadImageFile(file);
            option.image = url;
            syncToSection();
            createSnackbar(editorStrings.imageUploadSuccess$());
          } catch (err) {
            createSnackbar(editorStrings.imageUploadError$());
          } finally {
            isUploadingImage.value = false;
          }
        });
      }

      function removeOptionImage(option) {
        option.image = '';
        syncToSection();
      }

      return {
        activeQuestionIndex,
        localQuestions,
        isUploadingImage,
        totalQuestionsText,
        totalPointsText,
        addNewQuestion,
        handleQuestionTypeChange,
        addOption,
        removeOption,
        toggleOptionAnswer,
        isOptionCorrect,
        isOptionCorrectConfigured,
        updateShortAnswerKeys,
        moveQuestionUp,
        moveQuestionDown,
        duplicateQuestion,
        deleteQuestion,
        triggerPromptImageUpload,
        removePromptImage,
        triggerOptionImageUpload,
        removeOptionImage,
        onQuestionChange,
        ...editorStrings,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .google-forms-quiz-editor {
    position: relative;
    max-width: 900px;
    padding-bottom: 32px;
    margin: 0 auto;
  }

  .editor-header-banner {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    margin-bottom: 24px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .header-right {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .stats-badge {
    padding: 6px 12px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 16px;
  }

  .empty-state-card {
    padding: 48px 24px;
    text-align: center;
    border: 2px dashed;
    border-radius: 8px;
  }

  .empty-icon-circle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    margin-bottom: 12px;
    border-radius: 50%;
  }

  .large-icon {
    font-size: 32px;
  }

  .questions-cards-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .question-block-card {
    padding: 20px;
    cursor: default;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    transition: all 0.2s ease;

    &.is-active {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
  }

  .card-top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    margin-bottom: 16px;
  }

  .order-controls {
    display: flex;
    gap: 6px;
    align-items: center;
  }

  .question-number-pill {
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 700;
    border-radius: 12px;
  }

  .rotate-up {
    transform: rotate(90deg);
  }

  .rotate-down {
    transform: rotate(90deg);
  }

  .question-type-select {
    padding: 6px 12px;
    font-family: inherit;
    font-size: 14px;
    font-weight: 500;
    border: 1px solid;
    border-radius: 4px;
    outline: none;
    cursor: pointer;
  }

  .prompt-section {
    margin-bottom: 16px;
  }

  .prompt-input-row {
    display: flex;
    gap: 12px;
    align-items: flex-start;
  }

  .prompt-textbox {
    flex: 1;
    margin: 0;
  }

  .prompt-image-action {
    padding-top: 8px;
  }

  .hidden-file-input {
    display: none;
  }

  .image-preview-box {
    position: relative;
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    border: 1px solid #e2e8f0;
    border-radius: 6px;

    .preview-img {
      display: block;
      max-width: 100%;
      max-height: 240px;
      object-fit: contain;
    }

    .remove-image-btn {
      position: absolute;
      top: 4px;
      right: 4px;
      background-color: rgba(255, 255, 255, 0.85);
      border-radius: 50%;
    }
  }

  .options-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 16px;
  }

  .option-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
  }

  .answer-key-indicator {
    padding: 4px;
    cursor: pointer;
    background: transparent;
    border: none;
    border-radius: 4px;
    transition: background 0.15s ease;

    &:hover {
      background-color: rgba(0, 0, 0, 0.05);
    }
  }

  .option-text-field {
    flex: 1;
    min-width: 160px;
  }

  .option-input {
    width: 100%;
    padding: 8px 12px;
    font-family: inherit;
    font-size: 14px;
    border: 1px solid;
    border-radius: 4px;
    outline: none;
    transition: border-color 0.2s ease;

    &:focus {
      border-color: #3b82f6;
    }
  }

  .option-image-preview {
    position: relative;
    display: inline-flex;
    align-items: center;

    .option-thumb {
      width: 44px;
      height: 44px;
      object-fit: cover;
      border: 1px solid #cbd5e1;
      border-radius: 4px;
    }

    .remove-opt-img {
      position: absolute;
      top: -6px;
      right: -6px;
      background-color: white;
      border-radius: 50%;
    }
  }

  .short-answer-container {
    padding: 12px 16px;
    margin-bottom: 16px;
    background-color: #f8fafc;
    border-radius: 6px;
  }

  .card-bottom-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    justify-content: space-between;
    padding-top: 12px;
    margin-top: 12px;
  }

  .bottom-left-settings {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    align-items: center;
  }

  .points-field {
    display: flex;
    align-items: center;
    font-size: 14px;
    font-weight: 500;
  }

  .points-input {
    width: 60px;
    padding: 4px 8px;
    font-family: inherit;
    font-size: 14px;
    font-weight: 600;
    text-align: center;
    border: 1px solid;
    border-radius: 4px;
  }

  .correct-indicator-pill {
    display: inline-flex;
    gap: 4px;
    align-items: center;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    color: #15803d;
    background-color: #dcfce7;
    border-radius: 12px;

    .check-icon {
      font-size: 14px;
    }
  }

  .warning-indicator-pill {
    display: inline-flex;
    gap: 4px;
    align-items: center;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    color: #b45309;
    background-color: #fef3c7;
    border-radius: 12px;

    .warn-icon {
      font-size: 14px;
    }
  }

  .bottom-right-actions {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .editor-footer-bar {
    display: flex;
    justify-content: center;
  }

  .add-question-large-btn {
    min-width: 200px;
  }

  .upload-overlay {
    position: fixed;
    top: 50%;
    left: 50%;
    z-index: 1000;
    display: flex;
    gap: 12px;
    align-items: center;
    padding: 16px 24px;
    background-color: rgba(255, 255, 255, 0.95);
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    transform: translate(-50%, -50%);
  }

  .uploading-text {
    font-size: 14px;
    font-weight: 600;
  }

  .mt-8 {
    margin-top: 8px;
  }

  .mt-16 {
    margin-top: 16px;
  }

</style>
