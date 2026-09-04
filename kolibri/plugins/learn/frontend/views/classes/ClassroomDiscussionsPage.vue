<template>

  <LearnAppBarPage
    :appBarTitle="learnString('learnLabel')"
    :loading="loading"
  >
    <KCircularLoader v-if="loading" />
    <div
      v-else
      role="main"
      class="discussions-container"
    >
      <KBreadcrumbs
        :items="breadcrumbs"
        :ariaLabel="learnString('classesAndAssignmentsLabel')"
      />

      <!-- Header Row -->
      <div class="discussions-header-row">
        <div>
          <h1 class="page-title" :style="{ color: $themeTokens.text }">
            <KLabeledIcon
              icon="people"
              :label="discussionsTitle$()"
            />
          </h1>
          <p class="page-subtitle" :style="{ color: $themeTokens.annotation }">
            {{ discussionsSubtitle$({ className }) }}
          </p>
        </div>
        <div v-if="!selectedThread">
          <KButton
            :text="newQuestionButton$()"
            :primary="true"
            appearance="raised-button"
            icon="plus"
            @click="showCreateModal = true"
          />
        </div>
      </div>

      <!-- Thread Detail View (When a thread is selected) -->
      <div v-if="selectedThread" class="thread-detail-wrapper">
        <KButton
          :text="backToAllThreads$()"
          appearance="basic-link"
          icon="back"
          class="back-button"
          @click="selectedThread = null"
        />

        <div
          class="thread-detail-card"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
        >
          <!-- Original Post -->
          <div class="op-header">
            <div class="op-meta-row">
              <span v-if="selectedThread.pinned" class="pinned-pill">
                📌 {{ pinnedPill$() }}
              </span>
              <span v-if="selectedThread.closed" class="closed-pill">
                🔒 {{ closedPill$() }}
              </span>
              <span class="author-name" :style="{ color: $themeTokens.text }">
                {{ selectedThread.author_name || selectedThread.user_id }}
              </span>
              <span class="post-time" :style="{ color: $themeTokens.annotation }">
                • {{ formatDate(selectedThread.created_at) }}
              </span>
            </div>
            <h2 class="op-title" :style="{ color: $themeTokens.text }">
              {{ selectedThread.title }}
            </h2>
          </div>

          <div
            class="op-body"
            :style="{
              borderTop: `1px solid ${$themeTokens.fineLine}`,
              color: $themeTokens.text,
            }"
          >
            {{ selectedThread.content }}
          </div>
        </div>

        <!-- Replies Section -->
        <div class="replies-section">
          <h3 class="replies-heading" :style="{ color: $themeTokens.text }">
            {{ repliesHeading$() }} ({{ replies.length }})
          </h3>

          <div v-if="replies.length === 0" class="no-replies" :style="{ color: $themeTokens.annotation }">
            {{ noRepliesYet$() }}
          </div>

          <div
            v-for="reply in replies"
            :key="reply.id"
            class="reply-card"
            :class="{ 'is-endorsed': reply.endorsed_by_coach }"
            :style="{
              backgroundColor: reply.endorsed_by_coach ? '#f0fdf4' : $themeTokens.surface,
              border: reply.endorsed_by_coach ? '1.5px solid #22c55e' : `1px solid ${$themeTokens.fineLine}`,
            }"
          >
            <!-- Endorsed Banner -->
            <div v-if="reply.endorsed_by_coach" class="endorsed-banner">
              ⭐ {{ coachEndorsedAnswer$() }}
            </div>

            <div class="reply-meta" :style="{ color: $themeTokens.annotation }">
              <strong :style="{ color: $themeTokens.text }">
                {{ reply.author_name || reply.user_id }}
              </strong>
              <span>• {{ formatDate(reply.created_at) }}</span>
            </div>

            <div class="reply-content" :style="{ color: $themeTokens.text }">
              {{ reply.content }}
            </div>
          </div>

          <!-- Add Reply Box -->
          <div
            v-if="!selectedThread.closed"
            class="add-reply-box"
            :style="{
              backgroundColor: $themeTokens.surface,
              border: `1px solid ${$themeTokens.fineLine}`,
            }"
          >
            <label class="reply-label" :style="{ color: $themeTokens.text }">
              {{ leaveReplyLabel$() }}
            </label>
            <textarea
              v-model="newReplyText"
              rows="4"
              class="reply-textarea"
              :placeholder="replyPlaceholder$()"
              :style="{
                borderColor: $themeTokens.fineLine,
                backgroundColor: $themeTokens.surface,
                color: $themeTokens.text,
              }"
            ></textarea>
            <div class="reply-action-row">
              <KButton
                :text="postReplyButton$()"
                :primary="true"
                appearance="raised-button"
                icon="forward"
                :disabled="submittingReply || !newReplyText.trim()"
                @click="submitReply"
              />
            </div>
          </div>

          <div
            v-else
            class="closed-thread-notice"
            :style="{ color: $themeTokens.annotation }"
          >
            🔒 {{ threadIsClosedNotice$() }}
          </div>
        </div>
      </div>

      <!-- Threads List View -->
      <div v-else class="threads-list-wrapper">
        <div v-if="threads.length === 0" class="no-threads" :style="{ color: $themeTokens.annotation }">
          <p>{{ noQuestionsYet$() }}</p>
          <KButton
            :text="newQuestionButton$()"
            :primary="true"
            appearance="raised-button"
            icon="plus"
            @click="showCreateModal = true"
          />
        </div>

        <div
          v-for="thread in sortedThreads"
          :key="thread.id"
          class="thread-row-card"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
          @click="selectThread(thread)"
        >
          <div class="thread-row-left">
            <div class="thread-row-meta">
              <span v-if="thread.pinned" class="pinned-pill">
                📌 {{ pinnedPill$() }}
              </span>
              <span v-if="thread.closed" class="closed-pill">
                🔒 {{ closedPill$() }}
              </span>
              <span class="thread-author" :style="{ color: $themeTokens.annotation }">
                {{ thread.author_name || thread.user_id }}
              </span>
              <span class="thread-date" :style="{ color: $themeTokens.annotation }">
                • {{ formatDate(thread.created_at) }}
              </span>
            </div>
            <h2 class="thread-row-title" :style="{ color: $themeTokens.text }">
              {{ thread.title }}
            </h2>
            <p class="thread-preview" :style="{ color: $themeTokens.annotation }">
              {{ thread.content }}
            </p>
          </div>

          <div class="thread-row-right">
            <div class="reply-counter" :style="{ backgroundColor: $themePalette.grey.v_200, color: $themeTokens.text }">
              💬 {{ thread.replies_count || 0 }} {{ repliesCountLabel$() }}
            </div>
            <KButton
              appearance="basic-link"
              :text="viewThreadButton$()"
            />
          </div>
        </div>
      </div>

      <!-- New Thread / Ask Question Modal -->
      <KModal
        v-if="showCreateModal"
        :title="askQuestionModalTitle$()"
        :submitText="postQuestionButton$()"
        :cancelText="cancelButton$()"
        :submitDisabled="submittingThread || !newThreadTitle.trim() || !newThreadContent.trim()"
        @submit="submitNewThread"
        @cancel="showCreateModal = false"
      >
        <div class="modal-body">
          <div class="form-field">
            <label class="field-label" :style="{ color: $themeTokens.text }">
              {{ questionTitleLabel$() }}
            </label>
            <input
              v-model="newThreadTitle"
              type="text"
              class="text-input"
              :placeholder="questionTitlePlaceholder$()"
              :style="{
                borderColor: $themeTokens.fineLine,
                backgroundColor: $themeTokens.surface,
                color: $themeTokens.text,
              }"
            />
          </div>

          <div class="form-field" style="margin-top: 16px;">
            <label class="field-label" :style="{ color: $themeTokens.text }">
              {{ questionDetailsLabel$() }}
            </label>
            <textarea
              v-model="newThreadContent"
              rows="6"
              class="textarea-input"
              :placeholder="questionDetailsPlaceholder$()"
              :style="{
                borderColor: $themeTokens.fineLine,
                backgroundColor: $themeTokens.surface,
                color: $themeTokens.text,
              }"
            ></textarea>
          </div>
        </div>
      </KModal>
    </div>
  </LearnAppBarPage>

