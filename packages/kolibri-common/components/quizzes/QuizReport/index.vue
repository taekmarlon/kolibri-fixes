<template>

  <MultiPaneLayout
    ref="multiPaneLayout"
    class="container"
  >
    <template #header>
      <KGrid
        class="page-status"
        :style="{ backgroundColor: $themeTokens.surface }"
      >
        <KGridItem
          v-if="windowIsSmall"
          :layout4="{ span: 4, alignment: 'right' }"
        >
          <slot name="actions"></slot>
        </KGridItem>
        <KGridItem
          :layout12="{ span: 9, alignment: 'left' }"
          :layout8="{ span: 5, alignment: 'left' }"
          :layout4="{ span: 4, alignment: 'left' }"
        >
          <div>
            <h1
              v-if="userId"
              class="title"
            >
              <KLabeledIcon
                icon="person"
                :label="userName"
              />
            </h1>
            <KLabeledIcon
              :icon="titleIcon"
              :label="title"
            />
          </div>
          <!-- only show the current try if the user has only one try or if its a survey -->
          <TriesOverview
            v-if="pastTries.length > 1 && !isSurvey"
            :pastTries="pastTries"
            :totalQuestions="questions.length"
            :suggestedTime="duration"
            :isSurvey="isSurvey"
          />
          <CurrentTryOverview
            v-else-if="currentTry"
            :userId="userId"
            :currentTry="currentTry"
            :totalQuestions="questions.length"
            :isSurvey="isSurvey"
          />
        </KGridItem>
        <KGridItem
          v-if="!windowIsSmall"
          :layout12="{ span: 3, alignment: 'right' }"
          :layout8="{ span: 3, alignment: 'right' }"
          :layout="{ span: 2, alignment: 'right' }"
        >
          <slot name="actions"></slot>
        </KGridItem>
      </KGrid>
    </template>

    <template
      v-if="!loading"
      #subheader
    >
      <KSelect
        v-if="pastTries.length > 1"
        :value="pastTriesOptions[tryIndex]"
        :label="$tr('attemptDropdownLabel')"
        :options="pastTriesOptions"
        :style="{ background: $themePalette.grey.v_200 }"
        appearance="flat-button"
        class="try-selection"
        @change="navigateToTry"
      />
      <CurrentTryOverview
        v-if="currentTry && pastTries.length > 1 && currentTry.attemptlogs.length"
        :userId="userId"
        :currentTry="currentTry"
        :totalQuestions="questions.length"
        :hideStatus="true"
        :isSurvey="isSurvey"
      />
    </template>

    <template
      v-if="!windowIsSmall && !loading && currentTry && currentTry.attemptlogs.length"
      #aside
    >
      <AttemptLogList
        :attemptLogs="attemptLogs"
        :selectedQuestionNumber="questionNumber"
        :isSurvey="isSurvey"
        :sections="annotatedSections"
        :currentSectionIndex="currentSectionIndex"
        @select="navigateToQuestion"
      />
    </template>

    <template
      v-if="currentTry && currentTry.attemptlogs.length"
      #main
    >
      <KCircularLoader
        v-if="loading"
        class="loader"
      />
      <template v-else-if="itemId">
        <AttemptLogList
          v-if="windowIsSmall"
          class="mobile-attempt-log-list"
          :isMobile="true"
          :attemptLogs="attemptLogs"
          :selectedQuestionNumber="questionNumber"
          :isSurvey="isSurvey"
          :sections="annotatedSections"
          :currentSectionIndex="currentSectionIndex"
          @select="navigateToQuestion"
        />
        <div
          v-if="exercise && exercise.available"
          class="exercise-container"
          :class="windowIsSmall ? 'mobile-exercise-container' : ''"
          :style="{ backgroundColor: $themeTokens.surface }"
        >
          <h3 v-if="questionNumberInSectionLabel">{{ questionNumberInSectionLabel }}</h3>

          <p v-if="currentSection && currentSection.description">
            {{ currentSection.description }}
          </p>

          <div
            v-if="!isSurvey"
            data-testid="diff-business"
          >
            <KCheckbox
              :label="coreString('showCorrectAnswerLabel')"
              :checked="showCorrectAnswer"
              @change="toggleShowCorrectAnswer"
            />
            <div
              v-if="currentAttemptDiff"
              style="padding-bottom: 15px"
            >
              <AttemptIconDiff
                :correct="currentAttempt.correct"
                :diff="currentAttemptDiff.correct"
              />
              <AttemptTextDiff
                :userId="userId"
                :correct="currentAttempt.correct"
                :diff="currentAttemptDiff.correct"
              />
            </div>
            <InteractionList
              v-if="!showCorrectAnswer"
              :interactions="currentInteractionHistory"
              :selectedInteractionIndex="selectedInteractionIndex"
              :reverse="reverseInteractions"
              @select="navigateToQuestionAttempt"
            />
          </div>
          <ContentViewer
            :itemId="renderableItemId"
            :allowHints="false"
            :files="exercise.files"
            :extraFields="exercise.extra_fields"
            :interactive="false"
            :assessment="true"
            :answerState="answerState"
            :showCorrectAnswer="showCorrectAnswer"
          />
        </div>
        <div
          v-else-if="currentQuestionIsCustom"
          class="exercise-container"
          :class="windowIsSmall ? 'mobile-exercise-container' : ''"
          :style="{ backgroundColor: $themeTokens.surface, padding: '24px' }"
        >
          <h3 v-if="questionNumberInSectionLabel">{{ questionNumberInSectionLabel }}</h3>

          <p v-if="currentSection && currentSection.description">
            {{ currentSection.description }}
          </p>

          <div
            v-if="!isSurvey"
            data-testid="diff-business"
          >
            <KCheckbox
              :label="coreString('showCorrectAnswerLabel')"
              :checked="showCorrectAnswer"
              @change="toggleShowCorrectAnswer"
            />
            <div
              v-if="currentAttemptDiff"
              style="padding-bottom: 15px"
            >
              <AttemptIconDiff
                :correct="currentAttempt.correct"
                :diff="currentAttemptDiff.correct"
              />
              <AttemptTextDiff
                :userId="userId"
                :correct="currentAttempt.correct"
                :diff="currentAttemptDiff.correct"
              />
            </div>
          </div>

          <!-- Custom Question Content Review -->
          <div class="custom-question-report-content mt-16">
            <!-- Points badge and Status -->
            <div
              class="report-meta mb-16"
              style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;"
            >
              <span
                v-if="currentQuestion.point_value"
                :style="{
                  backgroundColor: $themePalette.grey.v_200,
                  color: $themeTokens.text,
                  padding: '4px 10px',
                  borderRadius: '12px',
                  fontSize: '0.85rem',
                  fontWeight: 'bold',
                }"
              >
                {{ currentQuestion.point_value }} {{ pointValueLabel$() }}
              </span>
              <span
                :style="{
                  backgroundColor: currentAttempt && currentAttempt.correct ? '#ecfdf5' : '#fef2f2',
                  color: currentAttempt && currentAttempt.correct ? '#059669' : '#dc2626',
                  padding: '4px 10px',
                  borderRadius: '12px',
                  fontSize: '0.85rem',
                  fontWeight: 'bold',
                }"
              >
                {{ currentAttempt && currentAttempt.correct ? correctLabel$() : incorrectLabel$() }}
              </span>
            </div>

            <!-- Question Prompt -->
            <h4 :style="{ color: $themeTokens.text, fontSize: '1.15rem', marginBottom: '16px' }">
              {{ currentQuestion.prompt || currentQuestion.title }}
            </h4>

            <!-- Prompt image -->
            <div
              v-if="currentQuestion.prompt_image"
              style="margin-bottom: 20px; text-align: center;"
            >
              <img
                :src="currentQuestion.prompt_image"
                alt="Question illustration"
                style="max-width: 100%; max-height: 380px; border-radius: 8px; border: 1px solid #e2e8f0;"
              >
            </div>

            <!-- Choices list for multiple choice, true/false, checkboxes -->
            <div
              v-if="currentQuestion.options && currentQuestion.options.length"
              class="custom-choices-review"
            >
              <div
                v-for="opt in currentQuestion.options"
                :key="opt.id"
                class="choice-review-item"
                :style="{
                  padding: '12px 16px',
                  borderRadius: '8px',
                  marginBottom: '10px',
                  border: isChoiceSelectedByLearner(opt.id)
                    ? `2px solid ${$themeTokens.primary}`
                    : `1px solid ${$themeTokens.fineLine}`,
                  backgroundColor:
                    isChoiceCorrect(opt.id) &&
                    (showCorrectAnswer || !currentAttempt || !currentAttempt.correct)
                      ? '#f0fdf4'
                      : isChoiceSelectedByLearner(opt.id) && !isChoiceCorrect(opt.id)
                      ? '#fef2f2'
                      : $themeTokens.surface,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }"
              >
                <div style="display: flex; align-items: center; gap: 10px;">
                  <KIcon
                    v-if="
                      isChoiceCorrect(opt.id) &&
                      (showCorrectAnswer || !currentAttempt || !currentAttempt.correct)
                    "
                    icon="correct"
                    style="color: #059669;"
                  />
                  <KIcon
                    v-else-if="isChoiceSelectedByLearner(opt.id)"
                    icon="incorrect"
                    style="color: #dc2626;"
                  />
                  <span :style="{ fontWeight: isChoiceSelectedByLearner(opt.id) ? 'bold' : 'normal' }">
                    {{ opt.text }}
                  </span>
                </div>
                <div>
                  <span
                    v-if="isChoiceSelectedByLearner(opt.id)"
                    :style="{
                      fontSize: '0.8rem',
                      fontWeight: 'bold',
                      color: $themeTokens.primary,
                      marginRight: '8px',
                    }"
                  >
                    {{ learnerAnswerBadge$() }}
                  </span>
                  <span
                    v-if="isChoiceCorrect(opt.id) && showCorrectAnswer"
                    :style="{
                      fontSize: '0.8rem',
                      fontWeight: 'bold',
                      color: '#059669',
                    }"
                  >
                    {{ correctAnswerBadge$() }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Short Answer Review -->
            <div
              v-else-if="currentQuestion.question_type === 'short_answer'"
              class="short-answer-review"
            >
              <div
                :style="{
                  padding: '14px',
                  borderRadius: '8px',
                  backgroundColor: currentAttempt && currentAttempt.correct ? '#f0fdf4' : '#fef2f2',
                  border: `1px solid ${$themeTokens.fineLine}`,
                  marginBottom: '12px',
                }"
              >
                <div
                  style="font-weight: bold; margin-bottom: 4px;"
                  :style="{ color: $themeTokens.annotation }"
                >
                  {{ learnerAnswerBadge$() }}:
                </div>
                <div :style="{ fontSize: '1.05rem', fontWeight: 'bold' }">
                  {{ currentLearnerAnswerText || noAnswerSubmitted$() }}
                </div>
              </div>
              <div
                v-if="showCorrectAnswer || (currentAttempt && !currentAttempt.correct)"
                :style="{
                  padding: '14px',
                  borderRadius: '8px',
                  backgroundColor: '#f0fdf4',
                  border: '1px solid #bbf7d0',
                }"
              >
                <div style="font-weight: bold; margin-bottom: 4px; color: #059669;">
                  {{ correctAnswerBadge$() }}:
                </div>
                <div style="font-size: 1.05rem; font-weight: bold; color: #065f46;">
                  {{ (currentQuestion.answer_key || []).join(' / ') }}
                </div>
              </div>
            </div>

            <!-- Interactive Activity Review -->
            <div
              v-else-if="isInteractiveQuestion(currentQuestion)"
              class="interactive-activity-review"
            >
              <iframe
                v-if="currentQuestion.file_url || currentQuestion.h5p_url || currentQuestion.h5p_content_id"
                :src="currentQuestion.file_url || currentQuestion.h5p_url || (currentQuestion.h5p_content_id ? `/h5p/play/${currentQuestion.h5p_content_id}` : '')"
                style="width: 100%; min-height: 480px; border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff;"
                sandbox="allow-scripts allow-same-origin"
                allow="fullscreen; geolocation; microphone; camera; midi"
              ></iframe>
              <iframe
                v-else-if="currentQuestion.content"
                :srcdoc="currentQuestion.content"
                style="width: 100%; min-height: 480px; border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff;"
                sandbox="allow-scripts allow-same-origin"
                allow="fullscreen; geolocation; microphone; camera; midi"
              ></iframe>
            </div>

            <!-- Explanation (if provided) -->
            <div
              v-if="
                currentQuestion.explanation &&
                (showCorrectAnswer || (currentAttempt && !currentAttempt.correct))
              "
              class="explanation-box mt-16"
              :style="{
                backgroundColor: $themePalette.grey.v_100,
                border: `1px solid ${$themeTokens.fineLine}`,
                borderRadius: '8px',
                padding: '14px',
                marginTop: '16px',
              }"
            >
              <div
                style="font-weight: bold; margin-bottom: 4px;"
                :style="{ color: $themeTokens.annotation }"
              >
                {{ explanationLabel$() }}:
              </div>
              <p style="margin: 0;">{{ currentQuestion.explanation }}</p>
            </div>
          </div>
        </div>
        <MissingResourceAlert
          v-else
          :multiple="false"
        />
      </template>

      <p v-else>
        {{ $tr('noItemId') }}
      </p>
    </template>
  </MultiPaneLayout>

