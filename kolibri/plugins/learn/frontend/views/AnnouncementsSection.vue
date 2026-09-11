<template>
  <div
    v-if="standalone || announcements.length > 0 || loading"
    class="announcements-section"
    :class="{ 'standalone-section': standalone }"
    :style="standalone ? {} : { borderTop: `2px solid ${$themeTokens.fineLine}`, paddingTop: '16px', marginTop: '24px' }"
  >
    <!-- Section header -->
    <div class="section-header">
      <h2 class="section-title" :style="{ color: $themeTokens.text }">
        📢 {{ sectionTitle$() }}
      </h2>
    </div>

    <!-- Filter tabs (shown in standalone view) -->
    <div v-if="standalone" class="filter-row">
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
    <KCircularLoader v-if="loading" />

    <!-- Empty state -->
    <div
      v-else-if="filteredAnnouncements.length === 0"
      class="empty-state"
      :style="{ color: $themeTokens.annotation }"
    >
      <span style="font-size: 2rem">📢</span>
      <p>{{ noAnnouncementsMsg$() }}</p>
    </div>

    <!-- Announcement cards -->
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
        <div class="ann-top">
          <span
            class="type-badge"
            :style="{ background: typeColor(ann.announcement_type), color: '#fff' }"
          >
            {{ typeEmoji(ann.announcement_type) }} {{ typeLabel(ann.announcement_type) }}
          </span>
          <span v-if="ann.is_pinned" class="pin-label" :style="{ color: $themeTokens.annotation }">
            📌
          </span>
          <span class="ann-date" :style="{ color: $themeTokens.annotation }">
            {{ formatDate(ann.date_created) }}
          </span>
        </div>

        <h3 class="ann-title" :style="{ color: $themeTokens.text }">
          {{ ann.title }}
        </h3>
        <p class="ann-body" :style="{ color: $themeTokens.annotation }">
          {{ ann.body }}
        </p>

        <!-- Event date -->
        <p
          v-if="ann.event_date"
          class="ann-event"
          :style="{ color: $themeTokens.primary }"
        >
          📅 {{ eventOnLabel$() }}: {{ formatDate(ann.event_date) }}
        </p>

        <!-- Link -->
        <KButton
          v-if="ann.link_url"
          :text="viewLinkBtn$()"
          appearance="flat-button"
          icon="externalLink"
          size="small"
          @click="openLink(ann.link_url)"
        />

        <p class="ann-author" :style="{ color: $themeTokens.annotation }">
          — {{ ann.created_by_name || schoolAdminLabel$() }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import AnnouncementResource from 'kolibri-common/apiResources/AnnouncementResource';

  const strings = createTranslator('AnnouncementsSectionStrings', {
    sectionTitle: {
      message: 'Announcements & School Notices',
      context: 'Learner announcements section title',
    },
    eventOnLabel: { message: 'Event on', context: 'Event date prefix for learner' },
    viewLinkBtn: { message: 'View Link', context: 'Link button label' },
    schoolAdminLabel: { message: 'School', context: 'Fallback author label for learner view' },
    noAnnouncementsMsg: {
      message: 'No announcements posted at this time.',
      context: 'Empty state message when no announcements are available',
    },
  });

  export default {
    name: 'AnnouncementsSection',
    props: {
      classId: {
        type: String,
        required: false,
        default: null,
      },
      standalone: {
        type: Boolean,
        default: false,
      },
    },
    setup(props) {
      const announcements = ref([]);
      const loading = ref(true);
      const activeFilter = ref('all');

      const {
        sectionTitle$,
        eventOnLabel$,
        viewLinkBtn$,
        schoolAdminLabel$,
        noAnnouncementsMsg$,
      } = strings;

      const filters = [
        { value: 'all', label: 'All', emoji: '📋' },
        { value: 'pinned', label: 'Pinned', emoji: '📌' },
        { value: 'event', label: 'Events', emoji: '📅' },
        { value: 'deped_memo', label: 'DepEd Memos', emoji: '📋' },
        { value: 'urgent', label: 'Urgent', emoji: '🚨' },
      ];

      const filteredAnnouncements = computed(() => {
        if (!props.standalone || activeFilter.value === 'all') return announcements.value;
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
            deped_memo: 'DepEd',
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
          if (props.classId) {
            params.collection = props.classId;
          }
          const data = await AnnouncementResource.fetchCollection({
            getParams: params,
          });
          announcements.value = data || [];
        } catch (e) {
          announcements.value = [];
        } finally {
          loading.value = false;
        }
      }

      onMounted(fetchAnnouncements);

      return {
        announcements,
        filteredAnnouncements,
        loading,
        activeFilter,
        filters,
        filterCount,
        typeColor,
        typeEmoji,
        typeLabel,
        formatDate,
        openLink,
        sectionTitle$,
        eventOnLabel$,
        viewLinkBtn$,
        schoolAdminLabel$,
        noAnnouncementsMsg$,
      };
    },
  };
</script>

<style lang="scss" scoped>

  .section-header {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
  }

  .section-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0;
  }

  .filter-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
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

  .empty-state {
    text-align: center;
    padding: 36px 16px;
    font-size: 0.95rem;

    p {
      margin-top: 8px;
    }
  }

  .ann-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .ann-card {
    border-radius: 6px;
    padding: 12px 16px;
  }

  .ann-top {
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

  .pin-label {
    font-size: 0.85rem;
  }

  .ann-date {
    margin-left: auto;
    font-size: 0.75rem;
  }

  .ann-title {
    margin: 0 0 4px;
    font-size: 1rem;
    font-weight: 600;
  }

  .ann-body {
    margin: 0 0 6px;
    font-size: 0.88rem;
    line-height: 1.5;
    white-space: pre-wrap;
  }

  .ann-event {
    margin: 0 0 6px;
    font-size: 0.85rem;
    font-weight: 500;
  }

  .ann-author {
    font-size: 0.78rem;
    font-style: italic;
    margin: 8px 0 0;
  }

</style>
