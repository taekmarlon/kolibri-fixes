<template>
  <FacilityAppBarPage :loading="pageLoading">
    <KPageContainer>
      <!-- Multi-facility switcher -->
      <p v-if="userIsMultiFacilityAdmin">
        <KRouterLink
          :to="{
            name: 'ALL_FACILITIES_PAGE',
            params: { subtopicName: 'FacilityAnnouncementsPage' },
          }"
          icon="back"
          :text="coreString('changeLearningFacility')"
        />
      </p>

      <!-- Header -->
      <KGrid class="page-header">
        <KGridItem
          :layout8="{ span: 6 }"
          :layout12="{ span: 9 }"
        >
          <h1 :style="{ color: $themeTokens.text }">
            📢 {{ pageTitle$() }}
          </h1>
          <p :style="{ color: $themeTokens.annotation }">
            {{ pageSubtitle$() }}
          </p>
        </KGridItem>
        <KGridItem
          :layout="{ alignment: 'right' }"
          :layout8="{ span: 2 }"
          :layout12="{ span: 3 }"
        >
          <KButton
            :text="newAnnouncementBtn$()"
            :primary="true"
            appearance="raised-button"
            icon="plus"
            class="add-btn"
            @click="openCreateModal"
          />
        </KGridItem>
      </KGrid>

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

      <!-- Loading state -->
      <KCircularLoader v-if="loading" class="loader" />

      <!-- Empty state -->
      <div
        v-else-if="filteredAnnouncements.length === 0"
        class="empty-state"
        :style="{ color: $themeTokens.annotation }"
      >
        <span style="font-size: 2.5rem">📢</span>
        <p>{{ noAnnouncementsMsg$() }}</p>
      </div>

      <!-- Announcements cards -->
      <div v-else class="ann-list">
        <div
          v-for="ann in filteredAnnouncements"
          :key="ann.id"
          class="ann-card"
          :style="{
            background: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
            borderLeft: `4px solid ${typeColor(ann.announcement_type)}`,
          }"
        >
          <!-- Card top -->
          <div class="ann-card-top">
            <span
              class="type-badge"
              :style="{ background: typeColor(ann.announcement_type), color: '#fff' }"
            >
              {{ typeEmoji(ann.announcement_type) }} {{ typeLabel(ann.announcement_type) }}
            </span>
            <span
              class="scope-badge"
              :style="{ background: $themeTokens.fineLine, color: $themeTokens.text }"
            >
              {{ ann.scope === 'facility' ? '🏛️ School-wide' : '🏫 Class' }}
            </span>
            <span v-if="ann.is_pinned" class="pin-badge" :style="{ color: $themeTokens.annotation }">
              📌 {{ pinnedLabel$() }}
            </span>
            <span class="ann-date" :style="{ color: $themeTokens.annotation }">
              {{ formatDate(ann.date_created) }}
            </span>
          </div>

          <!-- Title & body -->
          <h2 class="ann-title" :style="{ color: $themeTokens.text }">
            {{ ann.title }}
          </h2>
          <p class="ann-body" :style="{ color: $themeTokens.annotation }">
            {{ ann.body }}
          </p>

          <!-- Event date -->
          <p v-if="ann.event_date" class="ann-event-date" :style="{ color: $themeTokens.primary }">
            📅 {{ eventOnLabel$() }}: {{ formatDate(ann.event_date) }}
          </p>

          <!-- Card footer -->
          <div class="ann-card-footer">
            <span class="ann-author" :style="{ color: $themeTokens.annotation }">
              — {{ ann.created_by_name || schoolAdminLabel$() }}
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
                @click="openDeleteModal(ann)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Create / Edit Form Modal -->
      <AnnouncementFormModal
        v-if="showFormModal"
        :announcement="editingAnnouncement"
        :facilityId="facilityId"
        @saved="onAnnouncementSaved"
        @close="showFormModal = false"
      />

      <!-- Delete Confirmation Modal -->
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
  </FacilityAppBarPage>
</template>

