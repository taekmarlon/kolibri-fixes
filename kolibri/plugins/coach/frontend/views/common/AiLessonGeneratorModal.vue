<template>

  <KModal
    v-if="isAiEnabled"
    :title="modalTitle"
    :submitText="copyToClipboardButton"
    :cancelText="closeButton"
    :submitDisabled="!generatedContent"
    @submit="copyContent"
    @cancel="$emit('close')"
  >
    <div class="ai-generator-modal-body">
      <p class="modal-desc" :style="{ color: $themeTokens.annotation }">
        {{ modalDescription }}
      </p>

      <div class="form-grid">
        <KTextbox
          v-model="lessonTopic"
          :label="topicLabel"
          :placeholder="topicPlaceholder"
          :invalid="Boolean(topicError)"
          :invalidText="topicError"
          :disabled="isLoading"
        />

        <div class="options-row">
          <KSelect
            v-model="selectedGrade"
            :label="gradeLevelLabel"
            :options="gradeOptions"
            :disabled="isLoading"
          />

          <KSelect
            v-model="selectedDuration"
            :label="durationLabel"
            :options="durationOptions"
            :disabled="isLoading"
          />
        </div>

        <div class="action-row">
          <KButton
            :text="isLoading ? generating : generateButton"
            :primary="true"
            appearance="raised-button"
            icon="generate"
            :disabled="isLoading"
            @click="handleGenerate"
          />
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <KCircularLoader :delay="false" />
        <p :style="{ color: $themeTokens.text, marginTop: '12px' }">
          {{ generatingText }}
        </p>
      </div>

      <!-- Generated Result Box -->
      <div
        v-if="generatedContent && !isLoading"
        class="result-box"
        :style="{
          backgroundColor: $themePalette.grey.v_100,
          border: '1px solid ' + $themeTokens.fineLine,
          color: $themeTokens.text,
        }"
      >
        <div class="result-header">
          <span class="result-badge" :style="{ backgroundColor: $themeTokens.primary, color: 'white' }">
            {{ generatedResult }}
          </span>
          <span v-if="copied" class="copied-indicator" :style="{ color: $themeTokens.success }">
            {{ copiedNotice }}
          </span>
        </div>
        <pre class="result-pre">{{ generatedContent }}</pre>
      </div>
    </div>
  </KModal>

</template>


<script>

  import { ref } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useAiTutor from 'kolibri-common/composables/useAiTutor';

  const modalStrings = createTranslator('AiLessonGeneratorModalStrings', {
    modalTitle: {
      message: 'AI Lesson Plan & Activity Generator',
      context: 'Title of the AI lesson generator modal',
    },
    modalDescription: {
      message:
        'Create a complete, curriculum-aligned lesson plan with objectives, step-by-step activities, and formative assessments.',
      context: 'Subtitle description of modal',
    },
    topicLabel: {
      message: 'Lesson Topic or Standard',
      context: 'Label for lesson topic input',
    },
    topicPlaceholder: {
      message: 'e.g. Newton’s Laws of Motion, Introduction to Coding, World War II Causes',
      context: 'Placeholder for lesson topic input',
    },
    gradeLevelLabel: {
      message: 'Grade Level',
      context: 'Label for grade dropdown',
    },
    durationLabel: {
      message: 'Class Duration',
      context: 'Label for duration dropdown',
    },
    generateButton: {
      message: 'Generate Lesson Plan with AI',
      context: 'Button to trigger AI lesson generation',
    },
    generating: {
      message: 'Generating Lesson...',
      context: 'Loading button text',
    },
    generatingText: {
      message: 'Drafting structured lesson plan with AI model...',
      context: 'Loading status text',
    },
    generatedResult: {
      message: 'Lesson Plan & Activities',
      context: 'Header for result box',
    },
    copyToClipboardButton: {
      message: 'Copy Lesson Plan',
      context: 'Submit button text to copy content',
    },
    closeButton: {
      message: 'Close',
      context: 'Cancel button text',
    },
    copiedNotice: {
      message: 'Copied to clipboard!',
      context: 'Confirmation alert',
    },
    topicRequiredError: {
      message: 'Please enter a lesson topic',
      context: 'Validation error',
    },
  });

  export default {
    name: 'AiLessonGeneratorModal',
    emits: ['close'],
    setup(props, { emit }) {
      const { isAiEnabled, generateLesson, isLoading } = useAiTutor();
      const {
        modalTitle$,
        modalDescription$,
        topicLabel$,
        topicPlaceholder$,
        gradeLevelLabel$,
        durationLabel$,
        generateButton$,
        generating$,
        generatingText$,
        generatedResult$,
        copyToClipboardButton$,
        closeButton$,
        copiedNotice$,
        topicRequiredError$,
      } = modalStrings;

      const lessonTopic = ref('');
      const topicError = ref('');
      const generatedContent = ref('');
      const copied = ref(false);

      const gradeOptions = [
        { label: 'Elementary School (Grades 1-5)', value: 'Elementary School' },
        { label: 'Middle School (Grades 6-8)', value: 'Middle School' },
        { label: 'High School (Grades 9-12)', value: 'High School' },
        { label: 'College / Adult Education', value: 'College / Adult Education' },
      ];
      const selectedGrade = ref(gradeOptions[1]);

      const durationOptions = [
        { label: '30 Minutes', value: '30 minutes' },
        { label: '45 Minutes (Standard Class)', value: '45 minutes' },
        { label: '60 Minutes', value: '60 minutes' },
        { label: '90 Minutes (Block Period)', value: '90 minutes' },
      ];
      const selectedDuration = ref(durationOptions[1]);

      async function handleGenerate() {
        if (!lessonTopic.value.trim()) {
          topicError.value = topicRequiredError;
          return;
        }
        topicError.value = '';
        copied.value = false;

        try {
          const res = await generateLesson({
            topic: lessonTopic.value.trim(),
            grade_level: selectedGrade.value.value,
            duration: selectedDuration.value.value,
          });
          generatedContent.value = res.lesson || '';
        } catch (err) {
          // handled in composable
        }
      }

      function copyContent() {
        if (!generatedContent.value) return;
        if (navigator.clipboard) {
          navigator.clipboard.writeText(generatedContent.value).then(() => {
            copied.value = true;
            setTimeout(() => {
              emit('close');
            }, 1000);
          });
        }
      }

      return {
        isAiEnabled,
        isLoading,
        lessonTopic,
        topicError,
        gradeOptions,
        selectedGrade,
        durationOptions,
        selectedDuration,
        generatedContent,
        copied,
        handleGenerate,
        copyContent,
        modalTitle$,
        modalDescription$,
        topicLabel$,
        topicPlaceholder$,
        gradeLevelLabel$,
        durationLabel$,
        generateButton$,
        generating$,
        generatingText$,
        generatedResult$,
        copyToClipboardButton$,
        closeButton$,
        copiedNotice$,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .ai-generator-modal-body {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .modal-desc {
    margin: 0;
    font-size: 0.95rem;
  }

  .form-grid {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .options-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;

    > * {
      flex: 1;
      min-width: 180px;
    }
  }

  .action-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 8px;
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px 0;
  }

  .result-box {
    margin-top: 16px;
    padding: 16px;
    border-radius: 8px;
    max-height: 320px;
    overflow-y: auto;
  }

  .result-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }

  .result-badge {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: bold;
  }

  .copied-indicator {
    font-size: 0.85rem;
    font-weight: bold;
  }

  .result-pre {
    margin: 0;
    white-space: pre-wrap;
    font-family: inherit;
    font-size: 0.9rem;
    line-height: 1.5;
  }

</style>
