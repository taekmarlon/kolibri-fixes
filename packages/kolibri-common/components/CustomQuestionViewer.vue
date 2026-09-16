<template>

  <div class="custom-question-viewer">
    <!-- Prompt Text -->
    <div
      class="question-prompt"
      :style="{ color: $themeTokens.text }"
    >
      <h3 class="prompt-text">
        {{ question.prompt || question.title || fallbackTitle$() }}
      </h3>
    </div>

    <!-- Question Prompt Image -->
    <div
      v-if="question.prompt_image"
      class="prompt-image-container"
    >
      <img
        :src="question.prompt_image"
        alt="Question illustration"
        class="prompt-image"
      >
    </div>

    <!-- Multiple Choice / True-False -->
    <div
      v-if="question.question_type === 'multiple_choice' || question.question_type === 'true_false'"
      class="choices-list mt-24"
    >
      <KRadioButtonGroup>
        <div
          v-for="option in question.options"
          :key="option.id"
          class="choice-item"
          :class="{ 'is-selected': selectedOption === option.id }"
          :style="{
            borderColor:
              (preview || showCorrectAnswer) && isOptionCorrect(option.id)
                ? '#22c55e'
                : selectedOption === option.id
                ? $themeTokens.primary
                : $themeTokens.fineLine,
            backgroundColor:
              (preview || showCorrectAnswer) && isOptionCorrect(option.id)
                ? '#f0fdf4'
                : selectedOption === option.id
                ? $themePalette.grey.v_100
                : $themeTokens.surface,
          }"
          @click="selectSingleChoice(option.id)"
        >
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
            <KRadioButton
              :label="option.text || optionFallback$()"
              :buttonValue="option.id"
              :currentValue="selectedOption"
              class="choice-radio"
              @input="selectSingleChoice(option.id)"
            />
            <span
              v-if="(preview || showCorrectAnswer) && isOptionCorrect(option.id)"
              class="correct-badge"
              style="display: flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 600; color: #15803d;"
            >
              <KIcon
                icon="check"
                style="fill: #15803d;"
              />
              {{ correctAnswerLabel$() }}
            </span>
          </div>

          <!-- Choice Image (if attached) -->
          <div
            v-if="option.image"
            class="choice-image-container mt-8"
          >
            <img
              :src="option.image"
              alt="Option illustration"
              class="choice-image"
            >
          </div>
        </div>
      </KRadioButtonGroup>
    </div>

    <!-- Checkboxes (Multi-Select) -->
    <div
      v-else-if="question.question_type === 'checkboxes'"
      class="choices-list mt-24"
    >
      <div
        v-for="option in question.options"
        :key="option.id"
        class="choice-item"
        :class="{ 'is-selected': isChoiceChecked(option.id) }"
        :style="{
          borderColor:
            (preview || showCorrectAnswer) && isOptionCorrect(option.id)
              ? '#22c55e'
              : isChoiceChecked(option.id)
              ? $themeTokens.primary
              : $themeTokens.fineLine,
          backgroundColor:
            (preview || showCorrectAnswer) && isOptionCorrect(option.id)
              ? '#f0fdf4'
              : isChoiceChecked(option.id)
              ? $themePalette.grey.v_100
              : $themeTokens.surface,
        }"
        @click="toggleMultiChoice(option.id)"
      >
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
          <KCheckbox
            :label="option.text || optionFallback$()"
            :checked="isChoiceChecked(option.id)"
            class="choice-checkbox"
            @change="toggleMultiChoice(option.id)"
            @click.stop="() => {}"
          />
          <span
            v-if="(preview || showCorrectAnswer) && isOptionCorrect(option.id)"
            class="correct-badge"
            style="display: flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 600; color: #15803d;"
          >
            <KIcon
              icon="check"
              style="fill: #15803d;"
            />
            {{ correctAnswerLabel$() }}
          </span>
        </div>

        <!-- Choice Image (if attached) -->
        <div
          v-if="option.image"
          class="choice-image-container mt-8"
        >
          <img
            :src="option.image"
            alt="Option illustration"
            class="choice-image"
          >
        </div>
      </div>
    </div>

    <!-- Short Answer -->
    <div
      v-else-if="question.question_type === 'short_answer'"
      class="short-answer-entry mt-24"
    >
      <KTextbox
        v-model="shortAnswerText"
        :label="yourAnswerLabel$()"
        :placeholder="typeYourAnswerPlaceholder$()"
        class="short-answer-input"
        @input="onShortAnswerChange"
      />
      <div
        v-if="(preview || showCorrectAnswer) && question.answer_key && question.answer_key.length"
        class="mt-12"
        style="padding: 10px 14px; background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; color: #15803d;"
      >
        <strong>{{ acceptedAnswersLabel$() }}:</strong> {{ (question.answer_key || []).join(', ') }}
      </div>
    </div>

    <!-- H5P / Interactive Activity -->
    <div
      v-else-if="isInteractiveQuestion"
      class="interactive-question-container mt-16"
    >
      <iframe
        v-if="resolvedInteractiveUrl"
        :key="resolvedInteractiveUrl"
        :src="resolvedInteractiveUrl"
        class="interactive-player-iframe"
        sandbox="allow-scripts allow-same-origin"
        style="width: 100%; min-height: 560px; border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff;"
        allow="fullscreen; geolocation; microphone; camera; midi"
      ></iframe>
      <iframe
        v-else-if="question.content"
        :srcdoc="question.content"
        class="interactive-srcdoc-iframe"
        sandbox="allow-scripts allow-same-origin"
        style="width: 100%; min-height: 560px; border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff;"
        allow="fullscreen; geolocation; microphone; camera; midi"
      ></iframe>
      <div
        v-if="!preview"
        class="interactive-controls mt-16"
        style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;"
      >
        <div
          v-if="interactiveCompleted"
          class="completion-badge"
          :style="{
            padding: '8px 16px',
            backgroundColor: '#f0fdf4',
            border: '1px solid #bbf7d0',
            color: '#15803d',
            borderRadius: '6px',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }"
        >
          <KIcon icon="check" />
          <span>{{ activityCompletedLabel$() }}</span>
        </div>
        <div v-else></div>

        <KButton
          :text="interactiveCompleted ? markAsIncompleteLabel$() : markAsCompletedLabel$()"
          :appearance="interactiveCompleted ? 'flat-button' : 'raised-button'"
          :primary="!interactiveCompleted"
          @click="toggleInteractiveComplete"
        />
      </div>
    </div>

    <!-- Explanation (if provided and in review/preview) -->
    <div
      v-if="(preview || showCorrectAnswer) && question.explanation"
      class="explanation-box mt-16"
      :style="{
        backgroundColor: $themePalette.grey.v_100,
        border: `1px solid ${$themeTokens.fineLine}`,
        borderRadius: '8px',
        padding: '14px',
      }"
    >
      <div
        style="font-weight: bold; margin-bottom: 4px;"
        :style="{ color: $themeTokens.annotation }"
      >
        {{ explanationLabel$() }}:
      </div>
      <p style="margin: 0;">
        {{ question.explanation }}
      </p>
    </div>
  </div>

