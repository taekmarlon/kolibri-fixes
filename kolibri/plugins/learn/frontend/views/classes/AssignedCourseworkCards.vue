<template>

  <div
    v-if="!recent || (assignments && assignments.length > 0)"
    class="coursework-section"
  >
    <div class="header-row">
      <h2>
        <KLabeledIcon
          icon="edit"
          :label="header"
        />
      </h2>
      <KButton
        v-if="classId"
        appearance="basic-link"
        icon="people"
        :text="goToDiscussions$()"
        :to="discussionsLink"
      />
    </div>

    <!-- Quick Access Discussion Board Banner (only when on a specific class page) -->
    <div
      v-if="classId"
      class="discussions-banner"
      :style="{
        backgroundColor: $themeTokens.surface,
        border: `1px solid ${$themeTokens.fineLine}`,
      }"
    >
      <div class="banner-left">
        <KIcon
          icon="people"
          class="banner-icon"
          :color="$themeTokens.primary"
        />
        <div>
          <div class="banner-title" :style="{ color: $themeTokens.text }">
            {{ classroomDiscussionsTitle$() }}
          </div>
          <div class="banner-subtitle" :style="{ color: $themeTokens.annotation }">
            {{ classroomDiscussionsDesc$() }}
          </div>
        </div>
      </div>
      <KButton
        :text="openForumButton$()"
        appearance="flat-button"
        icon="openNewTab"
        :to="discussionsLink"
      />
    </div>

    <!-- Assignments Grid -->
    <KCircularLoader v-if="loading" />
    <KCardGrid
      v-else-if="assignments && assignments.length > 0"
      layout="1-2-3"
      :layoutOverride="[{ columnGap: '16px', rowGap: '16px' }]"
    >
      <KCard
        v-for="assignment in assignments"
        :key="assignment.id"
        :to="getAssignmentLink(assignment)"
        :title="assignment.title"
        :headingLevel="3"
        orientation="vertical"
        thumbnailDisplay="none"
      >
        <template #aboveTitle>
          <div
            v-if="displayClassName && getAssignmentClassName(assignment)"
            class="class-name-badge"
            :style="{ color: $themeTokens.annotation }"
          >
            {{ getAssignmentClassName(assignment) }}
          </div>
          <div class="card-tags">
            <span
              v-if="assignment.video_url"
              class="video-badge"
              :style="{
                backgroundColor: $themeTokens.primary + '18',
                color: $themeTokens.primary,
              }"
            >
              🎥 {{ videoLessonBadge$() }}
            </span>
            <span
              v-if="getSubmissionStatus(assignment.id).graded"
              class="status-badge graded-badge"
            >
              ✓ {{ gradedBadge$() }}: {{ getSubmissionStatus(assignment.id).score }}/{{ assignment.max_points || assignment.points_possible }}
            </span>
            <span
              v-else-if="getSubmissionStatus(assignment.id).submitted"
              class="status-badge submitted-badge"
            >
              {{ submittedBadge$() }}
            </span>
            <span
              v-else
              class="status-badge pending-badge"
            >
              {{ pendingBadge$() }}
            </span>
          </div>
        </template>

        <template #footer>
          <div class="card-footer" :style="{ color: $themeTokens.annotation }">
            <div class="footer-meta">
              <span class="points-label">
                {{ assignment.max_points || assignment.points_possible }} {{ pointsLabel$() }}
              </span>
              <span v-if="assignment.due_date" class="due-date">
                • {{ dueLabel$() }}: {{ formatDate(assignment.due_date) }}
              </span>
              <span v-else class="due-date">
                • {{ noDueDate$() }}
              </span>
            </div>
            <KButton
              :text="viewAssignment$()"
              appearance="basic-link"
              :to="getAssignmentLink(assignment)"
            />
          </div>
        </template>
      </KCard>
    </KCardGrid>

    <p
      v-else-if="!loading && !recent"
      :style="{ color: $themeTokens.annotation, marginTop: '8px' }"
    >
      {{ noAssignmentsMessage$() }}
    </p>
  </div>

</template>

