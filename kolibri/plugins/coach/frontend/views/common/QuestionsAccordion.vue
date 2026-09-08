<template>

  <AccordionContainer>
    <template #header="{ canExpandAll, expandAll, canCollapseAll, collapseAll }">
      <div class="questions-accordion-header">
        <div>
          <KCheckbox
            v-if="isSelectable"
            ref="selectAllCheckbox"
            :class="['select-all-box', { 'select-all-box-sortable': isSortable }]"
            :label="selectAllLabel$()"
            :disabled="selectAllIsDisabled"
            :checked="selectAllIsChecked"
            :indeterminate="selectAllIsIndeterminate"
            @change="handleSelectAll"
            @click.stop="() => {}"
          />
        </div>
        <div class="trailing-actions">
          <KIconButton
            icon="expandAll"
            :tooltip="expandAll$()"
            :disabled="!canExpandAll"
            @click="expandAll"
          />
          <KIconButton
            icon="collapseAll"
            :tooltip="collapseAll$()"
            :disabled="!canCollapseAll"
            @click="collapseAll"
          />
          <slot name="header-trailing-actions"></slot>
        </div>
      </div>
    </template>

    <DragContainer
      key="drag-container"
      :items="questions"
      @sort="handleQuestionOrderChange"
      @dragStart="handleDragStart"
    >
      <transition-group
        tag="div"
        name="list"
      >
        <Draggable
          v-for="(question, index) in questions"
          :key="`drag-${question.item}`"
          tabindex="-1"
          :style="{
            background: $themeTokens.surface,
          }"
        >
          <AccordionItem
            :title="getDisplayQuestionTitle(question, getQuestionContent(question)?.title)"
            :disabledTitle="questionItemsToReplace?.includes(question.item)"
            :aria-selected="questionIsChecked(question)"
            :headerAppearanceOverrides="{
              userSelect: dragActive ? 'none !important' : 'text',
            }"
          >
            <template #leading-actions>
              <DragHandle v-if="isSortable">
                <div>
                  <DragSortWidget
                    :noDrag="true"
                    :isFirst="index === 0"
                    :isLast="index === questions.length - 1"
                    :itemLabel="
                      getDisplayQuestionTitle(question, getQuestionContent(question)?.title)
                    "
                    :position="index + 1"
                    :total="questions.length"
                    @moveUp="() => handleKeyboardDragUp(index)"
                    @moveDown="() => handleKeyboardDragDown(index)"
                  />
                </div>
              </DragHandle>
              <KCheckbox
                v-if="isSelectable"
                class="accordion-item-checkbox"
                :checked="questionIsChecked(question)"
                :disabled="questionCheckboxDisabled(question)"
                @change="
                  (value, $event) => handleQuestionCheckboxChange(question.item, value, $event)
                "
              />
            </template>
            <template #trailing-actions>
              <span v-if="questionItemsToReplace?.includes(question.item)">
                {{ replacingThisQuestionLabel$() }}
              </span>
              <slot
                name="question-trailing-actions"
                :question="question"
              ></slot>
            </template>
            <template #content>
              <div
                :id="`question-panel-${question.item}`"
                :style="{ userSelect: dragActive ? 'none !important' : 'text' }"
              >
                <div
                  v-if="question.is_custom"
                  class="custom-question-accordion-content"
                  style="padding: 16px;"
                >
                  <p style="margin-bottom: 8px; font-size: 16px; font-weight: 600;">
                    {{ question.prompt || question.title }}
                  </p>
                  <div
                    v-if="question.prompt_image"
                    style="margin-bottom: 12px;"
                  >
                    <img
                      :src="question.prompt_image"
                      alt="Question illustration"
                      style="max-width: 100%; max-height: 200px; border-radius: 6px;"
                    >
                  </div>
                  <div
                    v-if="question.options && question.options.length"
                    style="display: flex; flex-direction: column; gap: 8px;"
                  >
                    <div
                      v-for="opt in question.options"
                      :key="opt.id"
                      style="display: flex; gap: 8px; align-items: center;"
                    >
                      <KIcon
                        :icon="question.answer_key && question.answer_key.includes(opt.id) ? 'check' : 'radio_button_unchecked'"
                        :style="{ color: question.answer_key && question.answer_key.includes(opt.id) ? '#16a34a' : $themeTokens.annotation }"
                      />
                      <span>{{ opt.text }}</span>
                      <span
                        v-if="question.answer_key && question.answer_key.includes(opt.id)"
                        style="font-size: 12px; font-weight: 600; color: #16a34a;"
                      >
                        ({{ correctAnswerLabel$() }})
                      </span>
                    </div>
                  </div>
                  <div
                    v-else-if="question.question_type === 'short_answer'"
                    style="margin-top: 8px;"
                  >
                    <span style="font-weight: 600;">{{ acceptedAnswersLabel$() }}: </span>
                    <span>{{ (question.answer_key || []).join(', ') }}</span>
                  </div>
                </div>
                <ContentViewer
                  v-else-if="questionContentExists(question)"
                  :ref="`contentRenderer-${question.item}`"
                  :lang="getQuestionContent(question).lang"
                  :files="getQuestionContent(question).files"
                  :itemId="question.question_id"
                  :assessment="true"
                  :allowHints="false"
                  :interactive="false"
                  :showCorrectAnswer="true"
                  @interaction="() => null"
                  @updateProgress="() => null"
                  @updateContentState="() => null"
                  @error="err => $emit('error', err)"
                />
                <div v-else>
                  <KIcon
                    icon="warning"
                    :style="{ fill: $themePalette.yellow.v_600 }"
                  />
                  {{ coreString('resourceNotFoundOnDevice') }}
                </div>
                <slot
                  name="questionExtraContent"
                  :question="question"
                ></slot>
              </div>
            </template>
          </AccordionItem>
        </Draggable>
      </transition-group>
    </DragContainer>
  </AccordionContainer>

