<template>

  <div>
    <div class="section-header">
      <h2 :style="{ margin: 0 }">
        <KLabeledIcon
          icon="quiz"
          :label="header"
        />
      </h2>
      <SectionToggleButton
        :isExpanded="isExpanded"
        @click="toggleExpand"
      />
    </div>

    <transition name="section-collapse">
      <div v-show="isExpanded" class="section-content">
        <KCardGrid
          v-if="visibleQuizzes.length > 0"
          layout="1-2-3"
          :layoutOverride="[{ columnGap: '16px', rowGap: '16px' }]"
        >
          <AssignmentCard
            v-for="quiz in visibleQuizzes"
            :key="quiz.id"
            :quiz="quiz"
            :to="getClassQuizLink(quiz)"
            :collectionTitle="displayClassName ? getQuizClassName(quiz) : ''"
          />
        </KCardGrid>
        <p v-else>
          {{ $tr('noQuizzesMessage') }}
        </p>
      </div>
    </transition>
  </div>

</template>


<script>

  import { computed } from 'vue';
  import SectionToggleButton from 'kolibri-common/components/SectionToggleButton';
  import useCollapsible from 'kolibri-common/composables/useCollapsible';
  import useLearnerResources from '../../composables/useLearnerResources';
  import AssignmentCard from '../cards/AssignmentCard';

  export default {
    name: 'AssignedQuizzesCards',
    components: {
      AssignmentCard,
      SectionToggleButton,
    },
    setup(props) {
      const { isExpanded, toggleExpand } = useCollapsible('learn_quizzes', true);
      const { getClass, getClassQuizLink } = useLearnerResources();

      const visibleQuizzes = computed(() => {
        if (!props.quizzes) {
          return [];
        }
        return props.quizzes.filter(quiz => {
          if (!quiz.active) {
            return false;
          } else if (quiz.archive) {
            // Closed (archived) quizzes only show if the learner started/submitted
            return quiz.progress.started || quiz.progress.closed;
          } else {
            return true;
          }
        });
      });

      function getQuizClassName(quiz) {
        const quizClass = getClass(quiz.collection);
        return quizClass ? quizClass.name : '';
      }

      return {
        visibleQuizzes,
        getQuizClassName,
        getClassQuizLink,
        isExpanded,
        toggleExpand,
      };
    },
    props: {
      // `quizzes` prop is used in `setup`
      // eslint-disable-next-line vue/no-unused-properties
      quizzes: {
        type: Array,
        required: true,
      },
      /**
       * If `true` 'Recent quizzes' header will be displayed.
       * Otherwise 'Your quizzes' will be displayed.
       */
      recent: {
        type: Boolean,
        default: false,
      },
      /**
       * A quiz's class name will be displayed above
       * the quiz title if `true`
       */
      displayClassName: {
        type: Boolean,
        default: false,
      },
    },
    computed: {
      // TODO: Would be more consistent to have this computed property in `setup`,
      // however haven't found a way to work with translations there yet
      header() {
        return this.recent ? this.$tr('recentQuizzesHeader') : this.$tr('yourQuizzesHeader');
      },
    },
    $trs: {
      yourQuizzesHeader: {
        message: 'Your quizzes',
        context:
          "AssignedQuizzesCards.yourQuizzesHeader\n\nHeading on the 'Learn' page for a section where a learner can see which quizzes have been assigned to them.",
      },
      noQuizzesMessage: {
        message: 'You have no quizzes assigned',
        context: 'Message that a learner sees if a coach has not assigned any quizzes to them.',
      },
      recentQuizzesHeader: {
        message: 'Recent quizzes',
        context:
          "Section header on the learner's Home page, displaying the most recent quizzes that the coaches assigned to them.",
      },
    },
  };

</script>


<style lang="scss" scoped>

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }

  .section-collapse-enter-active,
  .section-collapse-leave-active {
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
  }

  .section-collapse-enter-from,
  .section-collapse-leave-to {
    opacity: 0;
    transform: translateY(-8px);
  }

</style>