<script>
  import { ref, computed, onMounted } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import AnnouncementResource from 'kolibri-common/apiResources/AnnouncementResource';
  import useFacility from 'kolibri-common/composables/useFacility';
  import useFacilities from 'kolibri-common/composables/useFacilities';
  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';
  import AnnouncementFormModal from 'kolibri-common/components/AnnouncementFormModal';
  import FacilityAppBarPage from './FacilityAppBarPage';

  const strings = createTranslator('FacilityAnnouncementsPageStrings', {
    pageTitle: {
      message: 'School Announcements & Bulletins',
      context: 'Page title for facility announcements',
    },
    pageSubtitle: {
      message: 'Manage school-wide notices, DepEd memorandums, urgent bulletins, and school events.',
      context: 'Page subtitle for facility announcements',
    },
    newAnnouncementBtn: {
      message: '+ New Announcement',
      context: 'Button to create a new announcement',
    },
    noAnnouncementsMsg: {
      message: 'No school announcements yet. Click "+ New Announcement" to post a bulletin or notice.',
      context: 'Empty state message',
    },
    pinnedLabel: { message: 'Pinned', context: 'Pinned badge label' },
    eventOnLabel: { message: 'Event on', context: 'Event date label' },
    viewLinkBtn: { message: 'View Link', context: 'Link button label' },
    editBtn: { message: 'Edit', context: 'Edit button label' },
    deleteBtn: { message: 'Delete', context: 'Delete button label' },
    schoolAdminLabel: { message: 'School Administrator', context: 'Fallback author label' },
    deleteConfirmTitle: {
      message: 'Delete Announcement',
      context: 'Delete confirmation title',
    },
    deleteConfirmMsg: {
      message: 'Are you sure you want to delete this announcement? This action cannot be undone.',
      context: 'Delete confirmation message',
    },
    deleteConfirmBtn: { message: 'Delete', context: 'Delete confirmation button' },
    cancelBtn: { message: 'Cancel', context: 'Cancel button' },
  });

  export default {
    name: 'FacilityAnnouncementsPage',
    components: {
      FacilityAppBarPage,
      AnnouncementFormModal,
    },
    mixins: [commonCoreStrings],
    setup() {
      const { facilityId } = useFacility();
      const { userIsMultiFacilityAdmin } = useFacilities();

      const announcements = ref([]);
      const loading = ref(true);
      const activeFilter = ref('all');
      const showFormModal = ref(false);
      const showDeleteModal = ref(false);
      const editingAnnouncement = ref(null);
      const deletingAnnouncement = ref(null);

      const {
        pageTitle$,
        pageSubtitle$,
        newAnnouncementBtn$,
        noAnnouncementsMsg$,
        pinnedLabel$,
        eventOnLabel$,
        viewLinkBtn$,
        editBtn$,
        deleteBtn$,
        schoolAdminLabel$,
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
        return { general: '📢', event: '📅', deped_memo: '📋', urgent: '🚨' }[type] || '📢';
      }

      function typeLabel(type) {
        return (
          {
            general: 'Notice',
            event: 'Event',
            deped_memo: 'DepEd Memo',
            urgent: '⚠️ Urgent',
          }[type] || type
        );
      }

      function formatDate(dt) {
        if (!dt) return '';
        return new Date(dt).toLocaleDateString('en-PH', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
        });
      }

      function openLink(url) {
        window.open(url, '_blank', 'noopener');
      }

      async function fetchAnnouncements() {
        loading.value = true;
        try {
          const params = {};
          if (facilityId.value) {
            params.collection = facilityId.value;
          }
          const data = await AnnouncementResource.fetchCollection({
            getParams: params,
            force: true,
          });
          announcements.value = data || [];
        } catch (e) {
          announcements.value = [];
        } finally {
          loading.value = false;
        }
      }

      function openCreateModal() {
        editingAnnouncement.value = null;
        showFormModal.value = true;
      }

      function openEditModal(ann) {
        editingAnnouncement.value = ann;
        showFormModal.value = true;
      }

      function openDeleteModal(ann) {
        deletingAnnouncement.value = ann;
        showDeleteModal.value = true;
      }

      async function doDelete() {
        if (!deletingAnnouncement.value) return;
        try {
          await AnnouncementResource.deleteModel({ id: deletingAnnouncement.value.id });
          showDeleteModal.value = false;
          deletingAnnouncement.value = null;
          fetchAnnouncements();
        } catch (e) {
          showDeleteModal.value = false;
        }
      }

      function onAnnouncementSaved() {
        showFormModal.value = false;
        fetchAnnouncements();
      }

      onMounted(fetchAnnouncements);

      return {
        facilityId,
        userIsMultiFacilityAdmin,
        pageLoading,
        announcements,
        filteredAnnouncements,
        loading,
        activeFilter,
        filters,
        filterCount,
        showFormModal,
        showDeleteModal,
        editingAnnouncement,
        typeColor,
        typeEmoji,
        typeLabel,
        formatDate,
        openLink,
        openCreateModal,
        openEditModal,
        openDeleteModal,
        doDelete,
        onAnnouncementSaved,
        pageTitle$,
        pageSubtitle$,
        newAnnouncementBtn$,
        noAnnouncementsMsg$,
        pinnedLabel$,
        eventOnLabel$,
        viewLinkBtn$,
        editBtn$,
        deleteBtn$,
        schoolAdminLabel$,
        deleteConfirmTitle$,
        deleteConfirmMsg$,
        deleteConfirmBtn$,
        cancelBtn$,
      };
    },
  };
</script>

<style lang="scss" scoped>

  .page-header {
    margin-bottom: 20px;
    align-items: center;
  }

  .add-btn {
    margin-top: 10px;
  }

  .filter-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
  }

  .filter-pill {
    padding: 6px 14px;
    border-radius: 16px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;

    &.active {
      font-weight: 600;
    }
  }

  .loader {
    margin: 40px auto;
  }

  .empty-state {
    text-align: center;
    padding: 48px 16px;
    font-size: 1rem;

    p {
      margin-top: 12px;
    }
  }

  .ann-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .ann-card {
    border-radius: 8px;
    padding: 16px 20px;
  }

  .ann-card-top {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
    flex-wrap: wrap;
  }

  .type-badge {
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.78rem;
    font-weight: 600;
  }

  .scope-badge {
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .pin-badge {
    font-size: 0.85rem;
    font-weight: 500;
  }

  .ann-date {
    margin-left: auto;
    font-size: 0.8rem;
  }

  .ann-title {
    margin: 0 0 6px;
    font-size: 1.15rem;
    font-weight: 600;
  }

  .ann-body {
    margin: 0 0 8px;
    font-size: 0.95rem;
    line-height: 1.55;
    white-space: pre-wrap;
  }

  .ann-event-date {
    margin: 0 0 8px;
    font-size: 0.9rem;
    font-weight: 600;
  }

  .ann-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 12px;
    padding-top: 8px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .ann-author {
    font-size: 0.82rem;
    font-style: italic;
  }

  .ann-actions {
    display: flex;
    gap: 8px;
  }

</style>