<script>

  import { ref, computed, onMounted } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import AssignmentResource from 'kolibri-common/apiResources/AssignmentResource';
  import AssignmentSubmissionResource from 'kolibri-common/apiResources/AssignmentSubmissionResource';
  import useLearnerResources from '../../composables/useLearnerResources';
  import { assignmentDetailLink, classDiscussionsLink } from './classPageLinks';

  const strings = createTranslator('AssignedCourseworkCardsStrings', {
    courseworkHeader: {
      message: 'Homework & Assignments',
      context: 'Section header for coursework assignments in the learner view',
    },
    recentAssignmentsHeader: {
      message: 'Recent assignments',
      context: 'Header for recent assignments list on home page',
    },
    goToDiscussions: {
      message: 'Classroom Discussions',
      context: 'Link to navigate to class discussions',
    },
    classroomDiscussionsTitle: {
      message: 'Classroom Q&A & Discussions',
      context: 'Title of the classroom discussions banner',
    },
    classroomDiscussionsDesc: {
      message: 'Ask questions, share ideas with classmates, and view teacher-endorsed answers.',
      context: 'Description of classroom discussions',
    },
    openForumButton: {
      message: 'Open Forum',
      context: 'Button label to open class forum',
    },
    videoLessonBadge: {
      message: 'Video Lesson',
      context: 'Badge on assignment card indicating a video is included',
    },
    gradedBadge: {
      message: 'Graded',
      context: 'Badge indicating assignment is graded',
    },
    submittedBadge: {
      message: 'Submitted',
      context: 'Badge indicating assignment is submitted',
    },
    pendingBadge: {
      message: 'Not Submitted',
      context: 'Badge indicating assignment has not been submitted yet',
    },
    pointsLabel: {
      message: 'pts',
      context: 'Abbreviation for points',
    },
    dueLabel: {
      message: 'Due',
      context: 'Prefix for due date',
    },
    noDueDate: {
      message: 'No due date',
      context: 'Label when no due date is specified',
    },
    viewAssignment: {
      message: 'Open ➔',
      context: 'Link to view the assignment',
    },
    noAssignmentsMessage: {
      message: 'No assignments have been assigned for this class yet.',
      context: 'Message shown when there are no assignments',
    },
  });

  export default {
    name: 'AssignedCourseworkCards',
    props: {
      classId: {
        type: String,
        default: null,
      },
      recent: {
        type: Boolean,
        default: false,
      },
      displayClassName: {
        type: Boolean,
        default: false,
      },
    },
    setup(props) {
      const { getClass } = useLearnerResources();
      const loading = ref(true);
      const assignments = ref([]);
      const submissions = ref([]);

      const header = computed(() => {
        return props.recent ? strings.recentAssignmentsHeader$() : strings.courseworkHeader$();
      });

      const discussionsLink = computed(() => {
        return props.classId ? classDiscussionsLink(props.classId) : null;
      });

      function getAssignmentLink(assignment) {
        const classId = props.classId || assignment.collection;
        return assignmentDetailLink(classId, assignment.id);
      }

      function getAssignmentClassName(assignment) {
        if (!assignment) return '';
        if (assignment.collection_name) return assignment.collection_name;
        const cls = getClass(assignment.collection);
        return cls ? cls.name : '';
      }

      function loadData() {
        loading.value = true;
        const getParams = { is_active: true };
        if (props.classId) {
          getParams.collection = props.classId;
        }

        Promise.all([
          AssignmentResource.fetchCollection({ getParams }),
          AssignmentSubmissionResource.fetchCollection(),
        ])
          .then(([assignmentsData, submissionsData]) => {
            assignments.value = assignmentsData || [];
            submissions.value = submissionsData || [];
            loading.value = false;
          })
          .catch(() => {
            assignments.value = [];
            submissions.value = [];
            loading.value = false;
          });
      }

      function getSubmissionStatus(assignmentId) {
        const sub = submissions.value.find(s => s.assignment === assignmentId);
        if (!sub) {
          return { submitted: false, graded: false, score: 0 };
        }
        return {
          submitted: true,
          graded: sub.status === 'graded',
          score: sub.points_awarded || 0,
        };
      }

      function formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString(undefined, {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        });
      }

      onMounted(() => {
        loadData();
      });

      return {
        header,
        loading,
        assignments,
        discussionsLink,
        getAssignmentLink,
        getAssignmentClassName,
        getSubmissionStatus,
        formatDate,
        ...strings,
      };
    },
  };

</script>

<style lang="scss" scoped>

  .coursework-section {
    margin-top: 44px;
  }

  .header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }

  .discussions-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 8px;
    padding: 14px 20px;
    margin-bottom: 20px;
  }

  .banner-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .banner-icon {
    font-size: 28px;
  }

  .banner-title {
    font-weight: bold;
    font-size: 15px;
  }

  .banner-subtitle {
    font-size: 13px;
    margin-top: 2px;
  }

  .class-name-badge {
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 8px;
  }

  .video-badge {
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
  }

  .status-badge {
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
  }

  .graded-badge {
    background-color: #dcfce7;
    color: #166534;
  }

  .submitted-badge {
    background-color: #e0e7ff;
    color: #3730a3;
  }

  .pending-badge {
    background-color: #f3f4f6;
    color: #4b5563;
  }

  .card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    font-size: 12px;
    padding-top: 8px;
  }

  .footer-meta {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .points-label {
    font-weight: bold;
  }

</style>