</template>

<script>

  import { ref, computed, onMounted } from 'vue';
  import KBreadcrumbs from 'kolibri-design-system/lib/KBreadcrumbs';
  import KModal from 'kolibri-design-system/lib/KModal';
  import { createTranslator } from 'kolibri/utils/i18n';
  import commonLearnStrings from '../commonLearnStrings';
  import LearnAppBarPage from '../LearnAppBarPage';
  import DiscussionThreadResource from 'kolibri-common/apiResources/DiscussionThreadResource';
  import DiscussionReplyResource from 'kolibri-common/apiResources/DiscussionReplyResource';
  import useLearnerResources from '../../composables/useLearnerResources';
  import { ClassesPageNames } from '../../constants';

  const strings = createTranslator('ClassroomDiscussionsPageStrings', {
    discussionsTitle: {
      message: 'Classroom Discussions',
      context: 'Page title for student discussion boards',
    },
    discussionsSubtitle: {
      message: 'Ask questions, discuss topics, and learn together in {className}.',
      context: 'Subtitle describing discussion boards',
    },
    newQuestionButton: {
      message: 'Ask a Question',
      context: 'Button label to create a new discussion thread',
    },
    backToAllThreads: {
      message: 'All Discussions',
      context: 'Button to go back to discussion list',
    },
    pinnedPill: {
      message: 'Pinned',
      context: 'Badge for pinned discussion threads',
    },
    closedPill: {
      message: 'Closed',
      context: 'Badge for closed discussion threads',
    },
    repliesHeading: {
      message: 'Replies & Answers',
      context: 'Heading for replies in thread detail',
    },
    noRepliesYet: {
      message: 'No replies yet. Be the first to answer!',
      context: 'Message when a thread has no replies',
    },
    coachEndorsedAnswer: {
      message: 'Teacher-Endorsed Answer',
      context: 'Banner for replies verified/endorsed by the coach',
    },
    leaveReplyLabel: {
      message: 'Your Reply',
      context: 'Label for reply textarea',
    },
    replyPlaceholder: {
      message: 'Write a helpful response or share your solution...',
      context: 'Placeholder for reply textarea',
    },
    postReplyButton: {
      message: 'Post Reply',
      context: 'Button label to submit a reply',
    },
    threadIsClosedNotice: {
      message: 'This discussion thread has been closed by your teacher. New replies are disabled.',
      context: 'Notice when thread is closed',
    },
    noQuestionsYet: {
      message: 'No discussion questions yet in this classroom. Have a question about a lesson or assignment? Start a discussion!',
      context: 'Empty state message when no threads exist',
    },
    repliesCountLabel: {
      message: 'replies',
      context: 'Label suffix for reply counter',
    },
    viewThreadButton: {
      message: 'Open ➔',
      context: 'Action label to view a thread',
    },
    askQuestionModalTitle: {
      message: 'Ask a Question',
      context: 'Modal title for creating a thread',
    },
    postQuestionButton: {
      message: 'Post Question',
      context: 'Modal submit button',
    },
    cancelButton: {
      message: 'Cancel',
      context: 'Modal cancel button',
    },
    questionTitleLabel: {
      message: 'Question / Topic Title',
      context: 'Form field label for title',
    },
    questionTitlePlaceholder: {
      message: 'e.g., How do we solve question #3 in the homework?',
      context: 'Form field placeholder for title',
    },
    questionDetailsLabel: {
      message: 'Details & Context',
      context: 'Form field label for details',
    },
    questionDetailsPlaceholder: {
      message: 'Provide details about what you tried or what you would like to discuss...',
      context: 'Form field placeholder for details',
    },
  });

  export default {
    name: 'ClassroomDiscussionsPage',
    components: {
      KBreadcrumbs,
      KModal,
      LearnAppBarPage,
    },
    mixins: [commonLearnStrings],
    props: {
      classId: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      const loading = ref(true);
      const threads = ref([]);
      const selectedThread = ref(null);
      const replies = ref([]);
      const showCreateModal = ref(false);
      const newThreadTitle = ref('');
      const newThreadContent = ref('');
      const newReplyText = ref('');
      const submittingThread = ref(false);
      const submittingReply = ref(false);

      const { getClass, fetchClass } = useLearnerResources();

      const currentClass = computed(() => {
        return getClass(props.classId) || {};
      });

      const className = computed(() => {
        return currentClass.value.name || 'Class';
      });

      const breadcrumbs = computed(() => {
        return [
          {
            text: commonLearnStrings.methods.learnString('classesLabel') || 'Classes',
            link: { name: ClassesPageNames.ALL_CLASSES },
          },
          {
            text: className.value,
            link: {
              name: ClassesPageNames.CLASS_ASSIGNMENTS,
              params: { classId: props.classId },
            },
          },
          {
            text: strings.discussionsTitle$(),
          },
        ];
      });

      const sortedThreads = computed(() => {
        return [...threads.value].sort((a, b) => {
          if (a.pinned && !b.pinned) return -1;
          if (!a.pinned && b.pinned) return 1;
          return new Date(b.created_at) - new Date(a.created_at);
        });
      });

      function loadThreads() {
        loading.value = true;
        fetchClass(props.classId).catch(() => {});
        DiscussionThreadResource.fetchCollection({
          getParams: { collection: props.classId },
        })
          .then(data => {
            threads.value = data || [];
            loading.value = false;
          })
          .catch(() => {
            threads.value = [];
            loading.value = false;
          });
      }

      function selectThread(thread) {
        selectedThread.value = thread;
        loadReplies(thread.id);
      }

      function loadReplies(threadId) {
        DiscussionReplyResource.fetchCollection({
          getParams: { thread: threadId },
        })
          .then(data => {
            replies.value = data || [];
          })
          .catch(() => {
            replies.value = [];
          });
      }

      function submitNewThread() {
        submittingThread.value = true;
        DiscussionThreadResource.saveModel({
          data: {
            collection: props.classId,
            title: newThreadTitle.value,
            content: newThreadContent.value,
          },
        })
          .then(created => {
            threads.value.unshift(created);
            showCreateModal.value = false;
            newThreadTitle.value = '';
            newThreadContent.value = '';
            submittingThread.value = false;
            selectThread(created);
          })
          .catch(() => {
            submittingThread.value = false;
          });
      }

      function submitReply() {
        if (!selectedThread.value || !newReplyText.value.trim()) return;
        submittingReply.value = true;
        DiscussionReplyResource.saveModel({
          data: {
            thread: selectedThread.value.id,
            content: newReplyText.value,
          },
        })
          .then(created => {
            replies.value.push(created);
            newReplyText.value = '';
            submittingReply.value = false;
            if (selectedThread.value.replies_count !== undefined) {
              selectedThread.value.replies_count += 1;
            }
          })
          .catch(() => {
            submittingReply.value = false;
          });
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
        loadThreads();
      });

      return {
        loading,
        threads,
        sortedThreads,
        selectedThread,
        replies,
        showCreateModal,
        newThreadTitle,
        newThreadContent,
        newReplyText,
        submittingThread,
        submittingReply,
        className,
        breadcrumbs,
        selectThread,
        submitNewThread,
        submitReply,
        formatDate,
        ...strings,
      };
    },
  };

