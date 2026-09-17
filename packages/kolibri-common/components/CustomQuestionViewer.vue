<template>

  <div class="custom-question-viewer">
    <!-- Prompt Text & Points Badge -->
    <div
      class="question-prompt"
      :style="{ color: $themeTokens.text }"
    >
      <div
        v-if="question.point_value"
        style="display: flex; align-items: center; margin-bottom: 8px;"
      >
        <span
          :style="{
            backgroundColor: $themePalette.grey.v_200,
            color: $themeTokens.text,
            padding: '4px 10px',
            borderRadius: '12px',
            fontSize: '0.85rem',
            fontWeight: 'bold',
          }"
        >
          {{ question.point_value }} {{ pointValueLabel$() }}
        </span>
      </div>
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
                : preview && selectedOption === option.id && !isOptionCorrect(option.id)
                ? '#ef4444'
                : selectedOption === option.id
                ? $themeTokens.primary
                : $themeTokens.fineLine,
            backgroundColor:
              (preview || showCorrectAnswer) && isOptionCorrect(option.id)
                ? '#f0fdf4'
                : preview && selectedOption === option.id && !isOptionCorrect(option.id)
                ? '#fef2f2'
                : selectedOption === option.id
                ? $themePalette.grey.v_100
                : $themeTokens.surface,
            cursor: preview ? 'default' : 'pointer',
          }"
          @click="selectSingleChoice(option.id)"
        >
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
            <KRadioButton
              :label="option.text || optionFallback$()"
              :buttonValue="option.id"
              :currentValue="selectedOption"
              :disabled="preview"
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
              <span
                v-if="preview && selectedOption === option.id"
                style="margin-left: 4px; color: #15803d;"
              >
                ({{ learnerAnswerLabel$() }})
              </span>
            </span>
            <span
              v-else-if="preview && selectedOption === option.id && !isOptionCorrect(option.id)"
              class="incorrect-badge"
              style="display: flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 600; color: #dc2626;"
            >
              <KIcon
                icon="close"
                style="fill: #dc2626;"
              />
              {{ learnerAnswerLabel$() }}
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
              : preview && isChoiceChecked(option.id) && !isOptionCorrect(option.id)
              ? '#ef4444'
              : isChoiceChecked(option.id)
              ? $themeTokens.primary
              : $themeTokens.fineLine,
          backgroundColor:
            (preview || showCorrectAnswer) && isOptionCorrect(option.id)
              ? '#f0fdf4'
              : preview && isChoiceChecked(option.id) && !isOptionCorrect(option.id)
              ? '#fef2f2'
              : isChoiceChecked(option.id)
              ? $themePalette.grey.v_100
              : $themeTokens.surface,
          cursor: preview ? 'default' : 'pointer',
        }"
        @click="toggleMultiChoice(option.id)"
      >
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
          <KCheckbox
            :label="option.text || optionFallback$()"
            :checked="isChoiceChecked(option.id)"
            :disabled="preview"
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
            <span
              v-if="preview && isChoiceChecked(option.id)"
              style="margin-left: 4px; color: #15803d;"
            >
              ({{ learnerAnswerLabel$() }})
            </span>
          </span>
          <span
            v-else-if="preview && isChoiceChecked(option.id) && !isOptionCorrect(option.id)"
            class="incorrect-badge"
            style="display: flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 600; color: #dc2626;"
          >
            <KIcon
              icon="close"
              style="fill: #dc2626;"
            />
            {{ learnerAnswerLabel$() }}
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
      <div
        v-if="preview && shortAnswerText"
        class="mb-8"
        style="display: flex; align-items: center; gap: 6px; font-weight: bold; margin-bottom: 8px;"
        :style="{ color: isShortAnswerCorrect ? '#15803d' : '#dc2626' }"
      >
        <KIcon :icon="isShortAnswerCorrect ? 'check' : 'close'" />
        <span>{{ isShortAnswerCorrect ? correctAnswerLabel$() : incorrectAnswerLabel$() }}</span>
      </div>
      <KTextbox
        v-model="shortAnswerText"
        :label="yourAnswerLabel$()"
        :placeholder="typeYourAnswerPlaceholder$()"
        :disabled="preview"
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

    <!-- Perseus Interactive Exercise -->
    <div
      v-else-if="question.question_type === 'perseus'"
      class="perseus-question-container mt-16"
    >
      <component
        :is="perseusViewerComponent"
        v-if="perseusViewerComponent && parsedPerseusItem"
        ref="perseusViewerRef"
        :key="perseusKey"
        :itemData="parsedPerseusItem"
        :preset="'exercise'"
        :answerState="perseusAnswerState"
        :interactive="!preview"
        :allowHints="!preview"
        :showCorrectAnswer="showCorrectAnswer"
        @answerGiven="onPerseusAnswerGiven"
        @hintTaken="onPerseusHintTaken"
        @interaction="onPerseusInteraction"
      />
      <div
        v-else-if="parsedPerseusItem"
        class="perseus-static-fallback"
        :style="{
          padding: '16px',
          border: `1px solid ${$themeTokens.fineLine}`,
          borderRadius: '8px',
          backgroundColor: $themePalette.grey.v_100,
        }"
      >
        <div style="font-weight: 600; margin-bottom: 8px;">
          {{ (parsedPerseusItem.question && parsedPerseusItem.question.content) || question.prompt }}
        </div>
      </div>
      <div
        v-else
        class="perseus-error-fallback"
        :style="{ color: $themeTokens.annotation, padding: '12px' }"
      >
        {{ invalidPerseusData$() }}
      </div>
    </div>

    <!-- H5P / Interactive Activity -->
    <div
      v-else-if="isInteractiveQuestion"
      class="interactive-question-container mt-16"
    >
      <!-- Preview Summary Banner for Coach Report -->
      <div
        v-if="preview"
        class="interactive-preview-summary mb-16"
        style="margin-bottom: 16px; padding: 12px 16px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;"
        :style="{
          backgroundColor: interactiveCompleted ? '#f0fdf4' : '#fef2f2',
          border: `1px solid ${interactiveCompleted ? '#bbf7d0' : '#fecaca'}`,
          color: interactiveCompleted ? '#15803d' : '#dc2626',
        }"
      >
        <div style="display: flex; align-items: center; gap: 8px; font-weight: bold; font-size: 15px;">
          <KIcon :icon="interactiveCompleted ? 'check' : 'close'" />
          <span>{{ interactiveCompleted ? activityCompletedLabel$() : activityIncompleteLabel$() }}</span>
        </div>
        <div
          v-if="interactiveScoreText"
          style="font-weight: 600; font-size: 14px; background: rgba(255, 255, 255, 0.7); padding: 4px 10px; border-radius: 6px;"
        >
          {{ scoreLabel$() }}: {{ interactiveScoreText }}
        </div>
      </div>

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

  import Vue, { ref, computed, watch, onMounted, onUnmounted } from 'vue';
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
    activityIncompleteLabel: {
      message: 'Activity Incomplete / Not Attempted',
      context: 'Status badge when learner has not completed interactive task',
    },
    scoreLabel: {
      message: 'Score',
      context: 'Score label in interactive activity preview',
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
    incorrectAnswerLabel: {
      message: 'Incorrect',
      context: 'Status label when answer is incorrect',
    },
    learnerAnswerLabel: {
      message: 'Learner answer',
      context: 'Badge indicating learner selection in preview/review',
    },
    pointValueLabel: {
      message: 'point(s)',
      context: 'Label for point value of question',
    },
    acceptedAnswersLabel: {
      message: 'Accepted answers',
      context: 'Label for correct answers for short answer questions',
    },
    explanationLabel: {
      message: 'Explanation',
      context: 'Heading for explanation box',
    },
    perseusInteractiveLabel: {
      message: 'Perseus Interactive Activity',
      context: 'Label for Perseus activity type',
    },
    invalidPerseusData: {
      message: 'Unable to load interactive Perseus content.',
      context: 'Error message when Perseus JSON cannot be parsed',
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
      function extractAnswerValue(state) {
        if (!state) return null;
        if (typeof state === 'object' && state !== null && 'value' in state) {
          return state.value;
        }
        return state;
      }

      function extractScoreText(state) {
        if (!state) return '';
        if (typeof state === 'object' && state !== null) {
          if (state.simple_answer) return state.simple_answer;
          if (state.score) return state.score;
        }
        return '';
      }

      const initialVal = extractAnswerValue(props.answerState);

      const selectedOption = ref(
        typeof initialVal === 'string' ? initialVal : null,
      );

      const selectedOptions = ref(
        Array.isArray(initialVal) ? [...initialVal] : [],
      );

      const shortAnswerText = ref(
        typeof initialVal === 'string' ? initialVal : '',
      );

      const interactiveCompleted = ref(
        initialVal === 'completed' || Boolean(initialVal),
      );

      const interactiveScoreText = ref(extractScoreText(props.answerState));

      const isShortAnswerCorrect = computed(() => {
        if (!props.question.answer_key) return false;
        const val = (shortAnswerText.value || '').trim();
        if (!val) return false;
        const expected = (props.question.answer_key || []).map(s => (s || '').trim());
        if (props.question.case_sensitive) {
          return expected.includes(val);
        }
        return expected.map(s => s.toLowerCase()).includes(val.toLowerCase());
      });

      const isInteractiveQuestion = computed(() => {
        const q = props.question;
        if (!q) return false;
        const type = (q.question_type || '').toLowerCase();
        if (type === 'perseus') return false;
        return (
          type === 'h5p' ||
          type === 'interactive' ||
          Boolean(q.file_url) ||
          Boolean(q.h5p_content_id) ||
          Boolean(q.h5p_url) ||
          (Boolean(q.content) && type !== 'short_answer')
        );
      });

      const perseusViewerRef = ref(null);
      const latestPerseusAnswer = ref(null);
      const perseusKey = ref(0);

      const perseusViewerComponent = computed(() => {
        if (Vue.options && Vue.options.components) {
          if (Vue.options.components['exercise_viewer']) {
            return 'exercise_viewer';
          }
          if (Vue.options.components['ContentViewer']) {
            return 'ContentViewer';
          }
        }
        return 'ContentViewer';
      });

      const parsedPerseusItem = computed(() => {
        const q = props.question;
        if (!q) return null;
        if (q.item_data && typeof q.item_data === 'object') {
          return q.item_data;
        }
        if (q.content) {
          if (typeof q.content === 'object') {
            return q.content;
          }
          try {
            return JSON.parse(q.content);
          } catch (e) {
            return null;
          }
        }
        return null;
      });

      const perseusAnswerState = computed(() => {
        if (props.showCorrectAnswer) {
          return null;
        }
        if (!props.answerState) return null;
        if (props.answerState.userInput || props.answerState.question) {
          return props.answerState;
        }
        if (props.answerState.value) {
          if (typeof props.answerState.value === 'object') {
            return props.answerState.value;
          }
          try {
            return JSON.parse(props.answerState.value);
          } catch (e) {
            return null;
          }
        }
        return props.answerState;
      });

      function onPerseusAnswerGiven(answer) {
        if (!answer) return;
        latestPerseusAnswer.value = answer;
        emit('interaction');
      }

      function onPerseusHintTaken() {
        emit('interaction');
      }

      function onPerseusInteraction() {
        if (perseusViewerRef.value && typeof perseusViewerRef.value.checkAnswer === 'function') {
          const res = perseusViewerRef.value.checkAnswer();
          if (res) {
            latestPerseusAnswer.value = res;
          }
        }
        emit('interaction');
      }

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
        if (props.preview) return;
        interactiveCompleted.value = !interactiveCompleted.value;
        emit('interaction');
      }

      function onWindowMessage(event) {
        if (!event.data) return;
        let data = event.data;
        if (typeof data === 'string') {
          try {
            data = JSON.parse(data);
          } catch (e) {
            // not a json string
          }
        }
        if (!data) return;

        const isH5pComplete =
          data.type === 'H5P_COMPLETE' ||
          data.type === 'H5P_SCORE' ||
          data.h5p_completed ||
          data.completed;

        const statement = data.statement || (data.data && data.data.statement);
        const verb = statement && statement.verb;
        const verbId = typeof verb === 'object' ? verb.id : verb;
        const isXApiComplete =
          verbId &&
          (verbId === 'http://adlnet.gov/expapi/verbs/completed' ||
            verbId === 'http://adlnet.gov/expapi/verbs/passed' ||
            verbId === 'http://adlnet.gov/expapi/verbs/answered' ||
            (typeof verbId === 'string' &&
              (verbId.includes('completed') ||
                verbId.includes('passed') ||
                verbId.includes('answered'))));

        if (isH5pComplete || isXApiComplete) {
          interactiveCompleted.value = true;
          if (statement && statement.result && statement.result.score) {
            const sc = statement.result.score;
            if (sc.raw !== undefined && sc.max !== undefined) {
              interactiveScoreText.value = `${sc.raw}/${sc.max}`;
            }
          }
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
          if (newVal === undefined || newVal === null) return;
          const val = extractAnswerValue(newVal);
          const score = extractScoreText(newVal);
          if (score) {
            interactiveScoreText.value = score;
          }
          if (
            props.question.question_type === 'multiple_choice' ||
            props.question.question_type === 'true_false'
          ) {
            selectedOption.value = typeof val === 'string' ? val : null;
          } else if (props.question.question_type === 'checkboxes') {
            selectedOptions.value = Array.isArray(val) ? [...val] : [];
          } else if (props.question.question_type === 'short_answer') {
            shortAnswerText.value = typeof val === 'string' ? val : '';
          } else if (
            props.question.question_type === 'h5p' ||
            props.question.question_type === 'interactive' ||
            isInteractiveQuestion.value
          ) {
            interactiveCompleted.value = val === 'completed' || Boolean(val);
          }
        },
      );

      function selectSingleChoice(optId) {
        if (props.preview) return;
        selectedOption.value = optId;
        emit('interaction');
      }

      function toggleMultiChoice(optId) {
        if (props.preview) return;
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
        if (props.preview) return;
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
        } else if (type === 'perseus') {
          if (perseusViewerRef.value && typeof perseusViewerRef.value.checkAnswer === 'function') {
            const res = perseusViewerRef.value.checkAnswer();
            if (res) {
              return res;
            }
          }
          if (latestPerseusAnswer.value) {
            return latestPerseusAnswer.value;
          }
          return {
            answerState: null,
            simpleAnswer: '',
            correct: 0,
          };
        } else if (type === 'h5p' || type === 'interactive' || isInteractiveQuestion.value) {
          const isDone = Boolean(interactiveCompleted.value);
          answerState = isDone ? 'completed' : null;
          simpleAnswer = isDone
            ? (interactiveScoreText.value
                ? `${interactiveScoreText.value} (Completed)`
                : 'Completed')
            : 'In progress';
          isCorrect = isDone;
        }

        return {
          answerState:
            answerState !== null
              ? {
                  value: answerState,
                  type,
                  simple_answer: simpleAnswer,
                }
              : null,
          simpleAnswer,
          correct: isCorrect ? 1 : 0,
        };
      }

      return {
        selectedOption,
        selectedOptions,
        shortAnswerText,
        interactiveCompleted,
        interactiveScoreText,
        isShortAnswerCorrect,
        isInteractiveQuestion,
        resolvedInteractiveUrl,
        perseusViewerRef,
        perseusViewerComponent,
        perseusKey,
        parsedPerseusItem,
        perseusAnswerState,
        onPerseusAnswerGiven,
        onPerseusHintTaken,
        onPerseusInteraction,
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
