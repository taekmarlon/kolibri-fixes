<template>

  <LearnAppBarPage
    :appBarTitle="learnString('learnLabel')"
    :loading="loading"
  >
    <KCircularLoader v-if="loading" />
    <div
      v-else
      role="main"
      class="assignment-detail-container"
    >
      <KBreadcrumbs
        :items="breadcrumbs"
        :ariaLabel="learnString('classesAndAssignmentsLabel')"
      />

      <!-- Top Header & Metadata -->
      <div
        class="assignment-header-card"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
        }"
      >
        <div class="header-main">
          <div class="header-title-row">
            <h1 class="assignment-title" :style="{ color: $themeTokens.text }">
              <KLabeledIcon
                icon="edit"
                :label="assignment.title"
              />
            </h1>
            <div class="header-badges">
              <span
                v-if="submission && submission.status === 'graded'"
                class="badge graded-badge"
              >
                ✓ {{ gradedLabel$() }}: {{ submission.points_awarded }}/{{ assignment.points_possible }} {{ pointsLabel$() }}
              </span>
              <span
                v-else-if="submission"
                class="badge submitted-badge"
              >
                {{ submittedLabel$() }}
              </span>
              <span
                v-else
                class="badge pending-badge"
              >
                {{ notSubmittedLabel$() }}
              </span>
            </div>
          </div>

          <div class="assignment-metadata" :style="{ color: $themeTokens.annotation }">
            <span class="meta-item">
              <strong>{{ pointsLabel$() }}:</strong> {{ assignment.points_possible }}
            </span>
            <span class="meta-item">
              <strong>{{ dueLabel$() }}:</strong>
              {{ assignment.due_date ? formatDate(assignment.due_date) : noDueDate$() }}
            </span>
            <span v-if="assignment.allow_late_submissions" class="meta-item">
              • {{ lateSubmissionsAllowed$() }}
            </span>
          </div>
        </div>

        <!-- Instructions / Description -->
        <div
          v-if="assignment.description"
          class="assignment-instructions"
          :style="{
            borderTop: `1px solid ${$themeTokens.fineLine}`,
            color: $themeTokens.text,
          }"
        >
          <h2 class="section-title">
            {{ instructionsHeading$() }}
          </h2>
          <div class="instructions-content">
            {{ assignment.description }}
          </div>
        </div>
      </div>

      <!-- Native YouTube Video Player Embed (If video URL attached to this assignment) -->
      <div
        v-if="assignment.video_url"
        class="video-section-card"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
        }"
      >
        <div class="video-header">
          <h2 class="section-title" :style="{ color: $themeTokens.text }">
            🎬 {{ videoLessonHeading$() }}
          </h2>
          <p class="video-subtext" :style="{ color: $themeTokens.annotation }">
            {{ videoLessonSubtext$() }}
          </p>
        </div>
        <div class="video-player-container">
          <YouTubePlayer
            :videoUrl="assignment.video_url"
            :title="assignment.title"
          />
        </div>
      </div>

      <!-- Grade & Teacher Feedback Card (When graded) -->
      <div
        v-if="submission && submission.status === 'graded'"
        class="feedback-card"
        :style="{
          backgroundColor: '#f0fdf4',
          border: '1.5px solid #22c55e',
        }"
      >
        <div class="feedback-header">
          <div class="grade-score" style="color: #15803d;">
            ★ {{ scoreHeading$() }}: {{ submission.points_awarded }} / {{ assignment.points_possible }}
            <span class="score-percent">
              ({{ Math.round((submission.points_awarded / (assignment.points_possible || 1)) * 100) }}%)
            </span>
          </div>
          <div v-if="submission.graded_at" class="graded-at" style="color: #166534;">
            {{ gradedOnLabel$() }} {{ formatDate(submission.graded_at) }}
          </div>
        </div>
        <div v-if="submission.feedback" class="feedback-body" style="color: #166534;">
          <strong>{{ coachFeedbackLabel$() }}:</strong>
          <blockquote class="feedback-quote">
            {{ submission.feedback }}
          </blockquote>
        </div>
      </div>

      <!-- Submission Workspace Card -->
      <div
        class="submission-card"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
        }"
      >
        <h2 class="section-title" :style="{ color: $themeTokens.text }">
          {{ submissionSectionHeading$() }}
        </h2>
        <p class="submission-subtitle" :style="{ color: $themeTokens.annotation }">
          {{ submissionInstructions$() }}
        </p>

        <!-- Current File Attachment if already submitted -->
        <div
          v-if="submission && submission.file"
          class="existing-file-box"
          :style="{
            backgroundColor: $themePalette.grey.v_100,
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
        >
          <KIcon icon="attachment" />
          <span class="file-name">{{ existingFileName }}</span>
          <a
            :href="submission.file"
            target="_blank"
            rel="noopener noreferrer"
            class="download-link"
          >
            {{ downloadAttachment$() }}
          </a>
        </div>

        <!-- Written Text Answer Form -->
        <div class="form-group">
          <label class="form-label" :style="{ color: $themeTokens.text }">
            {{ yourResponseLabel$() }}
          </label>
          <textarea
            v-model="submissionText"
            rows="6"
            class="textarea-input"
            :placeholder="responsePlaceholder$()"
            :style="{
              borderColor: $themeTokens.fineLine,
              backgroundColor: $themeTokens.surface,
              color: $themeTokens.text,
            }"
          ></textarea>
        </div>

        <!-- File Upload Field -->
        <div class="form-group">
          <label class="form-label" :style="{ color: $themeTokens.text }">
            {{ attachFileLabel$() }}
          </label>
          <input
            type="file"
            class="file-input"
            @change="handleFileUpload"
          />
          <p class="file-hint" :style="{ color: $themeTokens.annotation }">
            {{ fileHint$() }}
          </p>
        </div>

        <!-- Success notification -->
        <div
          v-if="saveSuccess"
          class="success-alert"
          style="background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; padding: 12px; border-radius: 6px; margin-bottom: 16px;"
        >
          ✓ {{ submissionSavedSuccess$() }}
        </div>

        <!-- Action Button -->
        <div class="action-row">
          <KButton
            :text="submission ? resubmitButton$() : submitAssignmentButton$()"
            :primary="true"
            appearance="raised-button"
            icon="upload"
            :disabled="submitting || (!submissionText.trim() && !selectedFile && !submission)"
            @click="submitHomework"
          />
        </div>
      </div>
    </div>
  </LearnAppBarPage>

