<template>

  <div class="h5p-activity-builder">
    <!-- Header: Activity Details & Type Selection -->
    <div
      class="builder-top-bar"
      :style="{
        backgroundColor: $themePalette.grey.v_100,
        border: `1px solid ${$themeTokens.fineLine}`,
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '20px',
      }"
    >
      <div class="row-flex mb-16">
        <div class="flex-grow">
          <KTextbox
            v-model="title"
            :label="titleLabel$()"
            :invalid="Boolean(titleError)"
            :invalidText="titleError"
            :autofocus="true"
          />
        </div>
        <div class="type-select-box">
          <KSelect
            v-model="selectedType"
            :label="activityTypeLabel$()"
            :options="activityTypeOptions"
            :inline="true"
          />
        </div>
      </div>

      <KTextbox
        v-model="description"
        :label="descriptionLabel$()"
        :textArea="true"
        :rows="2"
      />
    </div>

    <!-- Mode Toggles: Edit vs Live Preview -->
    <div
      class="mode-selector mb-16"
      :style="{ borderBottom: `2px solid ${$themeTokens.fineLine}` }"
    >
      <KButton
        :text="editModeLabel$()"
        icon="edit"
        :appearance="activeMode === 'edit' ? 'raised-button' : 'flat-button'"
        :primary="activeMode === 'edit'"
        @click="activeMode = 'edit'"
      />
      <KButton
        :text="previewModeLabel$()"
        icon="preview"
        :appearance="activeMode === 'preview' ? 'raised-button' : 'flat-button'"
        :primary="activeMode === 'preview'"
        @click="activeMode = 'preview'"
      />
    </div>

    <!-- PREVIEW MODE -->
    <div
      v-if="activeMode === 'preview'"
      class="preview-container mb-24"
    >
      <div
        class="preview-header"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
          borderBottom: 'none',
          padding: '10px 16px',
          borderTopLeftRadius: '8px',
          borderTopRightRadius: '8px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }"
      >
        <span :style="{ fontWeight: 'bold', color: $themeTokens.text }">
          {{ previewBannerText$() }}
        </span>
        <KButton
          :text="refreshPreviewLabel$()"
          appearance="flat-button"
          icon="refresh"
          @click="refreshPreview"
        />
      </div>
      <iframe
        :key="previewKey"
        class="preview-iframe"
        :srcdoc="compiledHtml"
        sandbox="allow-scripts allow-same-origin"
        :style="{
          border: `1px solid ${$themeTokens.fineLine}`,
          borderBottomLeftRadius: '8px',
          borderBottomRightRadius: '8px',
          width: '100%',
          height: '520px',
          backgroundColor: '#f8fafc',
        }"
      ></iframe>
    </div>

    <!-- EDIT MODE -->
    <div
      v-else
      class="edit-container"
    >
      <!-- 1. QUIZ / QUESTION SET BUILDER -->
      <div
        v-if="selectedType.value === 'quiz'"
        class="activity-section"
      >
        <div class="section-header mb-16">
          <h3 :style="{ margin: 0, color: $themeTokens.text }">
            {{ quizQuestionsTitle$() }} ({{ questions.length }})
          </h3>
          <KButton
            :text="addQuestionBtn$()"
            icon="plus"
            :primary="true"
            appearance="basic-button"
            @click="addQuestion"
          />
        </div>

        <div
          v-for="(q, qIndex) in questions"
          :key="q.id"
          class="question-card mb-20"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
            borderRadius: '8px',
            padding: '16px',
          }"
        >
          <div class="card-top-bar mb-12">
            <span
              class="badge-pill"
              :style="{
                backgroundColor: $themePalette.grey.v_200,
                color: $themeTokens.text,
                fontWeight: 'bold',
                padding: '4px 10px',
                borderRadius: '16px',
              }"
            >
              {{ questionNumberPrefix$() }} {{ qIndex + 1 }}
            </span>
            <div class="card-controls">
              <KSelect
                v-model="q.type"
                :label="qTypeLabel$()"
                :options="questionTypeOptions"
                :inline="true"
                class="q-type-select"
              />
              <KButton
                v-if="questions.length > 1"
                icon="delete"
                appearance="flat-button"
                :aria-label="removeQuestion$()"
                @click="removeQuestion(qIndex)"
              />
            </div>
          </div>

          <KTextbox
            v-model="q.prompt"
            :label="questionPromptLabel$()"
            class="mb-12"
          />

          <!-- Multiple Choice Options -->
          <div
            v-if="q.type.value === 'multiple_choice'"
            class="options-container mb-12"
          >
            <div class="options-header mb-8">
              <span :style="{ fontWeight: 'bold', color: $themeTokens.annotation, fontSize: '0.9rem' }">
                {{ answerChoicesLabel$() }}
              </span>
            </div>
            <div
              v-for="(opt, optIndex) in q.options"
              :key="opt.id"
              class="option-row mb-8"
            >
              <KCheckbox
                :checked="opt.isCorrect"
                class="correct-checkbox"
                @change="toggleOptionCorrect(q, optIndex)"
              />
              <div class="flex-grow">
                <KTextbox
                  v-model="opt.text"
                  :label="`${optionTextLabel$()} ${optIndex + 1}`"
                />
              </div>
              <KButton
                v-if="q.options.length > 2"
                icon="clear"
                appearance="flat-button"
                @click="removeOption(q, optIndex)"
              />
            </div>
            <KButton
              :text="addChoiceBtn$()"
              icon="plus"
              appearance="flat-button"
              @click="addOption(q)"
            />
          </div>

          <!-- True / False -->
          <div
            v-else-if="q.type.value === 'true_false'"
            class="tf-container mb-12"
          >
            <span :style="{ fontWeight: 'bold', color: $themeTokens.annotation, display: 'block', marginBottom: '8px' }">
              {{ correctAnswerLabel$() }}
            </span>
            <div class="tf-buttons">
              <KButton
                :text="trueLabel$()"
                :appearance="q.tfAnswer === true ? 'raised-button' : 'flat-button'"
                :primary="q.tfAnswer === true"
                @click="q.tfAnswer = true"
              />
              <KButton
                :text="falseLabel$()"
                :appearance="q.tfAnswer === false ? 'raised-button' : 'flat-button'"
                :primary="q.tfAnswer === false"
                @click="q.tfAnswer = false"
              />
            </div>
          </div>

          <!-- Fill in the blank -->
          <div
            v-else-if="q.type.value === 'fill_blank'"
            class="blank-container mb-12"
          >
            <KTextbox
              v-model="q.blankAnswer"
              :label="acceptedAnswerLabel$()"
              :placeholder="blankPlaceholder$()"
            />
          </div>

          <!-- Explanation / Feedback -->
          <KTextbox
            v-model="q.explanation"
            :label="explanationLabel$()"
            :placeholder="explanationPlaceholder$()"
          />
        </div>
      </div>

      <!-- 2. FLASHCARDS BUILDER -->
      <div
        v-else-if="selectedType.value === 'flashcards'"
        class="activity-section"
      >
        <div class="section-header mb-16">
          <h3 :style="{ margin: 0, color: $themeTokens.text }">
            {{ flashcardsTitle$() }} ({{ flashcards.length }})
          </h3>
          <KButton
            :text="addCardBtn$()"
            icon="plus"
            :primary="true"
            appearance="basic-button"
            @click="addFlashcard"
          />
        </div>

        <div
          v-for="(card, cIndex) in flashcards"
          :key="card.id"
          class="card-box mb-16"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
            borderRadius: '8px',
            padding: '16px',
          }"
        >
          <div class="card-top-bar mb-12">
            <span
              class="badge-pill"
              :style="{
                backgroundColor: $themePalette.grey.v_200,
                color: $themeTokens.text,
                fontWeight: 'bold',
                padding: '4px 10px',
                borderRadius: '16px',
              }"
            >
              {{ cardLabel$() }} {{ cIndex + 1 }}
            </span>
            <KButton
              v-if="flashcards.length > 1"
              icon="delete"
              appearance="flat-button"
              :aria-label="removeCard$()"
              @click="removeFlashcard(cIndex)"
            />
          </div>

          <div class="flashcard-fields">
            <KTextbox
              v-model="card.front"
              :label="frontPromptLabel$()"
              :textArea="true"
              :rows="2"
              class="mb-12"
            />
            <KTextbox
              v-model="card.back"
              :label="backAnswerLabel$()"
              :textArea="true"
              :rows="2"
              class="mb-12"
            />
            <KTextbox
              v-model="card.hint"
              :label="hintLabel$()"
              :placeholder="optionalHintPlaceholder$()"
            />
          </div>
        </div>
      </div>

      <!-- 3. DRAG AND DROP MATCHING BUILDER -->
      <div
        v-else-if="selectedType.value === 'drag_drop'"
        class="activity-section"
      >
        <div class="section-header mb-16">
          <h3 :style="{ margin: 0, color: $themeTokens.text }">
            {{ matchingPairsTitle$() }} ({{ matchingPairs.length }})
          </h3>
          <KButton
            :text="addPairBtn$()"
            icon="plus"
            :primary="true"
            appearance="basic-button"
            @click="addMatchingPair"
          />
        </div>

        <div
          v-for="(pair, pIndex) in matchingPairs"
          :key="pair.id"
          class="pair-row mb-16"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
            borderRadius: '8px',
            padding: '16px',
          }"
        >
          <div class="card-top-bar mb-12">
            <span
              class="badge-pill"
              :style="{
                backgroundColor: $themePalette.grey.v_200,
                color: $themeTokens.text,
                fontWeight: 'bold',
                padding: '4px 10px',
                borderRadius: '16px',
              }"
            >
              {{ pairLabel$() }} {{ pIndex + 1 }}
            </span>
            <KButton
              v-if="matchingPairs.length > 2"
              icon="delete"
              appearance="flat-button"
              :aria-label="removePair$()"
              @click="removeMatchingPair(pIndex)"
            />
          </div>

          <div class="pair-inputs">
            <div class="pair-col">
              <KTextbox
                v-model="pair.item"
                :label="draggableItemLabel$()"
                :placeholder="draggablePlaceholder$()"
              />
            </div>
            <div class="pair-arrow">
              <KIcon icon="forward" />
            </div>
            <div class="pair-col">
              <KTextbox
                v-model="pair.target"
                :label="matchingTargetLabel$()"
                :placeholder="targetPlaceholder$()"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>


