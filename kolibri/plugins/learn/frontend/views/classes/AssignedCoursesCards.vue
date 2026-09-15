<template>

  <div v-if="courses && courses.length > 0">
    <div class="section-header">
      <h2 :style="{ margin: 0 }">
        <KLabeledIcon
          icon="course"
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
          layout="1-2-3"
          :layoutOverride="[{ columnGap: '16px', rowGap: '16px' }]"
        >
          <AssignmentCard
            v-for="course in courses"
            :key="course.id"
            :course="course"
            :to="getClassCourseLink(course)"
            :collectionTitle="displayClassName ? getCourseClassName(course) : ''"
          />
        </KCardGrid>
      </div>
    </transition>
  </div>

</template>


<script>

  import { coursesStrings } from 'kolibri-common/strings/coursesStrings';
  import SectionToggleButton from 'kolibri-common/components/SectionToggleButton';
  import useCollapsible from 'kolibri-common/composables/useCollapsible';
  import useLearnerResources from '../../composables/useLearnerResources';
  import AssignmentCard from '../cards/AssignmentCard';

  export default {
    name: 'AssignedCoursesCards',
    components: {
      AssignmentCard,
      SectionToggleButton,
    },
    setup(props) {
      const { isExpanded, toggleExpand } = useCollapsible('learn_courses', true);
      const { getClass, getClassCourseLink } = useLearnerResources();
      const { recentCoursesHeader$, yourCoursesHeader$ } = coursesStrings;

      function getCourseClassName(course) {
        const courseClass = getClass(course.collection);
        return courseClass ? courseClass.name : '';
      }

      return {
        getCourseClassName,
        getClassCourseLink,
        recentCoursesHeader$,
        yourCoursesHeader$,
        isExpanded,
        toggleExpand,
      };
    },
    props: {
      courses: {
        type: Array,
        required: true,
      },
      /**
       * If `true` 'Recent courses' header will be displayed.
       * Otherwise 'My courses' will be displayed.
       */
      recent: {
        type: Boolean,
        default: false,
      },
      /**
       * A course's class name will be displayed above
       * the course title if `true`
       */
      displayClassName: {
        type: Boolean,
        default: false,
      },
    },
    computed: {
      header() {
        return this.recent ? this.recentCoursesHeader$() : this.yourCoursesHeader$();
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