</script>

<style lang="scss" scoped>

  .discussions-container {
    max-width: 960px;
    margin: 0 auto;
    padding-bottom: 60px;
  }

  .discussions-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 16px;
  }

  .page-title {
    font-size: 24px;
    margin: 0;
  }

  .page-subtitle {
    font-size: 14px;
    margin: 4px 0 0 0;
  }

  .back-button {
    margin-bottom: 16px;
  }

  .thread-detail-card,
  .reply-card,
  .add-reply-box,
  .thread-row-card {
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 16px;
  }

  .thread-row-card {
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
  }

  .thread-row-left {
    flex: 1;
    min-width: 0;
  }

  .thread-row-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
  }

  .reply-counter {
    font-size: 12px;
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 12px;
    white-space: nowrap;
  }

  .thread-row-meta,
  .op-meta-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    margin-bottom: 6px;
    flex-wrap: wrap;
  }

  .pinned-pill {
    background: #fef3c7;
    color: #92400e;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
  }

  .closed-pill {
    background: #fee2e2;
    color: #991b1b;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
  }

  .thread-row-title {
    font-size: 17px;
    margin: 0 0 6px 0;
    font-weight: 700;
  }

  .thread-preview {
    font-size: 13px;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .op-title {
    font-size: 20px;
    margin: 4px 0 0 0;
  }

  .op-body {
    margin-top: 16px;
    padding-top: 16px;
    line-height: 1.6;
    font-size: 15px;
    white-space: pre-wrap;
  }

  .replies-section {
    margin-top: 32px;
  }

  .replies-heading {
    font-size: 18px;
    margin-bottom: 16px;
  }

  .no-replies {
    font-size: 14px;
    margin-bottom: 20px;
  }

  .endorsed-banner {
    display: inline-block;
    background: #bbf7d0;
    color: #166534;
    font-size: 11px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 9999px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .reply-meta {
    font-size: 13px;
    margin-bottom: 8px;
    display: flex;
    gap: 6px;
  }

  .reply-content {
    line-height: 1.5;
    font-size: 14px;
    white-space: pre-wrap;
  }

  .reply-label,
  .field-label {
    display: block;
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 6px;
  }

  .reply-textarea,
  .textarea-input,
  .text-input {
    width: 100%;
    padding: 10px 12px;
    border-radius: 6px;
    border-width: 1px;
    border-style: solid;
    font-family: inherit;
    font-size: 14px;
    box-sizing: border-box;
    outline: none;
  }

  .reply-action-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
  }

  .closed-thread-notice {
    padding: 16px;
    border-radius: 6px;
    background: #f9fafb;
    text-align: center;
    font-size: 14px;
  }

  .no-threads {
    text-align: center;
    padding: 48px 0;
    font-size: 15px;
  }

</style>
