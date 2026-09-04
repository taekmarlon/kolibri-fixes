<template>
  <CoachAppBarPage>
    <div class="discussions-container">
      <!-- Breadcrumb Bar -->
      <div class="header-nav">
        <KRouterLink
          :to="{ name: PageNames.COURSEWORK_ASSIGNMENTS, params: { classId } }"
          class="back-link"
        >
          ← {{ backToAssignments$() }}
        </KRouterLink>
      </div>

      <!-- Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title" :style="{ color: $themeTokens.text }">
            💬 {{ pageTitle$() }}
          </h1>
          <p class="page-subtitle" :style="{ color: $themeTokens.annotation }">
            {{ pageSubtitle$() }}
          </p>
        </div>
        <KButton
          :text="newTopicAction$()"
          :primary="true"
          appearance="raised-button"
          icon="plus"
          @click="openNewThreadModal"
        />
      </div>

      <!-- Loading State -->
      <KCircularLoader v-if="loading" />

      <!-- Empty State -->
      <div
        v-else-if="threads.length === 0"
        class="empty-state"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px dashed ${$themeTokens.fineLine}`,
        }"
      >
        <span class="empty-icon">🗨️</span>
        <h2 :style="{ color: $themeTokens.text }">{{ noThreadsTitle$() }}</h2>
        <p :style="{ color: $themeTokens.annotation }">
          {{ noThreadsDesc$() }}
        </p>
        <KButton
          :text="startFirstTopicAction$()"
          :primary="true"
          appearance="raised-button"
          @click="openNewThreadModal"
        />
      </div>

      <!-- Two-Pane Forum Layout: Topics List + Active Thread View -->
      <div v-else class="forum-layout">
        <!-- Thread List Sidebar -->
        <div
          class="thread-list-pane"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
        >
          <div
            v-for="thread in threads"
            :key="thread.id"
            class="thread-tab-item"
            :class="{ 'is-selected': selectedThread && selectedThread.id === thread.id }"
            :style="{ borderBottom: `1px solid ${$themeTokens.fineLine}` }"
            @click="selectThread(thread)"
          >
            <div class="thread-badges">
              <span v-if="thread.is_pinned" class="badge-pinned">📌 {{ pinnedLabel$() }}</span>
              <span v-if="thread.is_closed" class="badge-closed">🔒 {{ closedLabel$() }}</span>
            </div>
            <h3 class="thread-item-title" :style="{ color: $themeTokens.text }">
              {{ thread.title }}
            </h3>
            <div class="thread-item-meta" :style="{ color: $themeTokens.annotation }">
              <span>{{ thread.created_by_full_name || thread.created_by_username }}</span>
              <span>• {{ thread.reply_count || 0 }} {{ repliesLabel$() }}</span>
            </div>
          </div>
        </div>

        <!-- Active Thread Detail Pane -->
        <div
          v-if="selectedThread"
          class="thread-detail-pane"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
        >
          <!-- Thread Header -->
          <div
            class="detail-header"
            :style="{
              backgroundColor: $themePalette.grey.v_100,
              borderBottom: `1px solid ${$themeTokens.fineLine}`,
            }"
          >
            <div>
              <div class="detail-badges">
                <span v-if="selectedThread.is_pinned" class="badge-pinned">📌 {{ pinnedLabel$() }}</span>
                <span v-if="selectedThread.is_closed" class="badge-closed">🔒 {{ closedLabel$() }}</span>
              </div>
              <h2 class="detail-title" :style="{ color: $themeTokens.text }">
                {{ selectedThread.title }}
              </h2>
              <div class="detail-meta" :style="{ color: $themeTokens.annotation }">
                {{ postedByLabel$() }} <strong>{{ selectedThread.created_by_full_name || selectedThread.created_by_username }}</strong>
                • {{ formatDate(selectedThread.date_created) }}
              </div>
            </div>

            <!-- Coach Controls -->
            <div class="coach-controls">
              <KButton
                :text="selectedThread.is_pinned ? unpinAction$() : pinAction$()"
                appearance="flat-button"
                @click="togglePinThread(selectedThread)"
              />
              <KButton
                :text="selectedThread.is_closed ? reopenAction$() : closeTopicAction$()"
                appearance="flat-button"
                @click="toggleCloseThread(selectedThread)"
              />
            </div>
          </div>

          <!-- Original Post Content -->
          <div class="detail-content">
            <p class="post-text">{{ selectedThread.content }}</p>
          </div>

          <!-- Replies Section -->
          <div class="replies-section">
            <h3 class="replies-header" :style="{ color: $themeTokens.text }">
              {{ repliesSectionTitle$() }} ({{ replies.length }})
            </h3>

            <KCircularLoader v-if="repliesLoading" />

            <div v-else-if="replies.length === 0" class="no-replies">
              <p :style="{ color: $themeTokens.annotation }">{{ noRepliesYet$() }}</p>
            </div>

            <div v-else class="replies-list">
              <div
                v-for="reply in replies"
                :key="reply.id"
                class="reply-card"
                :class="{ 'is-endorsed': reply.is_endorsed }"
                :style="{
                  backgroundColor: reply.is_endorsed ? '#f0fdf4' : $themePalette.grey.v_100,
                  border: reply.is_endorsed ? '2px solid #22c55e' : `1px solid ${$themeTokens.fineLine}`,
                }"
              >
                <div class="reply-top">
                  <div>
                    <strong class="reply-author">{{ reply.created_by_full_name || reply.created_by_username }}</strong>
                    <span class="reply-date" :style="{ color: $themeTokens.annotation }">
                      • {{ formatDate(reply.date_created) }}
                    </span>
                    <span v-if="reply.is_endorsed" class="endorsed-badge">
                      ⭐ {{ endorsedLabel$() }}
                    </span>
                  </div>

                  <!-- Endorse Button for Coach -->
                  <KButton
                    :text="reply.is_endorsed ? removeEndorsementAction$() : endorseAnswerAction$()"
                    appearance="flat-button"
                    :style="reply.is_endorsed ? { color: '#166534' } : {}"
                    @click="toggleEndorseReply(reply)"
                  />
                </div>

                <p class="reply-text">{{ reply.content }}</p>
              </div>
            </div>

            <!-- Reply Box (if not closed) -->
            <div
              v-if="!selectedThread.is_closed"
              class="post-reply-box"
              :style="{ borderTop: `1px solid ${$themeTokens.fineLine}` }"
            >
              <KTextbox
                v-model="newReplyText"
                :label="replyPlaceholder$()"
                :textArea="true"
                :rows="3"
              />
              <div class="reply-btn-row">
                <KButton
                  :text="postReplyAction$()"
                  :primary="true"
                  appearance="raised-button"
                  :disabled="!newReplyText.trim()"
                  @click="submitReply"
                />
              </div>
            </div>
            <div
              v-else
              class="closed-notice"
              :style="{ backgroundColor: $themePalette.grey.v_100, color: $themeTokens.annotation }"
            >
              🔒 {{ threadClosedNotice$() }}
            </div>
          </div>
        </div>
      </div>

      <!-- New Topic Modal -->
      <KModal
        v-if="showNewThreadModal"
        :title="newTopicModalTitle$()"
        :submitText="createTopicAction$()"
        :cancelText="cancelAction$()"
        @submit="submitNewThread"
        @cancel="closeNewThreadModal"
      >
        <div class="modal-form">
          <KTextbox
            v-model="newThreadForm.title"
            :label="topicTitleLabel$()"
            :required="true"
            :autofocus="true"
          />
          <KTextbox
            v-model="newThreadForm.content"
            :label="topicContentLabel$()"
            :textArea="true"
            :rows="4"
            :required="true"
          />
        </div>
      </KModal>
    </div>
  </CoachAppBarPage>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { createTranslator } from 'kolibri/utils/i18n';
import DiscussionThreadResource from 'kolibri-common/apiResources/DiscussionThreadResource';
import DiscussionReplyResource from 'kolibri-common/apiResources/DiscussionReplyResource';
import useCoreCoach from '../../composables/useCoreCoach';
import CoachAppBarPage from '../CoachAppBarPage';
import { PageNames } from '../../constants';

const strings = createTranslator('CoachDiscussionsStrings', {
  backToAssignments: { message: 'Assignments', context: 'Back link' },
  pageTitle: { message: 'Classroom Q&A & Discussions', context: 'Page title' },
  pageSubtitle: { message: 'Facilitate class discussions, answer learner inquiries, and endorse verified solutions.', context: 'Subheader' },
  newTopicAction: { message: 'New Discussion Topic', context: 'Button' },
  noThreadsTitle: { message: 'No discussions started yet', context: 'Empty state title' },
  noThreadsDesc: { message: 'Post a question or welcome prompt to initiate classroom conversation.', context: 'Empty state desc' },
  startFirstTopicAction: { message: 'Start First Discussion', context: 'Button' },
  pinnedLabel: { message: 'Pinned', context: 'Badge' },
  closedLabel: { message: 'Closed', context: 'Badge' },
  repliesLabel: { message: 'replies', context: 'Count label' },
  postedByLabel: { message: 'Posted by', context: 'Author prefix' },
  pinAction: { message: '📌 Pin Topic', context: 'Button' },
  unpinAction: { message: 'Unpin Topic', context: 'Button' },
  closeTopicAction: { message: '🔒 Close Topic', context: 'Button' },
  reopenAction: { message: 'Reopen Topic', context: 'Button' },
  repliesSectionTitle: { message: 'Classroom Responses', context: 'Section title' },
  noRepliesYet: { message: 'No responses yet. Be the first to reply!', context: 'Empty text' },
  endorsedLabel: { message: 'Teacher Endorsed', context: 'Badge' },
  endorseAnswerAction: { message: '⭐ Endorse Answer', context: 'Button' },
  removeEndorsementAction: { message: 'Remove Endorsement', context: 'Button' },
  replyPlaceholder: { message: 'Write a response or explanation...', context: 'Textarea label' },
  postReplyAction: { message: 'Post Response', context: 'Button' },
  threadClosedNotice: { message: 'This topic has been closed for new replies by the coach.', context: 'Notice' },
  newTopicModalTitle: { message: 'Start a Discussion Topic', context: 'Modal header' },
  createTopicAction: { message: 'Publish Topic', context: 'Modal submit' },
  cancelAction: { message: 'Cancel', context: 'Button' },
  topicTitleLabel: { message: 'Discussion Title', context: 'Input label' },
  topicContentLabel: { message: 'Question or Details', context: 'Input label' },
});

export default {
  name: 'DiscussionsPage',
  components: { CoachAppBarPage },
  setup() {
    const { classId } = useCoreCoach();
    const loading = ref(false);
    const threads = ref([]);
    const selectedThread = ref(null);
    const repliesLoading = ref(false);
    const replies = ref([]);
    const newReplyText = ref('');

    const showNewThreadModal = ref(false);
    const newThreadForm = reactive({
      title: '',
      content: '',
    });

    const {
      backToAssignments$,
      pageTitle$,
      pageSubtitle$,
      newTopicAction$,
      noThreadsTitle$,
      noThreadsDesc$,
      startFirstTopicAction$,
      pinnedLabel$,
      closedLabel$,
      repliesLabel$,
      postedByLabel$,
      pinAction$,
      unpinAction$,
      closeTopicAction$,
      reopenAction$,
      repliesSectionTitle$,
      noRepliesYet$,
      endorsedLabel$,
      endorseAnswerAction$,
      removeEndorsementAction$,
      replyPlaceholder$,
      postReplyAction$,
      threadClosedNotice$,
      newTopicModalTitle$,
      createTopicAction$,
      cancelAction$,
      topicTitleLabel$,
      topicContentLabel$,
    } = strings;

    async function loadThreads() {
      loading.value = true;
      try {
        const data = await DiscussionThreadResource.fetchCollection({
          getParams: { collection: classId.value },
          force: true,
        });
        threads.value = data;
        if (data.length > 0 && !selectedThread.value) {
          selectThread(data[0]);
        }
      } catch (err) {
        console.error('Failed to load threads', err);
      } finally {
        loading.value = false;
      }
    }

    onMounted(() => {
      loadThreads();
    });

    async function selectThread(thread) {
      selectedThread.value = thread;
      repliesLoading.value = true;
      try {
        const reps = await DiscussionReplyResource.fetchCollection({
          getParams: { thread: thread.id },
          force: true,
        });
        replies.value = reps;
      } catch (err) {
        console.error('Failed to load replies', err);
      } finally {
        repliesLoading.value = false;
      }
    }

    function openNewThreadModal() {
      newThreadForm.title = '';
      newThreadForm.content = '';
      showNewThreadModal.value = true;
    }

    function closeNewThreadModal() {
      showNewThreadModal.value = false;
    }

    async function submitNewThread() {
      if (!newThreadForm.title.trim() || !newThreadForm.content.trim()) return;
      try {
        const newObj = await DiscussionThreadResource.createModel({
          collection: classId.value,
          title: newThreadForm.title.trim(),
          content: newThreadForm.content.trim(),
        }).save();
        closeNewThreadModal();
        await loadThreads();
        selectThread(newObj);
      } catch (err) {
        console.error('Failed to create thread', err);
      }
    }

    async function togglePinThread(thread) {
      try {
        const res = await DiscussionThreadResource.togglePin(thread.id);
        thread.is_pinned = res.data.is_pinned;
        loadThreads();
      } catch (err) {
        console.error('Failed to toggle pin', err);
      }
    }

    async function toggleCloseThread(thread) {
      try {
        const res = await DiscussionThreadResource.toggleClose(thread.id);
        thread.is_closed = res.data.is_closed;
      } catch (err) {
        console.error('Failed to toggle close', err);
      }
    }

    async function toggleEndorseReply(reply) {
      try {
        const res = await DiscussionReplyResource.toggleEndorse(reply.id);
        reply.is_endorsed = res.data.is_endorsed;
      } catch (err) {
        console.error('Failed to endorse reply', err);
      }
    }

    async function submitReply() {
      if (!newReplyText.value.trim() || !selectedThread.value) return;
      try {
        const rep = await DiscussionReplyResource.createModel({
          thread: selectedThread.value.id,
          content: newReplyText.value.trim(),
        }).save();
        replies.value.push(rep);
        newReplyText.value = '';
        selectedThread.value.reply_count = (selectedThread.value.reply_count || 0) + 1;
      } catch (err) {
        console.error('Failed to post reply', err);
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
      threads,
      selectedThread,
      repliesLoading,
      replies,
      newReplyText,
      showNewThreadModal,
      newThreadForm,
      selectThread,
      openNewThreadModal,
      closeNewThreadModal,
      submitNewThread,
      togglePinThread,
      toggleCloseThread,
      toggleEndorseReply,
      submitReply,
      formatDate,
      backToAssignments$,
      pageTitle$,
      pageSubtitle$,
      newTopicAction$,
      noThreadsTitle$,
      noThreadsDesc$,
      startFirstTopicAction$,
      pinnedLabel$,
      closedLabel$,
      repliesLabel$,
      postedByLabel$,
      pinAction$,
      unpinAction$,
      closeTopicAction$,
      reopenAction$,
      repliesSectionTitle$,
      noRepliesYet$,
      endorsedLabel$,
      endorseAnswerAction$,
      removeEndorsementAction$,
      replyPlaceholder$,
      postReplyAction$,
      threadClosedNotice$,
      newTopicModalTitle$,
      createTopicAction$,
      cancelAction$,
      topicTitleLabel$,
      topicContentLabel$,
    };
  },
};
</script>

<style lang="scss" scoped>
.discussions-container {
  padding: 24px;
  max-width: 1300px;
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
  margin-bottom: 24px;
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

.empty-state {
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

.forum-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.thread-list-pane {
  width: 380px;
  min-width: 320px;
  border-radius: 10px;
  overflow: hidden;
  max-height: 80vh;
  overflow-y: auto;
}

.thread-tab-item {
  padding: 16px;
  cursor: pointer;
  transition: background-color 0.15s ease;

  &:hover {
    background-color: rgba(0, 0, 0, 0.03);
  }

  &.is-selected {
    background-color: rgba(0, 0, 0, 0.06);
    border-left: 4px solid #2563eb;
  }
}

.thread-badges,
.detail-badges {
  display: flex;
  gap: 6px;
  margin-bottom: 4px;
}

.badge-pinned {
  font-size: 11px;
  font-weight: 700;
  background-color: #fef3c7;
  color: #92400e;
  padding: 2px 6px;
  border-radius: 4px;
}

.badge-closed {
  font-size: 11px;
  font-weight: 700;
  background-color: #f3f4f6;
  color: #6b7280;
  padding: 2px 6px;
  border-radius: 4px;
}

.thread-item-title {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.3;
}

.thread-item-meta {
  font-size: 12px;
  display: flex;
  gap: 6px;
}

.thread-detail-pane {
  flex: 1;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.detail-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
}

.detail-title {
  margin: 4px 0;
  font-size: 22px;
  font-weight: 700;
}

.detail-meta {
  font-size: 13px;
}

.coach-controls {
  display: flex;
  gap: 8px;
}

.detail-content {
  padding: 20px;
}

.post-text {
  font-size: 15px;
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
}

.replies-section {
  padding: 0 20px 20px 20px;
}

.replies-header {
  font-size: 17px;
  font-weight: 700;
  margin: 16px 0 12px 0;
}

.no-replies {
  padding: 20px 0;
  text-align: center;
}

.replies-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.reply-card {
  padding: 14px 16px;
  border-radius: 8px;
}

.reply-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.reply-author {
  font-size: 14px;
}

.reply-date {
  font-size: 12px;
}

.endorsed-badge {
  font-size: 11px;
  font-weight: 700;
  color: #166534;
  background-color: #bbf7d0;
  padding: 2px 8px;
  border-radius: 9999px;
  margin-left: 8px;
}

.reply-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
  white-space: pre-wrap;
}

.post-reply-box {
  padding-top: 16px;
}

.reply-btn-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.closed-notice {
  padding: 16px;
  text-align: center;
  border-radius: 8px;
  font-size: 14px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
