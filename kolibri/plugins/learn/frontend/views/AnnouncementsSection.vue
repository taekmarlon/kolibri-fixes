<template>
  <div
    v-if="announcements.length > 0 || loading"
    class="announcements-section"
    :style="{ borderTop: `2px solid ${$themeTokens.fineLine}`, paddingTop: '16px', marginTop: '24px' }"
  >
    <!-- Section header -->
    <div class="section-header">
      <h2 class="section-title" :style="{ color: $themeTokens.text }">
        📢 {{ sectionTitle$() }}
      </h2>
    </div>

    <!-- Loading -->
    <KCircularLoader v-if="loading" />

    <!-- Announcement cards -->
    <div v-else class="ann-list">
      <div
        v-for="ann in announcements"
        :key="ann.id"
        class="ann-card"
        :style="{
          background: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
          borderLeft: `4px solid ${typeColor(ann.announcement_type)}`
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
  import { ref, onMounted } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import AnnouncementResource from 'kolibri-common/apiResources/AnnouncementResource';

  const strings = createTranslator('AnnouncementsSectionStrings', {
    sectionTitle: { message: 'Announcements & School Notices', context: 'Learner announcements section title' },
    eventOnLabel: { message: 'Event on', context: 'Event date prefix for learner' },
    viewLinkBtn: { message: 'View Link', context: 'Link button label' },
    schoolAdminLabel: { message: 'School', context: 'Fallback author label for learner view' },
  });

  export default {
    name: 'AnnouncementsSection',
    props: {
      classId: {
        type: String,
        required: false,
        default: null,
      },
    },
    setup(props) {
      const announcements = ref([]);
      const loading = ref(true);

      const { sectionTitle$, eventOnLabel$, viewLinkBtn$, schoolAdminLabel$ } = strings;

      function typeColor(type) {
        const colors = { general: '#1976d2', event: '#388e3c', deped_memo: '#7b1fa2', urgent: '#d32f2f' };
        return colors[type] || '#607d8b';
      }

      function typeEmoji(type) {
        return { general: '📢', event: '📅', deped_memo: '📋', urgent: '🚨' }[type] || '📢';
      }

      function typeLabel(type) {
        return { general: 'Notice', event: 'Event', deped_memo: 'DepEd', urgent: '⚠️ Urgent' }[type] || type;
      }

      function formatDate(dt) {
        if (!dt) return '';
        return new Date(dt).toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' });
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
        loading,
        typeColor,
        typeEmoji,
        typeLabel,
        formatDate,
        openLink,
        sectionTitle$,
        eventOnLabel$,
        viewLinkBtn$,
        schoolAdminLabel$,
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
    font-size: 1rem;
    font-weight: 600;
    margin: 0;
  }

  .ann-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .ann-card {
    border-radius: 6px;
    padding: 10px 14px;
  }

  .ann-top {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;
    flex-wrap: wrap;
  }

  .type-badge {
    padding: 2px 7px;
    border-radius: 10px;
    font-size: 0.73rem;
    font-weight: 600;
  }

  .pin-label {
    font-size: 0.8rem;
  }

  .ann-date {
    margin-left: auto;
    font-size: 0.73rem;
  }

  .ann-title {
    margin: 0 0 3px;
    font-size: 0.9rem;
    font-weight: 600;
  }

  .ann-body {
    margin: 0 0 5px;
    font-size: 0.83rem;
    line-height: 1.45;
    white-space: pre-wrap;
  }

  .ann-event {
    margin: 0 0 5px;
    font-size: 0.8rem;
    font-weight: 500;
  }

  .ann-author {
    font-size: 0.75rem;
    font-style: italic;
    margin: 6px 0 0;
  }

</style>