</template>

<script>

  import { ref, computed, onMounted } from 'vue';
  import KBreadcrumbs from 'kolibri-design-system/lib/KBreadcrumbs';
  import { createTranslator } from 'kolibri/utils/i18n';
  import commonLearnStrings from '../commonLearnStrings';
  import LearnAppBarPage from '../LearnAppBarPage';
  import YouTubePlayer from 'kolibri-common/components/YouTubePlayer.vue';
  import AssignmentResource from 'kolibri-common/apiResources/AssignmentResource';
  import AssignmentSubmissionResource from 'kolibri-common/apiResources/AssignmentSubmissionResource';
  import useLearnerResources from '../../composables/useLearnerResources';
  import { ClassesPageNames } from '../../constants';

  const strings = createTranslator('LearnerAssignmentDetailPageStrings', {
    gradedLabel: {
      message: 'Graded',
      context: 'Status label for graded submission',
    },
    submittedLabel: {
      message: 'Submitted — Pending Review',
      context: 'Status label for submitted work',
    },
    notSubmittedLabel: {
      message: 'Not Submitted Yet',
      context: 'Status label for unsubmitted work',
    },
    pointsLabel: {
      message: 'Points',
      context: 'Points label',
    },
    dueLabel: {
      message: 'Due',
      context: 'Due label',
    },
    noDueDate: {
      message: 'No due date',
      context: 'Fallback when no due date',
    },
    lateSubmissionsAllowed: {
      message: 'Late submissions accepted',
      context: 'Note that late submissions are allowed',
    },
    instructionsHeading: {
      message: 'Instructions & Notes',
      context: 'Heading for assignment instructions',
    },
    videoLessonHeading: {
      message: 'Watch Video Lesson',
      context: 'Section heading for embedded video lesson',
    },
    videoLessonSubtext: {
      message: 'Watch this instructional video directly within Kolibri before completing your homework.',
      context: 'Subtext explaining the native video embed',
    },
    scoreHeading: {
      message: 'Your Score',
      context: 'Heading for score display',
    },
    gradedOnLabel: {
      message: 'Reviewed on',
      context: 'Date label when graded',
    },
    coachFeedbackLabel: {
      message: 'Coach Feedback',
      context: 'Label for teacher feedback',
    },
    submissionSectionHeading: {
      message: 'Your Homework Submission',
      context: 'Heading for submission form',
    },
    submissionInstructions: {
      message: 'Write your answer or upload your assignment document below. Your coach will review and grade your work.',
      context: 'Instructions for submitting homework',
    },
    downloadAttachment: {
      message: 'Download submitted file',
      context: 'Link to download previously submitted file',
    },
    yourResponseLabel: {
      message: 'Written Answer / Notes',
      context: 'Label for response textarea',
    },
    responsePlaceholder: {
      message: 'Type your homework answer, summary, or explanations here...',
      context: 'Placeholder text in answer textarea',
    },
    attachFileLabel: {
      message: 'Attach File (PDF, DOCX, ZIP, or Image)',
      context: 'Label for file upload',
    },
    fileHint: {
      message: 'Accepted formats: documents, archives, images. Max 100MB.',
      context: 'File upload hint',
    },
    submitAssignmentButton: {
      message: 'Submit Assignment',
      context: 'Button label to submit homework',
    },
    resubmitButton: {
      message: 'Update / Resubmit Homework',
      context: 'Button label to update homework',
    },
    submissionSavedSuccess: {
      message: 'Your homework has been submitted successfully!',
      context: 'Alert message upon submission',
    },
  });

  export default {
    name: 'LearnerAssignmentDetailPage',
    components: {
      KBreadcrumbs,
      LearnAppBarPage,
      YouTubePlayer,
    },
    mixins: [commonLearnStrings],
    props: {
      classId: {
        type: String,
        required: true,
      },
      assignmentId: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      const loading = ref(true);
      const submitting = ref(false);
      const saveSuccess = ref(false);
      const assignment = ref({});
      const submission = ref(null);
      const submissionText = ref('');
      const selectedFile = ref(null);

      const { getClass, fetchClass } = useLearnerResources();

      const currentClass = computed(() => {
        return getClass(props.classId) || {};
      });

      const className = computed(() => {
        return currentClass.value.name || '';
      });

      const breadcrumbs = computed(() => {
        return [
          {
            text: commonLearnStrings.methods.learnString('classesLabel') || 'Classes',
            link: { name: ClassesPageNames.ALL_CLASSES },
          },
          {
            text: className.value || 'Class',
            link: {
              name: ClassesPageNames.CLASS_ASSIGNMENTS,
              params: { classId: props.classId },
            },
          },
          {
            text: assignment.value.title || 'Assignment',
          },
        ];
      });

      const existingFileName = computed(() => {
        if (!submission.value || !submission.value.file) return '';
        const parts = submission.value.file.split('/');
        return parts[parts.length - 1];
      });

      function loadData() {
        loading.value = true;
        fetchClass(props.classId).catch(() => {});
        Promise.all([
          AssignmentResource.fetchModel({ id: props.assignmentId }),
          AssignmentSubmissionResource.fetchCollection({
            getParams: { assignment: props.assignmentId },
          }),
        ])
          .then(([assignmentData, submissionsData]) => {
            assignment.value = assignmentData || {};
            const userSub = submissionsData && submissionsData.length > 0 ? submissionsData[0] : null;
            submission.value = userSub;
            if (userSub) {
              submissionText.value = userSub.submission_text || '';
            }
            loading.value = false;
          })
          .catch(() => {
            loading.value = false;
          });
      }

      function handleFileUpload(event) {
        if (event.target.files && event.target.files.length > 0) {
          selectedFile.value = event.target.files[0];
        }
      }

      function submitHomework() {
        submitting.value = true;
        saveSuccess.value = false;

        let promise;
        if (selectedFile.value) {
          const formData = new FormData();
          formData.append('assignment', props.assignmentId);
          formData.append('submission_text', submissionText.value);
          formData.append('file', selectedFile.value);

          if (submission.value && submission.value.id) {
            promise = AssignmentSubmissionResource.saveModel({
              id: submission.value.id,
              data: formData,
            });
          } else {
            promise = AssignmentSubmissionResource.saveModel({
              data: formData,
            });
          }
        } else {
          const payload = {
            assignment: props.assignmentId,
            submission_text: submissionText.value,
          };
          if (submission.value && submission.value.id) {
            promise = AssignmentSubmissionResource.saveModel({
              id: submission.value.id,
              data: payload,
            });
          } else {
            promise = AssignmentSubmissionResource.saveModel({
              data: payload,
            });
          }
        }

        promise
          .then(updatedSub => {
            submission.value = updatedSub;
            submitting.value = false;
            saveSuccess.value = true;
            setTimeout(() => {
              saveSuccess.value = false;
            }, 5000);
          })
          .catch(() => {
            submitting.value = false;
          });
      }

      function formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString(undefined, {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        });
      }

      onMounted(() => {
        loadData();
      });

      return {
        loading,
        submitting,
        saveSuccess,
        assignment,
        submission,
        submissionText,
        selectedFile,
        breadcrumbs,
        existingFileName,
        handleFileUpload,
        submitHomework,
        formatDate,
        ...strings,
      };
    },
  };

