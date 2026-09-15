<template>
  <KPageContainer
    class="page-container announcements-block"
    :style="{ border: `1px solid ${$themeTokens.fineLine}` }"
  >
    <!-- Header -->
    <div class="block-header">
      <div class="header-left">
        <span class="block-badge">
          📢 {{ blockTitle$() }}
        </span>
      </div>
      <div class="header-right">
        <KButton
          :text="newAnnouncementBtn$()"
          :primary="true"
          appearance="raised-button"
          icon="plus"
          size="small"
          @click="openCreateModal"
        />
        <SectionToggleButton
          :isExpanded="isExpanded"
          @click="toggleExpand"
        />
      </div>
    </div>

    <transition name="section-collapse">
      <div v-show="isExpanded" class="block-body">
        <h2 class="block-title" :style="{ color: $themeTokens.text }">
          {{ blockSubtitle$() }}
        </h2>

    <!-- Filter tabs -->
    <div class="filter-row">
      <button
        v-for="f in filters"
        :key="f.value"
        class="filter-pill"
        :class="{ active: activeFilter === f.value }"
        :style="activeFilter === f.value
          ? { background: $themeTokens.primary, color: '#fff', border: 'none' }
          : { background: $themeTokens.surface, color: $themeTokens.text, border: `1px solid ${$themeTokens.fineLine}` }"
        @click="activeFilter = f.value"
      >
        {{ f.emoji }} {{ f.label }} ({{ filterCount(f.value) }})
      </button>
    </div>

    <!-- Loading -->
    <KCircularLoader v-if="loading" class="loader" />

    <!-- Empty state -->
    <div
      v-else-if="filteredAnnouncements.length === 0"
      class="empty-state"
      :style="{ color: $themeTokens.annotation }"
    >
      <span style="font-size:2rem">📢</span>
      <p>{{ noAnnouncementsMsg$() }}</p>
    </div>

    <!-- Announcement cards -->
    <div v-else class="announcements-list">
      <div
        v-for="ann in filteredAnnouncements"
        :key="ann.id"
        class="ann-card"
        :style="{ background: $themeTokens.surface, border: `1px solid ${$themeTokens.fineLine}`, borderLeft: `4px solid ${typeColor(ann.announcement_type)}` }"
      >
        <!-- Card header -->
        <div class="ann-card-top">
          <span
            class="type-badge"
            :style="{ background: typeColor(ann.announcement_type), color: '#fff' }"
          >
            {{ typeEmoji(ann.announcement_type) }} {{ typeLabel(ann.announcement_type) }}
          </span>
          <span v-if="ann.is_pinned" class="pin-badge" :style="{ color: $themeTokens.annotation }">
            📌 {{ pinnedLabel$() }}
          </span>
          <span class="ann-date" :style="{ color: $themeTokens.annotation }">
            {{ formatDate(ann.date_created) }}
          </span>
        </div>

        <!-- Title & body -->
        <h3 class="ann-title" :style="{ color: $themeTokens.text }">
          {{ ann.title }}
        </h3>
        <p class="ann-body" :style="{ color: $themeTokens.annotation }">
          {{ truncate(ann.body, 120) }}
        </p>

        <!-- Event date -->
        <p v-if="ann.event_date" class="ann-event-date" :style="{ color: $themeTokens.primary }">
          📅 {{ eventOnLabel$() }}: {{ formatDate(ann.event_date) }}
        </p>

        <!-- Card footer -->
        <div class="ann-card-footer">
          <span class="ann-author" :style="{ color: $themeTokens.annotation }">
            — {{ ann.created_by_name || unknownAuthorLabel$() }}
          </span>
          <div class="ann-actions">
            <KButton
              v-if="ann.link_url"
              :text="viewLinkBtn$()"
              appearance="flat-button"
              icon="externalLink"
              size="small"
              @click="openLink(ann.link_url)"
            />
            <KButton
              :text="editBtn$()"
              appearance="flat-button"
              icon="edit"
              size="small"
              @click="openEditModal(ann)"
            />
            <KButton
              :text="deleteBtn$()"
              appearance="flat-button"
              icon="delete"
              size="small"
              :style="{ color: $themeTokens.error }"
              @click="confirmDelete(ann)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</transition>

    <!-- Create/Edit Modal -->
    <AnnouncementFormModal
      v-if="showFormModal"
      :announcement="editingAnnouncement"
      :class-id="classId"
      :facility-id="facilityId"
      @close="showFormModal = false"
      @saved="onAnnouncementSaved"
    />

    <!-- Delete confirm modal -->
    <KModal
      v-if="showDeleteModal"
      :title="deleteConfirmTitle$()"
      :submitText="deleteConfirmBtn$()"
      :cancelText="cancelBtn$()"
      @submit="doDelete"
      @cancel="showDeleteModal = false"
    >
      <p>{{ deleteConfirmMsg$() }}</p>
    </KModal>
  </KPageContainer>