</template>


<script>

  import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';

  const viewerStrings = createTranslator('CustomQuestionViewerStrings', {
    fallbackTitle: {
      message: 'Question',
      context: 'Default title',
    },
    optionFallback: {
      message: 'Option',
      context: 'Default choice label',
    },
    yourAnswerLabel: {
      message: 'Your Answer',
      context: 'Textbox label',
    },
    typeYourAnswerPlaceholder: {
      message: 'Type your answer here...',
      context: 'Textbox placeholder',
    },
    activityCompletedLabel: {
      message: 'Interactive Activity Completed!',
      context: 'Status badge when learner finishes interactive task',
    },
    markAsCompletedLabel: {
      message: 'Mark as completed',
      context: 'Button label to mark interactive task complete',
    },
    markAsIncompleteLabel: {
      message: 'Mark as incomplete',
      context: 'Button label to toggle interactive task incomplete',
    },
    correctAnswerLabel: {
      message: 'Correct answer',
      context: 'Badge indicating the correct option in preview/review',
    },
    acceptedAnswersLabel: {
      message: 'Accepted answers',
      context: 'Label for correct answers for short answer questions',
    },
    explanationLabel: {
      message: 'Explanation',
      context: 'Heading for explanation box',
    },
  });

  export default {
    name: 'CustomQuestionViewer',
    props: {
      question: {
        type: Object,
        required: true,
      },
      answerState: {
        type: [String, Array, Object],
        default: null,
      },
      preview: {
        type: Boolean,
        default: false,
      },
      showCorrectAnswer: {
        type: Boolean,
        default: false,
      },
    },
    emits: ['interaction'],
    setup(props, { emit }) {
      const selectedOption = ref(
        typeof props.answerState === 'string' ? props.answerState : null,
      );

      const selectedOptions = ref(
        Array.isArray(props.answerState) ? [...props.answerState] : [],
      );

      const shortAnswerText = ref(
        typeof props.answerState === 'string' ? props.answerState : '',
      );

      const interactiveCompleted = ref(
        props.answerState === 'completed' || Boolean(props.answerState),
      );

      const isInteractiveQuestion = computed(() => {
        const q = props.question;
        if (!q) return false;
        const type = (q.question_type || '').toLowerCase();
        return (
          type === 'h5p' ||
          type === 'interactive' ||
          Boolean(q.file_url) ||
          Boolean(q.h5p_content_id) ||
          Boolean(q.h5p_url) ||
          (Boolean(q.content) && type !== 'short_answer')
        );
      });

      const resolvedInteractiveUrl = computed(() => {
        const q = props.question;
        if (!q) return '';
        if (q.file_url) return q.file_url;
        if (q.h5p_url) return q.h5p_url;
        if (q.h5p_content_id) return `/h5p/play/${q.h5p_content_id}`;
        return '';
      });

      function isOptionCorrect(optId) {
        return Boolean(props.question.answer_key && props.question.answer_key.includes(optId));
      }

      function toggleInteractiveComplete() {
        interactiveCompleted.value = !interactiveCompleted.value;
        emit('interaction');
      }

      function onWindowMessage(event) {
        if (!event.data) return;
        const msg = event.data;
        if (
          msg.type === 'H5P_COMPLETE' ||
          msg.type === 'H5P_SCORE' ||
          (msg.verb &&
            (msg.verb.includes('completed') ||
              msg.verb.includes('passed') ||
              msg.verb.includes('answered')))
        ) {
          interactiveCompleted.value = true;
          emit('interaction');
        }
      }

      onMounted(() => {
        window.addEventListener('message', onWindowMessage);
      });

      onUnmounted(() => {
        window.removeEventListener('message', onWindowMessage);
      });

      watch(
        () => props.answerState,
        newVal => {
          if (
            props.question.question_type === 'multiple_choice' ||
            props.question.question_type === 'true_false'
          ) {
            selectedOption.value = typeof newVal === 'string' ? newVal : null;
          } else if (props.question.question_type === 'checkboxes') {
            selectedOptions.value = Array.isArray(newVal) ? [...newVal] : [];
          } else if (props.question.question_type === 'short_answer') {
            shortAnswerText.value = typeof newVal === 'string' ? newVal : '';
          } else if (
            props.question.question_type === 'h5p' ||
            props.question.question_type === 'interactive' ||
            isInteractiveQuestion.value
          ) {
            interactiveCompleted.value = newVal === 'completed' || Boolean(newVal);
          }
        },
      );

      function selectSingleChoice(optId) {
        selectedOption.value = optId;
        emit('interaction');
      }

      function toggleMultiChoice(optId) {
        if (selectedOptions.value.includes(optId)) {
          selectedOptions.value = selectedOptions.value.filter(id => id !== optId);
        } else {
          selectedOptions.value.push(optId);
        }
        emit('interaction');
      }

      function isChoiceChecked(optId) {
        return selectedOptions.value.includes(optId);
      }

      function onShortAnswerChange() {
        emit('interaction');
      }

      function checkAnswer() {
        const q = props.question;
        const type = q.question_type;
        let isCorrect = false;
        let answerState = null;
        let simpleAnswer = '';

        if (type === 'multiple_choice' || type === 'true_false') {
          answerState = selectedOption.value;
          const chosenOpt = (q.options || []).find(o => o.id === selectedOption.value);
          simpleAnswer = chosenOpt ? chosenOpt.text : '';
          const correctKey = (q.answer_key || [])[0];
          isCorrect = Boolean(selectedOption.value && selectedOption.value === correctKey);
        } else if (type === 'checkboxes') {
          answerState = [...selectedOptions.value];
          const chosenTexts = (q.options || [])
            .filter(o => selectedOptions.value.includes(o.id))
            .map(o => o.text);
          simpleAnswer = chosenTexts.join(', ');

          const expectedKeys = (q.answer_key || []).slice().sort();
          const userKeys = selectedOptions.value.slice().sort();
          isCorrect =
            expectedKeys.length > 0 &&
            expectedKeys.length === userKeys.length &&
            expectedKeys.every((key, idx) => key === userKeys[idx]);
        } else if (type === 'short_answer') {
          answerState = shortAnswerText.value;
          simpleAnswer = shortAnswerText.value.trim();
          const expected = (q.answer_key || []).map(s => (s || '').trim());
          if (q.case_sensitive) {
            isCorrect = expected.includes(simpleAnswer);
          } else {
            const lowerAnswer = simpleAnswer.toLowerCase();
            isCorrect = expected.map(s => s.toLowerCase()).includes(lowerAnswer);
          }
        } else if (type === 'h5p' || type === 'interactive' || isInteractiveQuestion.value) {
          const isDone = Boolean(interactiveCompleted.value);
          answerState = isDone ? 'completed' : null;
          simpleAnswer = isDone ? 'Completed' : 'In progress';
          isCorrect = isDone;
        }

        return {
          answerState,
          simpleAnswer,
          correct: isCorrect ? 1 : 0,
        };
      }

      return {
        selectedOption,
        selectedOptions,
        shortAnswerText,
        interactiveCompleted,
        isInteractiveQuestion,
        resolvedInteractiveUrl,
        isOptionCorrect,
        toggleInteractiveComplete,
        selectSingleChoice,
        toggleMultiChoice,
        isChoiceChecked,
        onShortAnswerChange,
        checkAnswer,
        ...viewerStrings,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .custom-question-viewer {
    max-width: 760px;
    padding: 16px 0;
    margin: 0 auto;
  }

  .question-prompt {
    margin-bottom: 20px;

    .prompt-text {
      font-size: 20px;
      font-weight: 600;
      line-height: 1.4;
    }
  }

  .prompt-image-container {
    margin: 16px 0 24px;
    text-align: center;

    .prompt-image {
      max-width: 100%;
      max-height: 380px;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      object-fit: contain;
    }
  }

  .choices-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .choice-item {
    padding: 12px 16px;
    cursor: pointer;
    border: 1.5px solid;
    border-radius: 8px;
    transition: all 0.15s ease;

    &:hover {
      opacity: 0.95;
      transform: translateY(-1px);
    }
  }

  .choice-radio,
  .choice-checkbox {
    margin: 0;
    font-size: 15px;
  }

  .choice-image-container {
    padding-left: 28px;

    .choice-image {
      max-width: 240px;
      max-height: 160px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      object-fit: contain;
    }
  }

  .short-answer-entry {
    max-width: 500px;
  }

  .mt-8 {
    margin-top: 8px;
  }

  .mt-12 {
    margin-top: 12px;
  }

  .mt-16 {
    margin-top: 16px;
  }

  .mt-24 {
    margin-top: 24px;
  }

</style>