<script>

  import { ref, computed } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';

  const strings = createTranslator('H5PActivityBuilderStrings', {
    titleLabel: { message: 'Activity Title', context: 'Form label for activity name' },
    activityTypeLabel: { message: 'Activity Type', context: 'Dropdown selector' },
    descriptionLabel: { message: 'Description / Instructions', context: 'Form label' },
    editModeLabel: { message: 'Editor', context: 'Tab toggle' },
    previewModeLabel: { message: 'Interactive Preview', context: 'Tab toggle' },
    previewBannerText: { message: 'Live Learner Preview', context: 'Banner' },
    refreshPreviewLabel: { message: 'Refresh Preview', context: 'Button' },
    quizQuestionsTitle: { message: 'Questions', context: 'Section header' },
    addQuestionBtn: { message: 'Add Question', context: 'Button' },
    questionNumberPrefix: { message: 'Question', context: 'Label' },
    qTypeLabel: { message: 'Type', context: 'Dropdown label' },
    removeQuestion: { message: 'Remove Question', context: 'Tooltip' },
    questionPromptLabel: { message: 'Question Text', context: 'Form label' },
    answerChoicesLabel: { message: 'Answer Choices (Check the correct answer)', context: 'Subheader' },
    optionTextLabel: { message: 'Choice', context: 'Form label' },
    addChoiceBtn: { message: 'Add Choice', context: 'Button' },
    correctAnswerLabel: { message: 'Correct Answer', context: 'Label' },
    trueLabel: { message: 'True', context: 'Button' },
    falseLabel: { message: 'False', context: 'Button' },
    acceptedAnswerLabel: { message: 'Correct Answer Text', context: 'Label' },
    blankPlaceholder: { message: 'e.g. photosynthesis', context: 'Placeholder' },
    explanationLabel: { message: 'Explanation / Feedback (Optional)', context: 'Form label' },
    explanationPlaceholder: { message: 'Shown to the learner after answering', context: 'Placeholder' },
    flashcardsTitle: { message: 'Flashcards', context: 'Section header' },
    addCardBtn: { message: 'Add Card', context: 'Button' },
    cardLabel: { message: 'Card', context: 'Badge label' },
    removeCard: { message: 'Remove Card', context: 'Tooltip' },
    frontPromptLabel: { message: 'Front Side (Prompt / Question)', context: 'Form label' },
    backAnswerLabel: { message: 'Back Side (Answer / Explanation)', context: 'Form label' },
    hintLabel: { message: 'Hint (Optional)', context: 'Form label' },
    optionalHintPlaceholder: { message: 'e.g. Starts with letter P', context: 'Placeholder' },
    matchingPairsTitle: { message: 'Matching Pairs', context: 'Section header' },
    addPairBtn: { message: 'Add Pair', context: 'Button' },
    pairLabel: { message: 'Pair', context: 'Badge label' },
    removePair: { message: 'Remove Pair', context: 'Tooltip' },
    draggableItemLabel: { message: 'Draggable Item', context: 'Form label' },
    draggablePlaceholder: { message: 'e.g. Oxygen', context: 'Placeholder' },
    matchingTargetLabel: { message: 'Matching Target Category', context: 'Form label' },
    targetPlaceholder: { message: 'e.g. Chemical Element', context: 'Placeholder' },
  });

  export default {
    name: 'H5PActivityBuilder',
    setup() {
      const title = ref('');
      const description = ref('');
      const activeMode = ref('edit');
      const previewKey = ref(1);

      const activityTypeOptions = [
        { label: 'Interactive Quiz / Question Set', value: 'quiz' },
        { label: 'Flashcards Deck', value: 'flashcards' },
        { label: 'Drag-and-Drop Matching', value: 'drag_drop' },
      ];
      const selectedType = ref(activityTypeOptions[0]);

      const questionTypeOptions = [
        { label: 'Multiple Choice', value: 'multiple_choice' },
        { label: 'True / False', value: 'true_false' },
        { label: 'Fill in the Blank', value: 'fill_blank' },
      ];

      // Initial Quiz State
      const questions = ref([
        {
          id: 1,
          type: questionTypeOptions[0],
          prompt: 'What is 7 + 8?',
          options: [
            { id: 1, text: '14', isCorrect: false },
            { id: 2, text: '15', isCorrect: true },
            { id: 3, text: '16', isCorrect: false },
            { id: 4, text: '17', isCorrect: false },
          ],
          tfAnswer: true,
          blankAnswer: '',
          explanation: '7 + 8 equals 15.',
        },
      ]);

      // Initial Flashcards State
      const flashcards = ref([
        {
          id: 1,
          front: 'What is the powerhouse of the cell?',
          back: 'Mitochondria',
          hint: 'Produces ATP energy',
        },
        {
          id: 2,
          front: 'What is the speed of light in vacuum?',
          back: 'Approximately 300,000 km/s',
          hint: 'Represented by the letter c',
        },
      ]);

      // Initial Matching State
      const matchingPairs = ref([
        { id: 1, item: 'H2O', target: 'Water' },
        { id: 2, item: 'NaCl', target: 'Table Salt' },
        { id: 3, item: 'CO2', target: 'Carbon Dioxide' },
      ]);

      const titleError = computed(() => {
        if (!title.value.trim()) {
          return 'Title is required';
        }
        return '';
      });

      // Actions for Quiz
      function addQuestion() {
        questions.value.push({
          id: Date.now(),
          type: questionTypeOptions[0],
          prompt: '',
          options: [
            { id: 1, text: '', isCorrect: true },
            { id: 2, text: '', isCorrect: false },
            { id: 3, text: '', isCorrect: false },
            { id: 4, text: '', isCorrect: false },
          ],
          tfAnswer: true,
          blankAnswer: '',
          explanation: '',
        });
      }

      function removeQuestion(index) {
        questions.value.splice(index, 1);
      }

      function addOption(question) {
        question.options.push({
          id: Date.now(),
          text: '',
          isCorrect: false,
        });
      }

      function removeOption(question, optIndex) {
        question.options.splice(optIndex, 1);
      }

      function toggleOptionCorrect(question, optIndex) {
        question.options.forEach((opt, idx) => {
          opt.isCorrect = idx === optIndex;
        });
      }

      // Actions for Flashcards
      function addFlashcard() {
        flashcards.value.push({
          id: Date.now(),
          front: '',
          back: '',
          hint: '',
        });
      }

      function removeFlashcard(index) {
        flashcards.value.splice(index, 1);
      }

      // Actions for Matching
      function addMatchingPair() {
        matchingPairs.value.push({
          id: Date.now(),
          item: '',
          target: '',
        });
      }

      function removeMatchingPair(index) {
        matchingPairs.value.splice(index, 1);
      }

      function refreshPreview() {
        previewKey.value += 1;
      }

      // Compiler to generate offline self-contained HTML/JS interactive app
      const compiledHtml = computed(() => {
        const type = selectedType.value.value;
        const appTitle = title.value.trim() || 'Interactive Activity';
        const appDesc = description.value.trim();

        if (type === 'quiz') {
          const quizData = JSON.stringify(
            questions.value.map(q => ({
              prompt: q.prompt,
              type: q.type.value,
              options: q.options.map(o => ({ text: o.text, isCorrect: o.isCorrect })),
              tfAnswer: q.tfAnswer,
              blankAnswer: q.blankAnswer,
              explanation: q.explanation,
            }))
          );
          return generateQuizAppHtml(appTitle, appDesc, quizData);
        } else if (type === 'flashcards') {
          const cardsData = JSON.stringify(flashcards.value);
          return generateFlashcardsAppHtml(appTitle, appDesc, cardsData);
        } else {
          const pairsData = JSON.stringify(matchingPairs.value);
          return generateDragDropAppHtml(appTitle, appDesc, pairsData);
        }
      });

      const isValid = computed(() => {
        if (!title.value.trim()) {
          return false;
        }
        const type = selectedType.value && selectedType.value.value;
        if (type === 'quiz') {
          return (
            questions.value.length > 0 &&
            questions.value.every(q => q.prompt && q.prompt.trim())
          );
        } else if (type === 'flashcards') {
          return (
            flashcards.value.length > 0 &&
            flashcards.value.every(c => c.front && c.front.trim() && c.back && c.back.trim())
          );
        } else if (type === 'drag_drop') {
          return (
            matchingPairs.value.length >= 2 &&
            matchingPairs.value.every(p => p.item && p.item.trim() && p.target && p.target.trim())
          );
        }
        return true;
      });

      return {
        title,
        description,
        activeMode,
        previewKey,
        selectedType,
        activityTypeOptions,
        questionTypeOptions,
        questions,
        flashcards,
        matchingPairs,
        titleError,
        isValid,
        addQuestion,
        removeQuestion,
        addOption,
        removeOption,
        toggleOptionCorrect,
        addFlashcard,
        removeFlashcard,
        addMatchingPair,
        removeMatchingPair,
        refreshPreview,
        compiledHtml,
        ...strings,
      };
    },
  };

  /**
   * Generates a self-contained, responsive Quiz application.
   */
  function generateQuizAppHtml(title, desc, dataJson) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: #f1f5f9;
      color: #0f172a;
      display: flex;
      justify-content: center;
      padding: 24px 16px;
      min-height: 100vh;
    }
    .quiz-card {
      background: #ffffff;
      max-width: 680px;
      width: 100%;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.06);
      padding: 28px;
      display: flex;
      flex-direction: column;
    }
    .header-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 2px solid #e2e8f0;
    }
    .quiz-title { font-size: 1.35rem; font-weight: 700; color: #1e293b; }
    .progress-pill {
      background: #e0f2fe;
      color: #0369a1;
      padding: 4px 12px;
      border-radius: 20px;
      font-weight: 700;
      font-size: 0.85rem;
    }
    .prompt {
      font-size: 1.15rem;
      font-weight: 600;
      margin-bottom: 20px;
      line-height: 1.5;
    }
    .choice-btn {
      display: flex;
      align-items: center;
      width: 100%;
      text-align: left;
      padding: 14px 16px;
      margin-bottom: 10px;
      border: 2px solid #cbd5e1;
      border-radius: 8px;
      background: #ffffff;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .choice-btn:hover:not(:disabled) {
      border-color: #3b82f6;
      background: #f8fafc;
    }
    .choice-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      background: #f1f5f9;
      font-weight: 700;
      margin-right: 12px;
      flex-shrink: 0;
    }
    .choice-btn.correct {
      border-color: #22c55e;
      background-color: #f0fdf4;
      color: #15803d;
      font-weight: 600;
    }
    .choice-btn.correct .choice-badge {
      background: #22c55e;
      color: white;
    }
    .choice-btn.incorrect {
      border-color: #ef4444;
      background-color: #fef2f2;
      color: #b91c1c;
    }
    .choice-btn.incorrect .choice-badge {
      background: #ef4444;
      color: white;
    }
    .text-input {
      width: 100%;
      padding: 12px 16px;
      font-size: 1.05rem;
      border: 2px solid #cbd5e1;
      border-radius: 8px;
      margin-bottom: 16px;
    }
    .feedback-box {
      padding: 14px;
      border-radius: 8px;
      margin-top: 16px;
      font-size: 0.95rem;
      line-height: 1.4;
    }
    .feedback-box.correct { background: #dcfce7; color: #166534; }
    .feedback-box.incorrect { background: #fee2e2; color: #991b1b; }
    .next-btn {
      margin-top: 20px;
      padding: 12px 24px;
      border: none;
      border-radius: 8px;
      background: #2563eb;
      color: white;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      align-self: flex-end;
    }
    .next-btn:hover { background: #1d4ed8; }
    .score-screen { text-align: center; padding: 32px 16px; }
    .score-circle {
      width: 90px;
      height: 90px;
      border-radius: 50%;
      background: #dcfce7;
      color: #15803d;
      font-size: 2rem;
      font-weight: 800;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
    }
  </style>
</head>
<body>
  <div class="quiz-card" id="app"></div>
  <script>
    const questions = ${dataJson};
    let currentIndex = 0;
    let score = 0;
    let answered = false;

    function renderQuestion() {
      const app = document.getElementById('app');
      if (currentIndex >= questions.length) {
        renderScore();
        return;
      }
      const q = questions[currentIndex];
      answered = false;

      let choicesHtml = '';
      if (q.type === 'multiple_choice') {
        const letters = ['A','B','C','D','E','F'];
        choicesHtml = q.options.map((opt, idx) => \`
          <button class="choice-btn" onclick="selectChoice(\${idx})">
            <span class="choice-badge">\${letters[idx] || (idx+1)}</span>
            <span>\${escapeHtml(opt.text)}</span>
          </button>
        \`).join('');
      } else if (q.type === 'true_false') {
        choicesHtml = \`
          <button class="choice-btn" onclick="selectTf(true)">
            <span class="choice-badge">T</span>
            <span>True</span>
          </button>
          <button class="choice-btn" onclick="selectTf(false)">
            <span class="choice-badge">F</span>
            <span>False</span>
          </button>
        \`;
      } else {
        choicesHtml = \`
          <input type="text" id="blankInput" class="text-input" placeholder="Type your answer here..." onkeydown="if(event.key==='Enter')checkBlank()">
          <button class="next-btn" onclick="checkBlank()" style="align-self: flex-start; margin-top: 0;">Submit Answer</button>
        \`;
      }

      app.innerHTML = \`
        <div class="header-bar">
          <div class="quiz-title">\${escapeHtml("${escapeJsString(title)}")}</div>
          <div class="progress-pill">Question \${currentIndex + 1} of \${questions.length}</div>
        </div>
        <div class="prompt">\${escapeHtml(q.prompt)}</div>
        <div id="choices">\${choicesHtml}</div>
        <div id="feedback"></div>
        <button id="nextBtn" class="next-btn" style="display:none;" onclick="nextQuestion()">Next Question &rarr;</button>
      \`;
    }

    function selectChoice(idx) {
      if (answered) return;
      answered = true;
      const q = questions[currentIndex];
      const buttons = document.querySelectorAll('.choice-btn');
      const isCorrect = q.options[idx].isCorrect;

      buttons.forEach((btn, bIdx) => {
        btn.disabled = true;
        if (q.options[bIdx].isCorrect) {
          btn.classList.add('correct');
        } else if (bIdx === idx) {
          btn.classList.add('incorrect');
        }
      });

      if (isCorrect) score++;
      showFeedback(isCorrect, q.explanation);
    }

    function selectTf(val) {
      if (answered) return;
      answered = true;
      const q = questions[currentIndex];
      const buttons = document.querySelectorAll('.choice-btn');
      const isCorrect = (val === q.tfAnswer);

      buttons.forEach(btn => btn.disabled = true);
      if (isCorrect) {
        score++;
        buttons[val ? 0 : 1].classList.add('correct');
      } else {
        buttons[val ? 0 : 1].classList.add('incorrect');
        buttons[q.tfAnswer ? 0 : 1].classList.add('correct');
      }
      showFeedback(isCorrect, q.explanation);
    }

    function checkBlank() {
      if (answered) return;
      const input = document.getElementById('blankInput');
      if (!input) return;
      const val = input.value.trim().toLowerCase();
      const q = questions[currentIndex];
      const expected = (q.blankAnswer || '').trim().toLowerCase();
      answered = true;
      input.disabled = true;
      const isCorrect = (val === expected);
      if (isCorrect) score++;
      showFeedback(isCorrect, q.explanation || ('Correct answer: ' + q.blankAnswer));
    }

    function showFeedback(isCorrect, explanation) {
      const fb = document.getElementById('feedback');
      fb.className = 'feedback-box ' + (isCorrect ? 'correct' : 'incorrect');
      fb.innerHTML = '<strong>' + (isCorrect ? '&#10004; Correct!' : '&#10008; Incorrect') + '</strong>' +
        (explanation ? '<div style="margin-top:4px;">' + escapeHtml(explanation) + '</div>' : '');
      document.getElementById('nextBtn').style.display = 'block';
    }

    function nextQuestion() {
      currentIndex++;
      renderQuestion();
    }

    function renderScore() {
      const pct = Math.round((score / questions.length) * 100);
      document.getElementById('app').innerHTML = \`
        <div class="score-screen">
          <div class="score-circle">\${pct}%</div>
          <h2 style="margin-bottom:8px;">Activity Completed!</h2>
          <p style="color:#64748b; margin-bottom: 24px;">You scored \${score} out of \${questions.length} questions correctly.</p>
          <button class="next-btn" style="align-self:center;" onclick="restart()">Try Again</button>
        </div>
      \`;
      // Notify parent Kolibri window
      try {
        if (window.parent) {
          window.parent.postMessage({ type: 'KOLIBRI_RESOURCE_COMPLETE', score: pct }, '*');
        }
      } catch (e) {}
    }

    function restart() {
      currentIndex = 0;
      score = 0;
      renderQuestion();
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    renderQuestion();
  <\/script>
</body>
</html>`;
  }

  /**
   * Generates a self-contained, responsive Flashcards application.
   */
  function generateFlashcardsAppHtml(title, desc, dataJson) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: #f8fafc;
      color: #0f172a;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 24px 16px;
    }
    .deck-container {
      background: #ffffff;
      max-width: 580px;
      width: 100%;
      border-radius: 12px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.08);
      padding: 28px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .header-bar {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }
    .deck-title { font-size: 1.25rem; font-weight: 700; color: #1e293b; }
    .progress-badge {
      background: #f1f5f9;
      color: #475569;
      padding: 4px 12px;
      border-radius: 16px;
      font-weight: 600;
      font-size: 0.85rem;
    }
    .flashcard {
      width: 100%;
      min-height: 240px;
      background: #f8fafc;
      border: 2px solid #e2e8f0;
      border-radius: 12px;
      padding: 32px 24px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      cursor: pointer;
      user-select: none;
      transition: all 0.2s ease;
      position: relative;
    }
    .flashcard:hover {
      border-color: #3b82f6;
      box-shadow: 0 6px 16px rgba(59,130,246,0.1);
    }
    .card-side-tag {
      position: absolute;
      top: 12px;
      left: 16px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      color: #94a3b8;
    }
    .card-text {
      font-size: 1.35rem;
      font-weight: 600;
      line-height: 1.5;
      color: #1e293b;
    }
    .card-hint {
      margin-top: 16px;
      font-size: 0.9rem;
      color: #0284c7;
      background: #e0f2fe;
      padding: 4px 12px;
      border-radius: 12px;
    }
    .flip-instruction {
      margin-top: 16px;
      font-size: 0.8rem;
      color: #94a3b8;
    }
    .nav-controls {
      display: flex;
      gap: 12px;
      margin-top: 24px;
      width: 100%;
      justify-content: space-between;
    }
    .nav-btn {
      padding: 10px 20px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      background: #ffffff;
      font-weight: 600;
      cursor: pointer;
    }
    .nav-btn.primary { background: #2563eb; color: white; border: none; }
    .nav-btn:hover { opacity: 0.9; }
    .nav-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  </style>
</head>
<body>
  <div class="deck-container">
    <div class="header-bar">
      <div class="deck-title">${escapeHtml(title)}</div>
      <div id="progress" class="progress-badge"></div>
    </div>
    <div id="flashcard" class="flashcard" onclick="flipCard()">
      <span id="cardSide" class="card-side-tag">Front</span>
      <div id="cardContent" class="card-text"></div>
      <div id="cardHint" class="card-hint" style="display:none;"></div>
      <div class="flip-instruction">Click card to flip</div>
    </div>
    <div class="nav-controls">
      <button id="prevBtn" class="nav-btn" onclick="prevCard()">&larr; Previous</button>
      <button id="flipBtn" class="nav-btn" onclick="flipCard()">Flip</button>
      <button id="nextBtn" class="nav-btn primary" onclick="nextCard()">Next &rarr;</button>
    </div>
  </div>
  <script>
    const cards = ${dataJson};
    let currentIdx = 0;
    let isFlipped = false;

    function renderCard() {
      const card = cards[currentIdx];
      isFlipped = false;
      document.getElementById('progress').innerText = (currentIdx + 1) + ' of ' + cards.length;
      document.getElementById('cardSide').innerText = 'Front';
      document.getElementById('cardContent').innerText = card.front;
      const hintEl = document.getElementById('cardHint');
      if (card.hint) {
        hintEl.style.display = 'inline-block';
        hintEl.innerText = '💡 ' + card.hint;
      } else {
        hintEl.style.display = 'none';
      }
      document.getElementById('prevBtn').disabled = (currentIdx === 0);
      document.getElementById('nextBtn').innerText = (currentIdx === cards.length - 1) ? 'Finish & Complete' : 'Next →';
    }

    function flipCard() {
      const card = cards[currentIdx];
      isFlipped = !isFlipped;
      if (isFlipped) {
        document.getElementById('cardSide').innerText = 'Back';
        document.getElementById('cardContent').innerText = card.back;
        document.getElementById('cardHint').style.display = 'none';
      } else {
        document.getElementById('cardSide').innerText = 'Front';
        document.getElementById('cardContent').innerText = card.front;
        if (card.hint) document.getElementById('cardHint').style.display = 'inline-block';
      }
    }

    function nextCard() {
      if (currentIdx < cards.length - 1) {
        currentIdx++;
        renderCard();
      } else {
        // Complete deck
        try {
          if (window.parent) {
            window.parent.postMessage({ type: 'KOLIBRI_RESOURCE_COMPLETE', score: 100 }, '*');
          }
        } catch (e) {}
        alert('Congratulations! You completed this flashcard deck.');
        currentIdx = 0;
        renderCard();
      }
    }

    function prevCard() {
      if (currentIdx > 0) {
        currentIdx--;
        renderCard();
      }
    }

    renderCard();
  <\/script>
</body>
</html>`;
  }

  /**
   * Generates a self-contained, responsive Drag-and-Drop matching activity.
   */
  function generateDragDropAppHtml(title, desc, dataJson) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: #f1f5f9;
      color: #0f172a;
      display: flex;
      justify-content: center;
      padding: 24px 16px;
      min-height: 100vh;
    }
    .matching-card {
      background: #ffffff;
      max-width: 720px;
      width: 100%;
      border-radius: 12px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.06);
      padding: 28px;
    }
    .header-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 2px solid #e2e8f0;
    }
    .title { font-size: 1.3rem; font-weight: 700; color: #1e293b; }
    .instructions { color: #64748b; font-size: 0.95rem; margin-bottom: 20px; }
    .columns-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    .col-title { font-weight: 700; margin-bottom: 12px; color: #475569; font-size: 0.9rem; text-transform: uppercase; }
    .item-pill {
      background: #ffffff;
      border: 2px solid #cbd5e1;
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 10px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .item-pill:hover { border-color: #3b82f6; background: #f8fafc; }
    .item-pill.selected { border-color: #2563eb; background: #eff6ff; color: #1d4ed8; }
    .item-pill.matched { border-color: #22c55e; background: #f0fdf4; color: #15803d; cursor: default; }
    .target-slot {
      background: #f8fafc;
      border: 2px dashed #cbd5e1;
      padding: 14px 16px;
      border-radius: 8px;
      margin-bottom: 10px;
      min-height: 48px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
    }
    .target-slot:hover { border-color: #94a3b8; }
    .target-slot.active { border-color: #3b82f6; background: #eff6ff; }
    .target-slot.correct { border-style: solid; border-color: #22c55e; background: #f0fdf4; color: #166534; font-weight: 600; }
    .feedback-banner {
      margin-top: 20px;
      padding: 14px;
      border-radius: 8px;
      text-align: center;
      font-weight: 600;
      display: none;
    }
    .feedback-banner.success { background: #dcfce7; color: #15803d; display: block; }
  </style>
</head>
<body>
  <div class="matching-card">
    <div class="header-bar">
      <div class="title">${escapeHtml(title)}</div>
      <div id="counter" style="font-weight:bold; color:#0369a1;"></div>
    </div>
    <div class="instructions">Click an item on the left, then click its corresponding match on the right.</div>
    <div class="columns-grid">
      <div>
        <div class="col-title">Items</div>
        <div id="itemsCol"></div>
      </div>
      <div>
        <div class="col-title">Targets</div>
        <div id="targetsCol"></div>
      </div>
    </div>
    <div id="feedbackBanner" class="feedback-banner"></div>
  </div>
  <script>
    const pairs = ${dataJson};
    let selectedItemIdx = null;
    let matchesCount = 0;

    // Shuffle targets
    const shuffledTargets = pairs.map((p, idx) => ({ target: p.target, origIdx: idx }));
    shuffledTargets.sort(() => Math.random() - 0.5);

    function render() {
      const itemsCol = document.getElementById('itemsCol');
      const targetsCol = document.getElementById('targetsCol');
      document.getElementById('counter').innerText = matchesCount + ' / ' + pairs.length + ' Matched';

      itemsCol.innerHTML = pairs.map((p, idx) => {
        const isMatched = (p.matched === true);
        const isSelected = (selectedItemIdx === idx);
        let cls = 'item-pill';
        if (isMatched) cls += ' matched';
        else if (isSelected) cls += ' selected';
        return '<div class="' + cls + '" onclick="selectItem(' + idx + ')">' +
          '<span>' + escapeHtml(p.item) + '</span>' +
          (isMatched ? '<span>&#10004;</span>' : '') +
        '</div>';
      }).join('');

      targetsCol.innerHTML = shuffledTargets.map((t, idx) => {
        const isMatched = (t.matched === true);
        let cls = 'target-slot';
        if (isMatched) cls += ' correct';
        return '<div class="' + cls + '" onclick="selectTarget(' + idx + ')">' +
          '<span>' + escapeHtml(t.target) + '</span>' +
          (isMatched ? '<span>&#10004;</span>' : '') +
        '</div>';
      }).join('');

      if (matchesCount === pairs.length) {
        const fb = document.getElementById('feedbackBanner');
        fb.className = 'feedback-banner success';
        fb.innerHTML = '&#127881; All pairs matched successfully! Great job!';
        try {
          if (window.parent) {
            window.parent.postMessage({ type: 'KOLIBRI_RESOURCE_COMPLETE', score: 100 }, '*');
          }
        } catch (e) {}
      }
    }

    function selectItem(idx) {
      if (pairs[idx].matched) return;
      selectedItemIdx = idx;
      render();
    }

    function selectTarget(targetIdx) {
      if (selectedItemIdx === null) return;
      const targetObj = shuffledTargets[targetIdx];
      if (targetObj.matched) return;

      if (targetObj.origIdx === selectedItemIdx) {
        // Correct match!
        pairs[selectedItemIdx].matched = true;
        targetObj.matched = true;
        matchesCount++;
        selectedItemIdx = null;
        render();
      } else {
        // Incorrect match flash
        alert('Not a match! Try another pair.');
      }
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    render();
  <\/script>
</body>
</html>`;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function escapeJsString(str) {
    if (!str) return '';
    return String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"');
  }

</script>


<style lang="scss" scoped>

  .h5p-activity-builder {
    padding: 8px 0;
  }

  .row-flex {
    display: flex;
    gap: 16px;
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .flex-grow {
    flex: 1;
    min-width: 260px;
  }

  .type-select-box {
    width: 300px;
  }

  .mode-selector {
    display: flex;
    gap: 8px;
    padding-bottom: 8px;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .card-top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .card-controls {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .q-type-select {
    width: 200px;
  }

  .option-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .correct-checkbox {
    margin-right: 4px;
  }

  .tf-buttons {
    display: flex;
    gap: 12px;
  }

  .pair-inputs {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .pair-col {
    flex: 1;
  }

  .pair-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
  }

  .mb-8 { margin-bottom: 8px; }
  .mb-12 { margin-bottom: 12px; }
  .mb-16 { margin-bottom: 16px; }
  .mb-20 { margin-bottom: 20px; }
  .mb-24 { margin-bottom: 24px; }
  .mt-8 { margin-top: 8px; }
  .mt-12 { margin-top: 12px; }

</style>
