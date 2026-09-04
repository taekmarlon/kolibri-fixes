<template>

  <KModal
    v-if="isAiEnabled"
    :title="modalTitle$()"
    :submitText="copyToClipboardButton$()"
    :cancelText="closeButton$()"
    :submitDisabled="!generatedContent"
    @submit="copyContent"
    @cancel="$emit('close')"
  >
    <div class="ai-generator-modal-body">
      <p class="modal-desc" :style="{ color: $themeTokens.annotation }">
        {{ modalDescription$() }}
      </p>

      <div class="form-grid">
        <KTextbox
          v-model="topic"
          :label="topicLabel$()"
          :placeholder="topicPlaceholder$()"
          :invalid="Boolean(topicError)"
          :invalidText="topicError"
          :disabled="isLoading"
        />

        <div class="options-row">
          <KSelect
            v-model="selectedGrade"
            :label="gradeLevelLabel$()"
            :options="gradeOptions"
            :disabled="isLoading"
          />

          <KSelect
            v-model="selectedCount"
            :label="numQuestionsLabel$()"
            :options="countOptions"
            :disabled="isLoading"
          />
        </div>

        <div class="action-row">
          <KButton
            :text="isLoading ? generating$() : generateButton$()"
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
          {{ generatingText$() }}
        </p>
      </div>

      <!-- Generated Result Box -->
      <div
        v-if="generatedContent && !isLoading"
        class="result-box"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1.5px solid ${$themeTokens.fineLine}`,
          borderRadius: '8px',
          padding: '18px',
          marginTop: '16px',
        }"
      >
        <div class="result-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
          <span class="result-badge" :style="{ backgroundColor: $themeTokens.primary, color: 'white', padding: '4px 10px', borderRadius: '6px', fontSize: '13px', fontWeight: 'bold' }">
            {{ generatedResult$() }}
          </span>
          <span v-if="copied" class="copied-indicator" :style="{ color: $themeTokens.success, fontWeight: 'bold' }">
            {{ copiedNotice$() }}
          </span>
        </div>
        <AiMessageRenderer
          :content="generatedContent"
          :gradeLevel="selectedGrade ? selectedGrade.value : 'elementary'"
        />
      </div>
    </div>
  </KModal>

</template>


<script>

  import { ref } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useAiTutor from 'kolibri-common/composables/useAiTutor';
  import AiMessageRenderer from 'kolibri-common/components/AiMessageRenderer';

  const modalStrings = createTranslator('AiQuizGeneratorModalStrings', {
    modalTitle: {
      message: 'AI Practice Question & Quiz Generator',
      context: 'Title of the AI generator modal',
    },
    modalDescription: {
      message: 'Automatically generate high-quality practice questions and quizzes tailored to any topic and grade level.',
      context: 'Subtitle description of modal',
    },
    topicLabel: {
      message: 'Topic or Learning Standard',
      context: 'Label for topic input',
    },
    topicPlaceholder: {
      message: 'e.g. Quadratic Equations, Photosynthesis, Fractions',
      context: 'Placeholder for topic input',
    },
    gradeLevelLabel: {
      message: 'Grade Level',
      context: 'Label for grade dropdown',
    },
    numQuestionsLabel: {
      message: 'Number of Questions',
      context: 'Label for question count dropdown',
    },
    generateButton: {
      message: 'Generate Questions with AI',
      context: 'Button to trigger AI generation',
    },
    generating: {
      message: 'Generating...',
      context: 'Loading button text',
    },
    generatingText: {
      message: 'Generating educational questions with AI model...',
      context: 'Loading status text',
    },
    generatedResult: {
      message: 'Generated Questions',
      context: 'Header for result box',
    },
    copyToClipboardButton: {
      message: 'Copy Questions',
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
      message: 'Please enter a topic',
      context: 'Validation error',
    },
  });

  export default {
    name: 'AiQuizGeneratorModal',
    components: {
      AiMessageRenderer,
    },
    emits: ['close'],
    setup(props, { emit }) {
      const { isAiEnabled, generateQuiz, isLoading } = useAiTutor();
      const {
        modalTitle$,
        modalDescription$,
        topicLabel$,
        topicPlaceholder$,
        gradeLevelLabel$,
        numQuestionsLabel$,
        generateButton$,
        generating$,
        generatingText$,
        generatedResult$,
        copyToClipboardButton$,
        closeButton$,
        copiedNotice$,
        topicRequiredError$,
      } = modalStrings;

      const topic = ref('');
      const topicError = ref('');
      const generatedContent = ref('');
      const copied = ref(false);

      const gradeOptions = [
        { label: 'Elementary School (Grades 1-5)', value: 'Elementary School' },
        { label: 'Middle School (Grades 6-8)', value: 'Middle School' },
        { label: 'High School (Grades 9-12)', value: 'High School' },
        { label: 'College / Advanced', value: 'College / Advanced' },
      ];
      const selectedGrade = ref(gradeOptions[1]);

      const countOptions = [
        { label: '3 Questions', value: 3 },
        { label: '5 Questions', value: 5 },
        { label: '10 Questions', value: 10 },
      ];
      const selectedCount = ref(countOptions[1]);

      async function handleGenerate() {
        if (!topic.value.trim()) {
          topicError.value = topicRequiredError$();
          return;
        }
        topicError.value = '';
        copied.value = false;

        try {
          const res = await generateQuiz({
            topic: topic.value.trim(),
            grade_level: selectedGrade.value.value,
            num_questions: selectedCount.value.value,
          });
          generatedContent.value = res.quiz || '';
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
        topic,
        topicError,
        gradeOptions,
        selectedGrade,
        countOptions,
        selectedCount,
        generatedContent,
        copied,
        handleGenerate,
        copyContent,
        modalTitle$,
        modalDescription$,
        topicLabel$,
        topicPlaceholder$,
        gradeLevelLabel$,
        numQuestionsLabel$,
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