</template>

<script>
  import { ref, computed, onMounted } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import AnnouncementResource from 'kolibri-common/apiResources/AnnouncementResource';
  import SectionToggleButton from 'kolibri-common/components/SectionToggleButton';
  import useCollapsible from 'kolibri-common/composables/useCollapsible';
  import useCoreCoach from '../../../composables/useCoreCoach';
  import AnnouncementFormModal from './AnnouncementFormModal';

  const strings = createTranslator('AnnouncementsBlockStrings', {
    blockTitle: { message: 'School Announcements & Events', context: 'Announcements block header' },
    blockSubtitle: { message: 'Bulletins, Events & DepEd Notices', context: 'Announcements block subtitle' },
    newAnnouncementBtn: { message: '+ New Announcement', context: 'Button to create announcement' },
    allFilter: { message: 'All', context: 'Filter pill: all announcements' },
    pinnedFilter: { message: 'Pinned', context: 'Filter pill: pinned' },
    eventsFilter: { message: 'Events', context: 'Filter pill: events' },
    depedFilter: { message: 'DepEd Memos', context: 'Filter pill: DepEd' },
    urgentFilter: { message: 'Urgent', context: 'Filter pill: urgent' },
    noAnnouncementsMsg: { message: 'No announcements yet. Click "+ New Announcement" to post one.', context: 'Empty state message' },
    pinnedLabel: { message: 'Pinned', context: 'Pinned badge label' },
    eventOnLabel: { message: 'Event on', context: 'Event date prefix' },
    viewLinkBtn: { message: 'View Link', context: 'Button to open announcement URL' },
    editBtn: { message: 'Edit', context: 'Edit button' },
    deleteBtn: { message: 'Delete', context: 'Delete button' },
    unknownAuthorLabel: { message: 'School Admin', context: 'Fallback author label' },
    deleteConfirmTitle: { message: 'Delete Announcement', context: 'Delete confirmation modal title' },
    deleteConfirmMsg: { message: 'Are you sure you want to delete this announcement? This cannot be undone.', context: 'Delete confirmation message' },
    deleteConfirmBtn: { message: 'Delete', context: 'Confirm delete button' },
    cancelBtn: { message: 'Cancel', context: 'Cancel button' },
  });

  export default {
    name: 'AnnouncementsBlock',
    components: {
      AnnouncementFormModal,
      SectionToggleButton,
    },
    setup() {
      const { isExpanded, toggleExpand } = useCollapsible('coach_announcements', true);
      const { classId } = useCoreCoach();
      const facilityId = ref(null);
      const announcements = ref([]);
      const loading = ref(true);
      const activeFilter = ref('all');
      const showFormModal = ref(false);
      const showDeleteModal = ref(false);
      const editingAnnouncement = ref(null);
      const deletingAnnouncement = ref(null);

      const {
        blockTitle$,
        blockSubtitle$,
        newAnnouncementBtn$,
        allFilter$,
        pinnedFilter$,
        eventsFilter$,
        depedFilter$,
        urgentFilter$,
        noAnnouncementsMsg$,
        pinnedLabel$,
        eventOnLabel$,
        viewLinkBtn$,
        editBtn$,
        deleteBtn$,
        unknownAuthorLabel$,
        deleteConfirmTitle$,
        deleteConfirmMsg$,
        deleteConfirmBtn$,
        cancelBtn$,
      } = strings;

      const filters = [
        { value: 'all', label: 'All', emoji: '📋' },
        { value: 'pinned', label: 'Pinned', emoji: '📌' },
        { value: 'event', label: 'Events', emoji: '📅' },
        { value: 'deped_memo', label: 'DepEd Memos', emoji: '📋' },
        { value: 'urgent', label: 'Urgent', emoji: '🚨' },
      ];

      const filteredAnnouncements = computed(() => {
        if (activeFilter.value === 'all') return announcements.value;
        if (activeFilter.value === 'pinned') return announcements.value.filter(a => a.is_pinned);
        return announcements.value.filter(a => a.announcement_type === activeFilter.value);
      });

      function filterCount(filterValue) {
        if (filterValue === 'all') return announcements.value.length;
        if (filterValue === 'pinned') return announcements.value.filter(a => a.is_pinned).length;
        return announcements.value.filter(a => a.announcement_type === filterValue).length;
      }

      function typeColor(type) {
        const colors = {
          general: '#1976d2',
          event: '#388e3c',
          deped_memo: '#7b1fa2',
          urgent: '#d32f2f',
        };
        return colors[type] || '#607d8b';
      }

      function typeEmoji(type) {
        const emojis = { general: '📢', event: '📅', deped_memo: '📋', urgent: '🚨' };
        return emojis[type] || '📢';
      }

      function typeLabel(type) {
        const labels = {
          general: 'General',
          event: 'Event',
          deped_memo: 'DepEd Memo',
          urgent: 'Urgent',
        };
        return labels[type] || type;
      }

      function truncate(text, maxLen) {
        if (!text) return '';
        return text.length > maxLen ? text.slice(0, maxLen) + '…' : text;
      }

      function formatDate(dt) {
        if (!dt) return '';
        return new Date(dt).toLocaleDateString('en-PH', {
          year: 'numeric', month: 'short', day: 'numeric',
        });
      }

      function openLink(url) {
        window.open(url, '_blank', 'noopener');
      }

      function openCreateModal() {
        editingAnnouncement.value = null;
        showFormModal.value = true;
      }

      function openEditModal(ann) {
        editingAnnouncement.value = ann;
        showFormModal.value = true;
      }

      function confirmDelete(ann) {
        deletingAnnouncement.value = ann;
        showDeleteModal.value = true;
      }

      function doDelete() {
        if (!deletingAnnouncement.value) return;
        AnnouncementResource.deleteModel({ id: deletingAnnouncement.value.id })
          .then(() => {
            announcements.value = announcements.value.filter(
              a => a.id !== deletingAnnouncement.value.id
            );
            showDeleteModal.value = false;
            deletingAnnouncement.value = null;
          });
      }

      async function fetchAnnouncements() {
        loading.value = true;
        try {
          const params = {};
          if (classId.value) params.collection = classId.value;
          const resp = await AnnouncementResource.fetchCollection({ getParams: params });
          announcements.value = resp || [];
        } catch (e) {
          announcements.value = [];
        } finally {
          loading.value = false;
        }
      }

      function onAnnouncementSaved(saved) {
        const idx = announcements.value.findIndex(a => a.id === saved.id);
        if (idx >= 0) {
          announcements.value.splice(idx, 1, saved);
        } else {
          announcements.value.unshift(saved);
        }
        showFormModal.value = false;
      }

      onMounted(fetchAnnouncements);

      return {
        classId,
        facilityId,
        announcements,
        loading,
        activeFilter,
        filters,
        filteredAnnouncements,
        filterCount,
        showFormModal,
        showDeleteModal,
        editingAnnouncement,
        typeColor,
        typeEmoji,
        typeLabel,
        truncate,
        formatDate,
        openLink,
        openCreateModal,
        openEditModal,
        confirmDelete,
        doDelete,
        onAnnouncementSaved,
        isExpanded,
        toggleExpand,
        blockTitle$,
        blockSubtitle$,
        newAnnouncementBtn$,
        allFilter$,
        pinnedFilter$,
        eventsFilter$,
        depedFilter$,
        urgentFilter$,
        noAnnouncementsMsg$,
        pinnedLabel$,
        eventOnLabel$,
        viewLinkBtn$,
        editBtn$,
        deleteBtn$,
        unknownAuthorLabel$,
        deleteConfirmTitle$,
        deleteConfirmMsg$,
        deleteConfirmBtn$,
        cancelBtn$,
      };
    },
  };