</template>


<script>

  import { computed, ref } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import { enhancedQuizManagementStrings } from 'kolibri-common/strings/enhancedQuizManagementStrings';
  import Draggable from 'kolibri-common/components/sortable/Draggable';
  import DragHandle from 'kolibri-common/components/sortable/DragHandle';
  import DragContainer from 'kolibri-common/components/sortable/DragContainer';
  import DragSortWidget from 'kolibri-common/components/sortable/DragSortWidget';
  import AccordionItem from 'kolibri-common/components/accordion/AccordionItem';
  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';
  import AccordionContainer from 'kolibri-common/components/accordion/AccordionContainer';
  import useDrag from './useDrag.js';

  const accordionStrings = createTranslator('QuestionsAccordionStrings', {
    correctAnswerLabel: {
      message: 'Correct',
      context: 'Label indicating correct answer',
    },
    acceptedAnswersLabel: {
      message: 'Accepted answers',
      context: 'Label indicating accepted short answers',
    },
  });

  export default {
    name: 'QuestionsAccordion',
    components: {
      Draggable,
      DragHandle,
      DragContainer,
      DragSortWidget,
      AccordionItem,
      AccordionContainer,
    },
    mixins: [commonCoreStrings],
    setup(props) {
      const dragActive = ref(false);

      const { selectAllLabel$, expandAll$, collapseAll$, replacingThisQuestionLabel$ } =
        enhancedQuizManagementStrings;

      const { correctAnswerLabel$, acceptedAnswersLabel$ } = accordionStrings;

      const { moveUpOne, moveDownOne } = useDrag();

      function questionCheckboxDisabled(question) {
        if (
          props.disabled ||
          props.unselectableQuestionItems?.includes(question.item) ||
          props.questionItemsToReplace?.includes(question.item)
        ) {
          return true;
        }
        if (
          props.selectedQuestions.includes(question.item) ||
          props.maxSelectableQuestions === null
        ) {
          return false;
        }
        return props.selectedQuestions.length >= props.maxSelectableQuestions;
      }

      function questionIsChecked(question) {
        if (props.questionItemsToReplace?.includes(question.item)) {
          return false;
        }
        if (props.unselectableQuestionItems?.includes(question.item)) {
          return true;
        }
        return props.selectedQuestions.includes(question.item);
      }

      const selectableQuestions = computed(() => {
        if (!props.isSelectable) {
          return [];
        }
        return props.questions.filter(
          question => !props.unselectableQuestionItems?.includes(question.item),
        );
      });

      const selectAllIsChecked = computed(
        () =>
          selectableQuestions.value.length > 0 &&
          selectableQuestions.value.every(question =>
            props.selectedQuestions.includes(question.item),
          ),
      );

      const selectAllIsIndeterminate = computed(
        () =>
          selectableQuestions.value.length > 0 &&
          !selectAllIsChecked.value &&
          selectableQuestions.value.some(question =>
            props.selectedQuestions.includes(question.item),
          ),
      );

      const selectAllIsDisabled = computed(() => {
        if (props.disabled) {
          return true;
        }
        if (props.maxSelectableQuestions === null || selectAllIsChecked.value) {
          return false;
        }
        if (props.selectedQuestions.length >= props.maxSelectableQuestions) {
          return true;
        }
        const deselectedQuestions = selectableQuestions.value.filter(
          question => !props.selectedQuestions.includes(question.item),
        );
        const selectedQuestionsLength = props.selectedQuestions.length;
        const potentialSelectionLength = selectedQuestionsLength + deselectedQuestions.length;
        return potentialSelectionLength > props.maxSelectableQuestions;
      });

      return {
        dragActive,
        selectableQuestions,
        selectAllIsDisabled,
        selectAllIsChecked,
        selectAllIsIndeterminate,

        moveUpOne,
        moveDownOne,
        questionIsChecked,
        questionCheckboxDisabled,

        selectAllLabel$,
        expandAll$,
        collapseAll$,
        replacingThisQuestionLabel$,
        correctAnswerLabel$,
        acceptedAnswersLabel$,
      };
    },
    props: {
      questions: {
        type: Array,
        required: true,
      },
      getQuestionContent: {
        type: Function,
        required: true,
      },
      selectedQuestions: {
        type: Array,
        required: false,
        default: () => [],
      },
      isSelectable: {
        type: Boolean,
        required: false,
        default: true,
      },
      /**
       * Maximum number of questions that can be selected.
       */
      maxSelectableQuestions: {
        type: Number,
        required: false,
        default: null,
      },
      /**
       * If true, all checkboxes will be disabled.
       */
      disabled: {
        type: Boolean,
        default: false,
      },
      /**
       * Array of question ids that already belongs to the quiz,
       * and should not be selectable.
       */
      unselectableQuestionItems: {
        type: Array,
        required: false,
        default: null,
      },
      /**
       * If provided, the question with this item will appear as disabled
       * and with a `Replacing this question` message.
       */
      questionItemsToReplace: {
        type: Array,
        required: false,
        default: null,
      },
    },
    computed: {
      isSortable() {
        return this.$listeners.sort !== undefined;
      },
    },
    methods: {
      handleDragStart() {
        // Used to mitigate the issue of text being selected while dragging
        this.dragActive = true;
      },
      handleQuestionOrderChange({ newArray }) {
        this.$emit('sort', { newArray });
        this.dragActive = false;
      },
      handleKeyboardDragDown(oldIndex) {
        const newArray = this.moveDownOne(oldIndex, this.questions);
        this.handleQuestionOrderChange({ newArray });
      },
      handleKeyboardDragUp(oldIndex) {
        const newArray = this.moveUpOne(oldIndex, this.questions);
        this.handleQuestionOrderChange({ newArray });
      },
      handleQuestionCheckboxChange(questionItem, value, $event) {
        $event.stopPropagation();
        if (value) {
          this.$emit('selectQuestions', [questionItem]);
        } else {
          this.$emit('deselectQuestions', [questionItem]);
        }
      },
      handleSelectAll(value) {
        if (value) {
          this.$emit(
            'selectQuestions',
            this.selectableQuestions.map(question => question.item),
          );
        } else {
          this.$emit(
            'deselectQuestions',
            this.selectableQuestions.map(question => question.item),
          );
        }
      },
      getDisplayQuestionTitle(question, title) {
        if (question && question.is_custom) {
          return question.prompt || question.title || 'Custom Question';
        }
        return title || this.coreString('resourceNotFoundOnDevice');
      },
      questionContentExists(question) {
        if (question && question.is_custom) {
          return true;
        }
        const content = this.getQuestionContent(question);
        return content && content.available;
      },
    },
  };

</script>


<style lang="scss" scoped>

  .questions-accordion-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-left: 8px;

    .select-all-box {
      margin-top: 0;
      margin-bottom: 0;

      &.select-all-box-sortable {
        margin-left: 1.5em;
      }

      // Vertical centering here into the KCheckbox
      ::v-deep & label {
        line-height: 28px;
      }
    }

    .trailing-actions {
      display: flex;
      align-items: center;
    }
  }

  .accordion-item-checkbox {
    margin-left: 0.5em;
  }

</style>
