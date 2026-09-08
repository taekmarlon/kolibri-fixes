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
      <div
        v-for="option in question.options"
        :key="option.id"
        class="choice-item"
        :class="{ 'is-selected': selectedOption === option.id }"
        :style="{
          borderColor: selectedOption === option.id ? $themeTokens.primary : $themeTokens.fineLine,
          backgroundColor: selectedOption === option.id ? $themePalette.grey.v_100 : $themeTokens.surface,
        }"
        @click="selectSingleChoice(option.id)"
      >
        <KRadioButton
          :label="option.text || optionFallback$()"
          :buttonValue="option.id"
          :currentValue="selectedOption"
          class="choice-radio"
          @input="selectSingleChoice(option.id)"
        />

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
          borderColor: isChoiceChecked(option.id) ? $themeTokens.primary : $themeTokens.fineLine,
          backgroundColor: isChoiceChecked(option.id) ? $themePalette.grey.v_100 : $themeTokens.surface,
        }"
        @click="toggleMultiChoice(option.id)"
      >
        <KCheckbox
          :label="option.text || optionFallback$()"
          :checked="isChoiceChecked(option.id)"
          class="choice-checkbox"
          @change="toggleMultiChoice(option.id)"
          @click.stop="() => {}"
        />

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
    </div>
  </div>

</template>


<script>

  import { ref, watch } from 'vue';
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
  });

  export default {
    name: 'CustomQuestionViewer',
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
        selectSingleChoice,
        toggleMultiChoice,
        isChoiceChecked,
        onShortAnswerChange,
        checkAnswer,
        ...viewerStrings,
      };
    },
    props: {
      question: {
        type: Object,
        required: true,
      },
      answerState: {
        type: [String, Array, Object],
        default: null,
      },
    },
    emits: ['interaction'],
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

  .mt-24 {
    margin-top: 24px;
  }

</style>