</script>

<style lang="scss" scoped>

  .assignment-detail-container {
    max-width: 960px;
    margin: 0 auto;
    padding-bottom: 60px;
  }

  .assignment-header-card,
  .video-section-card,
  .submission-card {
    border-radius: 8px;
    padding: 24px;
    margin-top: 24px;
  }

  .header-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }

  .assignment-title {
    font-size: 24px;
    margin: 0;
  }

  .header-badges {
    display: flex;
    gap: 8px;
  }

  .badge {
    font-size: 12px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
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

  .assignment-metadata {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-top: 12px;
    font-size: 14px;
  }

  .assignment-instructions {
    margin-top: 20px;
    padding-top: 16px;
  }

  .section-title {
    font-size: 18px;
    margin: 0 0 8px 0;
  }

  .instructions-content {
    line-height: 1.6;
    font-size: 15px;
    white-space: pre-wrap;
  }

  .video-header {
    margin-bottom: 16px;
  }

  .video-subtext {
    font-size: 13px;
    margin: 4px 0 0 0;
  }

  .video-player-container {
    border-radius: 8px;
    overflow: hidden;
  }

  .feedback-card {
    border-radius: 8px;
    padding: 20px 24px;
    margin-top: 24px;
  }

  .feedback-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
  }

  .grade-score {
    font-size: 20px;
    font-weight: 800;
  }

  .score-percent {
    font-size: 15px;
    font-weight: 600;
    margin-left: 6px;
  }

  .graded-at {
    font-size: 13px;
  }

  .feedback-body {
    margin-top: 12px;
    font-size: 15px;
  }

  .feedback-quote {
    margin: 6px 0 0 0;
    padding: 10px 14px;
    background: rgba(255, 255, 255, 0.6);
    border-left: 4px solid #16a34a;
    border-radius: 4px;
    font-style: italic;
    white-space: pre-wrap;
  }

  .submission-subtitle {
    font-size: 14px;
    margin: 4px 0 20px 0;
  }

  .existing-file-box {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 20px;
    font-size: 14px;
  }

  .file-name {
    flex: 1;
    font-weight: 600;
  }

  .download-link {
    color: #2563eb;
    text-decoration: underline;
  }

  .form-group {
    margin-bottom: 20px;
  }

  .form-label {
    display: block;
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 8px;
  }

  .textarea-input {
    width: 100%;
    padding: 12px;
    border-radius: 6px;
    font-family: inherit;
    font-size: 14px;
    line-height: 1.5;
    box-sizing: border-box;
    outline: none;
    border-width: 1px;
    border-style: solid;
  }

  .file-input {
    display: block;
    margin-top: 4px;
    font-size: 14px;
  }

  .file-hint {
    font-size: 12px;
    margin: 4px 0 0 0;
  }

  .action-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }

</style>