</script>

<style lang="scss" scoped>

  .announcements-block {
    padding: 16px;
  }

  .block-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
  }

  .block-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 10px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #1565c0;
    background: #e3f2fd;
    border-radius: 12px;
  }

  .block-title {
    margin: 0 0 12px;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .filter-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
  }

  .filter-pill {
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 0.82rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;

    &:hover {
      opacity: 0.85;
    }
  }

  .loader {
    margin: 24px auto;
    display: block;
  }

  .empty-state {
    text-align: center;
    padding: 32px 16px;
    font-size: 0.95rem;
  }

  .announcements-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .ann-card {
    border-radius: 8px;
    padding: 12px 16px;
    transition: box-shadow 0.15s;

    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
  }

  .ann-card-top {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
    flex-wrap: wrap;
  }

  .type-badge {
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .pin-badge {
    font-size: 0.75rem;
    font-weight: 500;
  }

  .ann-date {
    margin-left: auto;
    font-size: 0.75rem;
  }

  .ann-title {
    margin: 0 0 4px;
    font-size: 0.95rem;
    font-weight: 600;
  }

  .ann-body {
    margin: 0 0 6px;
    font-size: 0.85rem;
    line-height: 1.4;
  }

  .ann-event-date {
    margin: 0 0 6px;
    font-size: 0.82rem;
    font-weight: 500;
  }

  .ann-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 8px;
  }

  .ann-author {
    font-size: 0.78rem;
    font-style: italic;
  }

  .ann-actions {
    display: flex;
    gap: 4px;
  }

  .header-right {
    display: inline-flex;
    align-items: center;
    gap: 8px;
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
