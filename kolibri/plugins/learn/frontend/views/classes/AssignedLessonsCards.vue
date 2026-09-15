<template>

  <div>
    <div class="section-header">
      <h2 :style="{ margin: 0 }">
        <KLabeledIcon
          icon="lesson"
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
          v-if="lessons && lessons.length > 0"
          layout="1-2-3"
          :layoutOverride="[{ columnGap: '16px', rowGap: '16px' }]"
        >
          <AssignmentCard
            v-for="lesson in lessons"
            :key="lesson.id"
            :lesson="lesson"
            :to="getClassLessonLink(lesson)"
            :collectionTitle="displayClassName ? getLessonClassName(lesson) : ''"
          />
        </KCardGrid>

        <p v-else>
          {{ $tr('noLessonsMessage') }}
        </p>
      </div>
    </transition>
  </div>

</template>


<script>

  import SectionToggleButton from 'kolibri-common/components/SectionToggleButton';
  import useCollapsible from 'kolibri-common/composables/useCollapsible';
  import useLearnerResources from '../../composables/useLearnerResources';
  import AssignmentCard from '../cards/AssignmentCard';

  export default {
    name: 'AssignedLessonsCards',
    components: {
      AssignmentCard,
      SectionToggleButton,
    },
    setup(props) {
      const { isExpanded, toggleExpand } = useCollapsible('learn_lessons', true);
      const { getClass, getClassLessonLink } = useLearnerResources();

      function getLessonClassName(lesson) {
        const lessonClass = getClass(lesson.collection);
        return lessonClass ? lessonClass.name : '';
      }

      return {
        getLessonClassName,
        getClassLessonLink,
        isExpanded,
        toggleExpand,
      };
    },
    props: {
      lessons: {
        type: Array,
        required: true,
      },
      /**
       * If `true` 'Recent lessons' header will be displayed.
       * Otherwise 'Your lessons' will be displayed.
       */
      recent: {
        type: Boolean,
        default: false,
      },
      /**
       * A lesson's class name will be displayed above
       * the lesson title if `true`
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
        return this.recent ? this.$tr('recentLessonsHeader') : this.$tr('yourLessonsHeader');
      },
    },
    $trs: {
      recentLessonsHeader: {
        message: 'Recent lessons',
        context:
          "Section header on the learner's Home page, displaying the most recent lessons that the coaches assigned to them.",
      },
      yourLessonsHeader: {
        message: 'Your lessons',
        context:
          "Heading on the 'Learn' page for a section where a learner can see which lessons have been assigned to them.",
      },
      noLessonsMessage: {
        message: 'You have no lessons assigned',
        context: 'Message that a learner sees if a coach has not assigned any lessons to them.',
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
