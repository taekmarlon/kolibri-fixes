<template>
  <CoachAppBarPage>
    <div class="assignments-container">
      <div class="header-nav">
        <KRouterLink
          :to="{ name: PageNames.HOME_PAGE, params: { classId } }"
          class="back-link"
        >
          ← {{ backToClassHome$() }}
        </KRouterLink>
      </div>

      <div class="page-header">
        <div>
          <h1 class="page-title" :style="{ color: $themeTokens.text }">
            📝 {{ pageTitle$() }}
          </h1>
          <p class="page-subtitle" :style="{ color: $themeTokens.annotation }">
            {{ pageSubtitle$() }}
          </p>
        </div>
        <div class="header-buttons">
          <KButton
            :text="createAssignmentButton$()"
            :primary="true"
            appearance="raised-button"
            icon="plus"
            @click="openCreateModal"
          />
          <KRouterLink
            :text="viewGradebookButton$()"
            appearance="flat-button"
            icon="reports"
            :to="{ name: PageNames.COURSEWORK_GRADEBOOK, params: { classId } }"
          />
          <KRouterLink
            :text="viewDiscussionsButton$()"
            appearance="flat-button"
            icon="group"
            :to="{ name: PageNames.COURSEWORK_DISCUSSIONS, params: { classId } }"
          />
        </div>
      </div>

      <KCircularLoader v-if="loading" />

      <div
        v-else-if="assignments.length === 0"
        class="empty-box"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px dashed ${$themeTokens.fineLine}`,
        }"
      >
        <span class="empty-icon">📁</span>
        <h2 :style="{ color: $themeTokens.text }">{{ noAssignmentsTitle$() }}</h2>
        <p :style="{ color: $themeTokens.annotation }">
          {{ noAssignmentsDesc$() }}
        </p>
        <KButton
          :text="createFirstAssignmentButton$()"
          :primary="true"
          appearance="raised-button"
          @click="openCreateModal"
        />
      </div>

      <div v-else class="assignments-grid">
        <div
          v-for="assignment in assignments"
          :key="assignment.id"
          class="assignment-card"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
        >
          <div class="card-top">
            <div class="card-meta">
              <span
                class="status-pill"
                :class="{ 'is-active': assignment.is_active }"
              >
                {{ assignment.is_active ? activeLabel$() : inactiveLabel$() }}
              </span>
              <span v-if="assignment.due_date" class="due-date">
                📅 {{ formatDate(assignment.due_date) }}
              </span>
              <span class="max-pts">
                🎯 {{ assignment.max_points }} {{ pointsLabel$() }}
              </span>
            </div>
            <h2 class="assignment-title" :style="{ color: $themeTokens.text }">
              {{ assignment.title }}
            </h2>
            <p
              v-if="assignment.description"
              class="assignment-desc"
              :style="{ color: $themeTokens.annotation }"
            >
              {{ assignment.description }}
            </p>
          </div>

          <div v-if="assignment.video_url" class="video-indicator">
            <span class="video-tag">▶ YouTube Video Attached</span>
            <span class="video-url-snippet">{{ assignment.video_url }}</span>
          </div>

          <div
            class="card-bottom"
            :style="{
              borderTop: `1px solid ${$themeTokens.fineLine}`,
              backgroundColor: $themePalette.grey.v_100,
            }"
          >
            <div class="submission-stats">
              <span class="stat-bubble">
                📥 <strong>{{ assignment.submissions_count || 0 }}</strong> {{ submissionsLabel$() }}
              </span>
              <span class="stat-bubble graded">
                ✅ <strong>{{ assignment.graded_count || 0 }}</strong> {{ gradedLabel$() }}
              </span>
            </div>

            <div class="card-actions">
              <KButton
                :text="viewSubmissionsButton$()"
                :primary="true"
                appearance="flat-button"
                @click="openSubmissionsDrawer(assignment)"
              />
              <KButton
                :text="deleteButton$()"
                appearance="flat-button"
                :style="{ color: $themeTokens.error }"
                @click="confirmDelete(assignment)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Create Assignment Modal -->
      <KModal
        v-if="showCreateModal"
        :title="newAssignmentModalTitle$()"
        :submitText="saveAssignmentAction$()"
        :cancelText="cancelAction$()"
        @submit="submitNewAssignment"
        @cancel="closeCreateModal"
      >
        <div class="modal-form">
          <KTextbox
            v-model="newForm.title"
            :label="assignmentTitleLabel$()"
            :required="true"
            :autofocus="true"
          />

          <KTextbox
            v-model="newForm.description"
            :label="assignmentInstructionsLabel$()"
            :textArea="true"
            :rows="3"
          />

          <div class="form-section">
            <KTextbox
              v-model="newForm.video_url"
              :label="youtubeUrlLabel$()"
              :placeholder="youtubeUrlPlaceholder$()"
            />
            <p class="form-hint" :style="{ color: $themeTokens.annotation }">
              💡 {{ youtubeHelpText$() }}
            </p>
            <div v-if="newForm.video_url" class="modal-preview">
              <YouTubePlayer :videoUrl="newForm.video_url" :title="newForm.title" />
            </div>
          </div>

          <div class="form-row">
            <KTextbox
              v-model.number="newForm.max_points"
              :label="maxPointsLabel$()"
              type="number"
              style="width: 140px;"
            />
            <div class="date-input-box">
              <label class="date-label">{{ dueDateLabel$() }}</label>
              <input
                v-model="newForm.due_date"
                type="datetime-local"
                class="native-date-input"
                :style="{ borderColor: $themeTokens.fineLine }"
              />
            </div>
          </div>

          <div class="checkbox-group">
            <KCheckbox
              v-model="newForm.allow_text_submission"
              :label="allowTextLabel$()"
            />
            <KCheckbox
              v-model="newForm.allow_file_upload"
              :label="allowFileLabel$()"
            />
          </div>
        </div>
      </KModal>

      <!-- Submissions Review Modal -->
      <KModal
        v-if="activeSubmissionsAssignment"
        :title="`${submissionsForTitle$()}: ${activeSubmissionsAssignment.title}`"
        :cancelText="closeAction$()"
        @cancel="closeSubmissionsDrawer"
      >
        <div class="submissions-drawer">
          <KCircularLoader v-if="submissionsLoading" />

          <div v-else-if="submissionsList.length === 0" class="empty-submissions">
            <p>{{ noSubmissionsYet$() }}</p>
          </div>

          <div v-else class="submissions-list">
            <div
              v-for="sub in submissionsList"
              :key="sub.id"
              class="submission-item"
              :style="{
                backgroundColor: $themeTokens.surface,
                border: `1px solid ${$themeTokens.fineLine}`,
              }"
            >
              <div class="sub-header">
                <div>
                  <strong class="student-name">{{ sub.learner_full_name || sub.learner_username }}</strong>
                  <span class="sub-date" :style="{ color: $themeTokens.annotation }">
                    • {{ formatDate(sub.submitted_at) }}
                  </span>
                </div>
                <span
                  class="sub-status-badge"
                  :class="sub.status"
                >
                  {{ sub.status === 'graded' ? gradedStatus$() : submittedStatus$() }}
                </span>
              </div>

              <div v-if="sub.text_content" class="sub-body">
                <span class="section-tag">{{ studentAnswerLabel$() }}:</span>
                <p class="sub-text">{{ sub.text_content }}</p>
              </div>

              <div v-if="sub.file_attachment" class="sub-attachment">
                <span class="section-tag">📎 {{ attachedFileLabel$() }}:</span>
                <a
                  :href="sub.file_attachment"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="attachment-link"
                >
                  {{ sub.file_name || downloadAttachmentLabel$() }}
                </a>
              </div>

              <div
                class="grading-form"
                :style="{
                  backgroundColor: $themePalette.grey.v_100,
                  borderTop: `1px solid ${$themeTokens.fineLine}`,
                }"
              >
                <div class="grading-row">
                  <div class="score-input">
                    <label class="field-lbl">{{ scoreLabel$() }} (max {{ activeSubmissionsAssignment.max_points }}):</label>
                    <input
                      v-model.number="gradingForms[sub.id].grade"
                      type="number"
                      step="0.5"
                      min="0"
                      :max="activeSubmissionsAssignment.max_points"
                      class="grade-input"
                    />
                  </div>
                  <KButton
                    :text="saveGradeAction$()"
                    :primary="true"
                    appearance="raised-button"
                    @click="submitGrade(sub)"
                  />
                </div>
                <KTextbox
                  v-model="gradingForms[sub.id].feedback"
                  :label="feedbackPlaceholder$()"
                  :textArea="true"
                  :rows="2"
                />
              </div>
            </div>
          </div>
        </div>
      </KModal>
    </div>
  </CoachAppBarPage>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { createTranslator } from 'kolibri/utils/i18n';
import YouTubePlayer from 'kolibri-common/components/YouTubePlayer.vue';
import AssignmentResource from 'kolibri-common/apiResources/AssignmentResource';
import AssignmentSubmissionResource from 'kolibri-common/apiResources/AssignmentSubmissionResource';
import useCoreCoach from '../../composables/useCoreCoach';
import CoachAppBarPage from '../CoachAppBarPage';
import { PageNames } from '../../constants';

const strings = createTranslator('CoachAssignmentsStrings', {
  backToClassHome: { message: 'Class Home', context: 'Navigation link' },
  pageTitle: { message: 'Assignments & Homework Dropboxes', context: 'Page header' },
  pageSubtitle: { message: 'Create student assignments, review homework submissions, and grade work.', context: 'Subheader' },
  createAssignmentButton: { message: 'New Assignment', context: 'Button' },
  viewGradebookButton: { message: 'Gradebook', context: 'Button' },
  viewDiscussionsButton: { message: 'Discussion Board', context: 'Button' },
  noAssignmentsTitle: { message: 'No assignments created yet', context: 'Empty state title' },
  noAssignmentsDesc: { message: 'Create your first homework assignment or lab report with text, file dropboxes, or embedded YouTube videos.', context: 'Empty state description' },
  createFirstAssignmentButton: { message: 'Create First Assignment', context: 'Button' },
  activeLabel: { message: 'Active', context: 'Status pill' },
  inactiveLabel: { message: 'Draft', context: 'Status pill' },
  pointsLabel: { message: 'pts', context: 'Points abbreviation' },
  submissionsLabel: { message: 'submissions', context: 'Count label' },
  gradedLabel: { message: 'graded', context: 'Count label' },
  viewSubmissionsButton: { message: 'Review Submissions', context: 'Action button' },
  deleteButton: { message: 'Delete', context: 'Action button' },
  newAssignmentModalTitle: { message: 'Create New Assignment', context: 'Modal header' },
  saveAssignmentAction: { message: 'Publish Assignment', context: 'Modal submit' },
  cancelAction: { message: 'Cancel', context: 'Button' },
  closeAction: { message: 'Close', context: 'Button' },
  assignmentTitleLabel: { message: 'Assignment Title', context: 'Input label' },
  assignmentInstructionsLabel: { message: 'Instructions & Notes', context: 'Input label' },
  youtubeUrlLabel: { message: 'YouTube Video Link (Optional)', context: 'Input label' },
  youtubeUrlPlaceholder: { message: 'e.g. https://www.youtube.com/watch?v=...', context: 'Placeholder' },
  youtubeHelpText: { message: 'Learners can watch this video natively inside Kolibri without leaving the platform.', context: 'Helper note' },
  maxPointsLabel: { message: 'Max Points', context: 'Input label' },
  dueDateLabel: { message: 'Due Date', context: 'Input label' },
  allowTextLabel: { message: 'Allow written text submission', context: 'Checkbox' },
  allowFileLabel: { message: 'Allow file upload (PDF, images, documents)', context: 'Checkbox' },
  submissionsForTitle: { message: 'Submissions', context: 'Modal title' },
  noSubmissionsYet: { message: 'No submissions received yet for this assignment.', context: 'Empty text' },
  gradedStatus: { message: 'Graded', context: 'Badge' },
  submittedStatus: { message: 'Needs Grading', context: 'Badge' },
  studentAnswerLabel: { message: 'Student Written Answer', context: 'Section title' },
  attachedFileLabel: { message: 'Submitted File', context: 'Section title' },
  downloadAttachmentLabel: { message: 'Download Attachment', context: 'Link' },
  scoreLabel: { message: 'Grade Score', context: 'Field label' },
  saveGradeAction: { message: 'Save Grade', context: 'Button' },
  feedbackPlaceholder: { message: 'Feedback comments for student...', context: 'Field label' },
});

export default {
  name: 'AssignmentsRootPage',
  components: {
    CoachAppBarPage,
    YouTubePlayer,
  },
  setup() {
    const { classId } = useCoreCoach();
    const loading = ref(false);
    const assignments = ref([]);

    const showCreateModal = ref(false);
    const newForm = reactive({
      title: '',
      description: '',
      video_url: '',
      max_points: 100,
      due_date: '',
      allow_text_submission: true,
      allow_file_upload: true,
    });

    const activeSubmissionsAssignment = ref(null);
    const submissionsLoading = ref(false);
    const submissionsList = ref([]);
    const gradingForms = reactive({});

    const {
      backToClassHome$,
      pageTitle$,
      pageSubtitle$,
      createAssignmentButton$,
      viewGradebookButton$,
      viewDiscussionsButton$,
      noAssignmentsTitle$,
      noAssignmentsDesc$,
      createFirstAssignmentButton$,
      activeLabel$,
      inactiveLabel$,
      pointsLabel$,
      submissionsLabel$,
      gradedLabel$,
      viewSubmissionsButton$,
      deleteButton$,
      newAssignmentModalTitle$,
      saveAssignmentAction$,
      cancelAction$,
      closeAction$,
      assignmentTitleLabel$,
      assignmentInstructionsLabel$,
      youtubeUrlLabel$,
      youtubeUrlPlaceholder$,
      youtubeHelpText$,
      maxPointsLabel$,
      dueDateLabel$,
      allowTextLabel$,
      allowFileLabel$,
      submissionsForTitle$,
      noSubmissionsYet$,
      gradedStatus$,
      submittedStatus$,
      studentAnswerLabel$,
      attachedFileLabel$,
      downloadAttachmentLabel$,
      scoreLabel$,
      saveGradeAction$,
      feedbackPlaceholder$,
    } = strings;

    async function fetchAssignments() {
      loading.value = true;
      try {
        const collection = await AssignmentResource.fetchCollection({
          getParams: { collection: classId.value },
          force: true,
        });
        assignments.value = collection;
      } catch (err) {
        console.error('Error fetching assignments', err);
      } finally {
        loading.value = false;
      }
    }

    onMounted(() => {
      fetchAssignments();
    });

    function openCreateModal() {
      newForm.title = '';
      newForm.description = '';
      newForm.video_url = '';
      newForm.max_points = 100;
      newForm.due_date = '';
      newForm.allow_text_submission = true;
      newForm.allow_file_upload = true;
      showCreateModal.value = true;
    }

    function closeCreateModal() {
      showCreateModal.value = false;
    }

    async function submitNewAssignment() {
      if (!newForm.title.trim()) {
        return;
      }
      try {
        const payload = {
          title: newForm.title.trim(),
          description: newForm.description.trim(),
          video_url: newForm.video_url.trim(),
          max_points: newForm.max_points || 100,
          collection: classId.value,
          allow_text_submission: newForm.allow_text_submission,
          allow_file_upload: newForm.allow_file_upload,
          is_active: true,
        };
        if (newForm.due_date) {
          payload.due_date = new Date(newForm.due_date).toISOString();
        }
        await AssignmentResource.createModel(payload).save();
        closeCreateModal();
        fetchAssignments();
      } catch (err) {
        console.error('Failed to create assignment', err);
      }
    }

    async function confirmDelete(assignment) {
      if (window.confirm(`Are you sure you want to delete "${assignment.title}"?`)) {
        try {
          await AssignmentResource.deleteModel({ id: assignment.id });
          fetchAssignments();
        } catch (err) {
          console.error('Failed to delete assignment', err);
        }
      }
    }

    async function openSubmissionsDrawer(assignment) {
      activeSubmissionsAssignment.value = assignment;
      submissionsLoading.value = true;
      try {
        const subs = await AssignmentSubmissionResource.fetchCollection({
          getParams: { assignment: assignment.id },
          force: true,
        });
        submissionsList.value = subs;
        subs.forEach(s => {
          gradingForms[s.id] = {
            grade: s.grade,
            feedback: s.feedback || '',
          };
        });
      } catch (err) {
        console.error('Failed to load submissions', err);
      } finally {
        submissionsLoading.value = false;
      }
    }

    function closeSubmissionsDrawer() {
      activeSubmissionsAssignment.value = null;
      submissionsList.value = [];
    }

    async function submitGrade(sub) {
      const form = gradingForms[sub.id];
      if (!form) return;
      try {
        await AssignmentSubmissionResource.gradeSubmission(sub.id, {
          grade: form.grade,
          feedback: form.feedback,
        });
        sub.grade = form.grade;
        sub.feedback = form.feedback;
        sub.status = 'graded';
        fetchAssignments();
      } catch (err) {
        console.error('Failed to grade submission', err);
      }
    }

    function formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    }

    return {
      classId,
      PageNames,
      loading,
      assignments,
      showCreateModal,
      newForm,
      activeSubmissionsAssignment,
      submissionsLoading,
      submissionsList,
      gradingForms,
      openCreateModal,
      closeCreateModal,
      submitNewAssignment,
      confirmDelete,
      openSubmissionsDrawer,
      closeSubmissionsDrawer,
      submitGrade,
      formatDate,
      backToClassHome$,
      pageTitle$,
      pageSubtitle$,
      createAssignmentButton$,
      viewGradebookButton$,
      viewDiscussionsButton$,
      noAssignmentsTitle$,
      noAssignmentsDesc$,
      createFirstAssignmentButton$,
      activeLabel$,
      inactiveLabel$,
      pointsLabel$,
      submissionsLabel$,
      gradedLabel$,
      viewSubmissionsButton$,
      deleteButton$,
      newAssignmentModalTitle$,
      saveAssignmentAction$,
      cancelAction$,
      closeAction$,
      assignmentTitleLabel$,
      assignmentInstructionsLabel$,
      youtubeUrlLabel$,
      youtubeUrlPlaceholder$,
      youtubeHelpText$,
      maxPointsLabel$,
      dueDateLabel$,
      allowTextLabel$,
      allowFileLabel$,
      submissionsForTitle$,
      noSubmissionsYet$,
      gradedStatus$,
      submittedStatus$,
      studentAnswerLabel$,
      attachedFileLabel$,
      downloadAttachmentLabel$,
      scoreLabel$,
      saveGradeAction$,
      feedbackPlaceholder$,
    };
  },
};
</script>

<style lang="scss" scoped>
.assignments-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.header-nav {
  margin-bottom: 12px;
}

.back-link {
  font-weight: 600;
  text-decoration: none;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 28px;
}

.page-title {
  margin: 0 0 4px 0;
  font-size: 26px;
  font-weight: 700;
}

.page-subtitle {
  margin: 0;
  font-size: 15px;
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.empty-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  border-radius: 12px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.assignments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.assignment-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.card-top {
  padding: 20px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.status-pill {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 9999px;
  background-color: #e5e7eb;
  color: #4b5563;
  text-transform: uppercase;

  &.is-active {
    background-color: #dcfce7;
    color: #166534;
  }
}

.due-date,
.max-pts {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
}

.assignment-title {
  margin: 0 0 8px 0;
  font-size: 19px;
  font-weight: 700;
}

.assignment-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
}

.video-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background-color: #fef2f2;
}

.video-tag {
  background-color: #dc2626;
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.video-url-snippet {
  font-size: 11px;
  color: #991b1b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-bottom {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.submission-stats {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-bubble {
  font-size: 12px;
  color: #374151;

  &.graded {
    color: #15803d;
  }
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-section {
  margin-top: 4px;
}

.form-hint {
  margin: 4px 0 8px 0;
  font-size: 12px;
}

.modal-preview {
  margin-top: 8px;
}

.form-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
}

.date-input-box {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.date-label {
  font-size: 12px;
  font-weight: 600;
}

.native-date-input {
  padding: 8px 12px;
  font-size: 14px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.submissions-drawer {
  max-height: 70vh;
  overflow-y: auto;
}

.empty-submissions {
  padding: 30px;
  text-align: center;
  color: #6b7280;
}

.submissions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.submission-item {
  border-radius: 8px;
  overflow: hidden;
}

.sub-header {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.student-name {
  font-size: 15px;
}

.sub-date {
  font-size: 12px;
}

.sub-status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 9999px;

  &.submitted {
    background-color: #fef3c7;
    color: #92400e;
  }

  &.graded {
    background-color: #dcfce7;
    color: #166534;
  }
}

.sub-body,
.sub-attachment {
  padding: 0 16px 12px 16px;
}

.section-tag {
  font-size: 12px;
  font-weight: 700;
  color: #4b5563;
  display: block;
  margin-bottom: 4px;
}

.sub-text {
  margin: 0;
  font-size: 14px;
  background: #f9fafb;
  padding: 10px;
  border-radius: 6px;
  white-space: pre-wrap;
}

.attachment-link {
  font-size: 14px;
  font-weight: 600;
  color: #2563eb;
  text-decoration: underline;
}

.grading-form {
  padding: 12px 16px;
}

.grading-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 10px;
}

.score-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-lbl {
  font-size: 13px;
  font-weight: 600;
}

.grade-input {
  width: 90px;
  padding: 6px 10px;
  font-size: 14px;
  font-weight: 700;
  border-radius: 4px;
  border: 1px solid #9ca3af;
}
</style>