</template>


<script>

  import sortBy from 'lodash/sortBy';
  import isFinite from 'lodash/isFinite';
  import isNumber from 'lodash/isNumber';
  import isString from 'lodash/isString';
  import InteractionList from 'kolibri-common/components/quizzes/InteractionList';
  import find from 'lodash/find';
  import MultiPaneLayout from 'kolibri-common/components/MultiPaneLayout';
  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';
  import useKResponsiveWindow from 'kolibri-design-system/lib/composables/useKResponsiveWindow';
  import MasteryLogResource from 'kolibri-common/apiResources/MasteryLogResource';
  import useNow from 'kolibri/composables/useNow';
  import { createTranslator } from 'kolibri/utils/i18n';
  import { annotateSections, isCustomQuestion } from 'kolibri-common/quizzes/utils';
  import MissingResourceAlert from 'kolibri-common/components/MissingResourceAlert';
  import { displaySectionTitle } from 'kolibri-common/strings/enhancedQuizManagementStrings';
  import AttemptLogList from './AttemptLogList';
  import AttemptTextDiff from './AttemptTextDiff';
  import AttemptIconDiff from './AttemptIconDiff';
  import TriesOverview from './TriesOverview';
  import CurrentTryOverview from './CurrentTryOverview';

  const customQuizReportStrings = createTranslator('CustomQuizReportStrings', {
    pointValueLabel: {
      message: 'pts',
      context: 'Abbreviation for points',
    },
    correctLabel: {
      message: 'Correct',
      context: 'Status for correct answer',
    },
    incorrectLabel: {
      message: 'Incorrect',
      context: 'Status for incorrect answer',
    },
    learnerAnswerBadge: {
      message: "Learner's answer",
      context: 'Badge for learner answer',
    },
    correctAnswerBadge: {
      message: 'Correct answer',
      context: 'Badge for correct answer',
    },
    noAnswerSubmitted: {
      message: 'No answer submitted',
      context: 'Placeholder text when learner did not answer',
    },
    explanationLabel: {
      message: 'Explanation',
      context: 'Label for question explanation',
    },
  });

  export default {
    name: 'QuizReport',
    components: {
      AttemptLogList,
      InteractionList,
      MultiPaneLayout,
      AttemptIconDiff,
      AttemptTextDiff,
      TriesOverview,
      CurrentTryOverview,
      MissingResourceAlert,
    },
    mixins: [commonCoreStrings],
    setup() {
      const { windowIsSmall } = useKResponsiveWindow();
      const { now } = useNow();
      return {
        windowIsSmall,
        now,
        ...customQuizReportStrings,
      };
    },
    props: {
      // Unique identifier of the item for the report
      // this will be used to filter for previous tries
      contentId: {
        type: String,
        required: true,
      },
      // The title of the item
      title: {
        type: String,
        required: true,
      },
      // The suggested duration of the item in seconds
      duration: {
        type: Number,
        default: null,
      },
      // The user id of the user for the report
      // Let it be null to handle anonymous users
      // with just the title and action bar.
      userId: {
        type: String,
        default: null,
      },
      // The name of the user for the report
      userName: {
        type: String,
        required: true,
      },
      // Which specific interaction within an attempt to show
      selectedInteractionIndex: {
        type: Number,
        required: true,
      },
      // Which specific question within a try to show
      // A zero based index
      // For quiz type assessments, this is the specific question number
      // For exercise type assessments, 0 is the most recent attempt in the try
      questionNumber: {
        type: Number,
        required: true,
      },
      // Which 'try' to show - this is a zero based index with 0 being the most recent.
      // To the user we describe this as an 'attempt' but to avoid confusion with the
      // attempt logs that describe a users interaction with a specific question, we
      // refer to this as a 'try'
      tryIndex: {
        type: Number,
        default: 0,
      },
      // An object containing all of the content metadata for the item.
      // We allow this to be empty to accommodate missing resources
      exercise: {
        type: Object,
        default: null,
      },
      // A function that has the signature tryIndex, questionNumber, interactionIndex
      // this should handle changes to the three parameters above.
      navigateTo: {
        type: Function,
        required: true,
      },
      // The exam.question_sources value
      sections: {
        type: Array,
        required: false,
        default: null,
      },
      // An array of questions in the format:
      // {
      //   exercise_id: <exercise_id>,
      //   question_id: <item id for question>,
      //   title: <title to use when displaying the question>,
      //   counter_in_exercise: <zero based index of question in exercise>,
      //   item: <a unique identifier for the question>
      // }
      // The question_id and item are identical for non-coach assigned/generated quizzes
      // for coach generated quizzes, we currently use a concatenation of the exercise_id
      // and question_id in order to generate a globally unique item identifier:
      // <exercise_id>:<question_id>
      // in case two exercises have a colliding question_id.
      // For exercises and practice quizzes there is no risk of collision, so this is not done.
      questions: {
        type: Array,
        required: true,
        validator: questions => {
          return questions.every(question => {
            return (
              isString(question.exercise_id) &&
              isString(question.question_id) &&
              isNumber(question.counter_in_exercise) &&
              isString(question.title) &&
              isString(question.item)
            );
          });
        },
      },
      // An array containing all of the content metadata for the item.
      // Note: this is only really needed for coach assigned quizzes
      // for exercises and practice quizzes, this is just the exercise prop
      // wrapped in an array.
      // TODO: Add general purpose content node validator here.
      exerciseContentNodes: {
        type: Array,
        default: () => [],
      },
      // Is this a coach assigned quiz or a practice quiz?
      // This is used to determine the ordering of displayed attempts
      // For quizzes it's by question number, for non-quizzes it's by most recent attempt
      // and whether to show non-attempted questions.
      isQuiz: {
        type: Boolean,
        default: true,
      },
      // Is this.content a survey modality?
      isSurvey: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        showCorrectAnswer: false,
        pastTries: [],
        currentTry: null,
        loading: true,
      };
    },
    computed: {
      annotatedSections() {
        return annotateSections(this.sections, this.questions);
      },
      currentSectionIndex() {
        return this.annotatedSections.findIndex(
          section =>
            this.questionNumber >= section.startQuestionNumber &&
            this.questionNumber <= section.endQuestionNumber,
        );
      },
      currentSection() {
        return this.annotatedSections[this.currentSectionIndex];
      },
      questionNumberInSectionLabel() {
        const questionLabel = this.coreString('questionNumberLabel', {
          questionNumber: this.questionNumber + 1,
        });
        if (this.annotatedSections.length === 1) {
          return questionLabel;
        }
        const sectionLabel = displaySectionTitle(this.currentSection, this.currentSectionIndex);
        return `${sectionLabel} - ${questionLabel}`;
      },
      attemptLogs() {
        if (this.isQuiz || this.isSurvey) {
          return this.quizAttempts();
        }
        return this.masteryAttempts();
      },
      answerState() {
        // Do not pass in answerState if showCorrectAnswer is set to true
        // answerState has a precedence over showCorrectAnswer
        if (
          !this.showCorrectAnswer &&
          this.currentInteraction &&
          this.currentInteraction.type === 'answer'
        ) {
          return this.currentInteraction.answer;
        }
        return null;
      },
      currentAttempt() {
        return this.attemptLogs.find(a => a.item === this.itemId);
      },
      currentAttemptDiff() {
        return this.currentAttempt &&
          this.currentAttempt.diff &&
          this.currentAttempt.diff.correct !== null
          ? this.currentAttempt.diff
          : null;
      },
      pastTriesOptions() {
        return this.pastTries.map((quizTry, index) => {
          const rawScore = quizTry.correct / this.questions.length;
          const score = this.$formatNumber(rawScore, { style: 'percent' });
          const time = this.$formatRelative(quizTry.completion_timestamp || quizTry.end_timestamp, {
            now: this.now,
          });

          return {
            value: index,
            label: this.isSurvey ? time : `(${score}) ${time}`,
          };
        });
      },
      itemId() {
        return this.isQuiz || this.isSurvey
          ? this.questions[this.questionNumber].item
          : this.attemptLogs[this.questionNumber].item;
      },
      renderableItemId() {
        // This item value is used to pass into ContentViewer to set the correct question,
        // so reclaim the actual item id value here by splitting on ':'.
        // This is only needed in cases where the item id has been artificially generated for coach
        // assigned quizzes.
        return this.itemId.split(':')[1] || this.itemId;
      },
      currentInteractionHistory() {
        // filter out interactions without answers but keep hints and errors
        return this.currentAttempt
          ? this.currentAttempt.interaction_history.filter(interaction =>
            Boolean(
              interaction.answer || interaction.type === 'hint' || interaction.type === 'error',
            ),
          ) || []
          : [];
      },
      reverseInteractions() {
        return this.isQuiz || this.isSurvey;
      },
      currentInteraction() {
        if (!this.currentInteractionHistory) {
          return null;
        }
        const history = this.reverseInteractions
          ? this.currentInteractionHistory.toReversed()
          : this.currentInteractionHistory;
        return history[this.selectedInteractionIndex];
      },
      currentQuestion() {
        return this.questions && this.questions[this.questionNumber];
      },
      currentQuestionIsCustom() {
        return Boolean(this.currentQuestion && isCustomQuestion(this.currentQuestion));
      },
      currentLearnerAnswerText() {
        if (!this.currentAttempt || this.currentAttempt.answer == null) return '';
        if (typeof this.currentAttempt.answer === 'string') {
          return this.currentAttempt.answer;
        }
        return this.currentAttempt.simple_answer || '';
      },
      titleIcon() {
        if (this.isSurvey) {
          return 'reflectSolid';
        }
        return this.isQuiz ? 'quiz' : (this.exercise ? this.exercise.kind : 'document');
      },
    },
    watch: {
      tryIndex(newVal, oldVal) {
        if (newVal !== oldVal) {
          this.loadAttempts();
        }
      },
    },
    created() {
      if (this.userId) {
        this.loadAttempts();
        this.loadAllTries();
      }
    },
    methods: {
      isChoiceSelectedByLearner(optId) {
        if (!this.currentAttempt || this.currentAttempt.answer == null) return false;
        if (Array.isArray(this.currentAttempt.answer)) {
          return this.currentAttempt.answer.includes(optId);
        }
        return this.currentAttempt.answer === optId;
      },
      isChoiceCorrect(optId) {
        if (!this.currentQuestion || !this.currentQuestion.answer_key) return false;
        return this.currentQuestion.answer_key.includes(optId);
      },
      isInteractiveQuestion(q) {
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
      },
      navigateToQuestion(questionNumber) {
        if (questionNumber !== this.questionNumber) {
          this.navigateTo(this.tryIndex, questionNumber, 0);
          this.$refs.multiPaneLayout.scrollMainToTop();
          this.showCorrectAnswer = false;
        }
      },
      navigateToQuestionAttempt(interaction) {
        if (interaction !== this.selectedInteractionIndex) {
          this.navigateTo(this.tryIndex, this.questionNumber, interaction);
          this.$refs.multiPaneLayout.scrollMainToTop();
          this.showCorrectAnswer = false;
        }
      },
      navigateToTry(tryOption) {
        if (tryOption.value !== this.tryIndex) {
          this.navigateTo(tryOption.value, 0, 0);
          this.$refs.multiPaneLayout.scrollMainToTop();
          this.showCorrectAnswer = false;
        }
      },
      toggleShowCorrectAnswer() {
        this.showCorrectAnswer = !this.showCorrectAnswer;
        this.$forceUpdate();
      },
      getParams() {
        return {
          content: this.contentId,
          user: this.userId,
          back: this.tryIndex,
          quiz: this.isQuiz,
        };
      },
      loadAttempts() {
        if (!isFinite(this.tryIndex)) {
          return;
        }
        this.loading = true;
        MasteryLogResource.fetchMostRecentDiff(this.getParams())
          .then(currentTry => {
            this.currentTry = currentTry;
            this.loading = false;
          })
          .catch(err => {
            if (err.response && err.response.status_code === 404) {
              this.$emit('noCompleteTries');
            }
            this.loading = false;
          });
      },
      loadAllTries() {
        MasteryLogResource.fetchCollection({ getParams: this.getParams(), force: true }).then(
          pastTries => {
            this.pastTries = pastTries;
          },
        );
      },
      quizAttempts() {
        const mostRecentAttempts = sortBy(
          this.currentTry ? this.currentTry.attemptlogs : [],
          'end_timestamp',
        ).reverse();
        return sortBy(
          this.questions.map((question, index) => {
            const attempt = mostRecentAttempts.find(a => a.item === question.item);
            const questionNumber = index + 1;
            const noattempt = !attempt;
            let num_coach_contents;
            let missing_resource = true;
            if (this.exerciseContentNodes.length) {
              const exerciseId = this.questions[questionNumber - 1].exercise_id;
              const exerciseMatch = find(this.exerciseContentNodes, { id: exerciseId });
              if (exerciseMatch) {
                num_coach_contents = exerciseMatch.num_coach_contents;
                missing_resource = false;
              }
            }
            return {
              ...(attempt || {}),
              noattempt,
              questionNumber,
              num_coach_contents,
              missing_resource,
            };
          }),
          'questionNumber',
        );
      },
      masteryAttempts() {
        return sortBy(this.currentTry ? this.currentTry.attemptlogs : [], 'end_timestamp')
          .reverse()
          .map(attempt => {
            const questionNumber = this.questions.findIndex(q => q.item === attempt.item) + 1;
            let num_coach_contents;
            let missing_resource = true;
            if (this.exerciseContentNodes.length) {
              const exerciseId = this.questions[questionNumber - 1].exercise_id;
              const exerciseMatch = find(this.exerciseContentNodes, { id: exerciseId });
              if (exerciseMatch) {
                num_coach_contents = exerciseMatch.num_coach_contents;
                missing_resource = false;
              }
            }
            return {
              ...attempt,
              questionNumber,
              num_coach_contents,
              missing_resource,
            };
          });
      },
    },
    $trs: {
      noItemId: {
        message: 'This question has an error, please move on to the next question',
        context:
          'Message that a coach would see in a report that indicates that there is an error in one of the questions in a quiz.',
      },
      attemptDropdownLabel: {
        message: 'Attempt',
        context:
          'Label in the dropdown menu where one can choose an attempt from their five most recent attempts at a practice quiz',
      },
    },
  };

</script>


<style lang="scss" scoped>

  .exercise-container {
    padding: 8px;
  }

  .container {
    max-width: 1000px;
    margin: 0 auto;
    background-color: white;
  }

  .mobile-exercise-container {
    margin-top: 16px;
  }

  .mobile-attempt-log-list {
    margin-top: 16px;
  }

  h3 {
    margin-top: 0;
  }

  .try-selection {
    max-width: 400px;
    padding: 8px 8px 0;
    margin-top: 16px;
  }

  .loader {
    padding-top: 64px;
    padding-bottom: 64px;
  }

  th {
    text-align: left;
  }

  th,
  td {
    height: 2em;
    padding-right: 24px;
    font-size: 14px;
  }

</style>
