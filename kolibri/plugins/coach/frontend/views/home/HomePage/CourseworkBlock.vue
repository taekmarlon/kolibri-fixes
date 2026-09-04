<template>
  <Block
    :allLinkText="viewAllAction$()"
    :allLinkRoute="classRoute(PageNames.COURSEWORK_ASSIGNMENTS)"
    :showAllLink="assignments.length > 0"
  >
    <template #title>
      {{ blockTitle$() }}
    </template>

    <div class="block-actions">
      <KRouterLink
        :text="newAssignmentAction$()"
        :primary="true"
        appearance="raised-button"
        :to="classRoute(PageNames.COURSEWORK_ASSIGNMENTS)"
      />
      <KRouterLink
        :text="gradebookAction$()"
        appearance="flat-button"
        icon="reports"
        :to="classRoute(PageNames.COURSEWORK_GRADEBOOK)"
      />
      <KRouterLink
        :text="discussionsAction$()"
        appearance="flat-button"
        icon="group"
        :to="classRoute(PageNames.COURSEWORK_DISCUSSIONS)"
      />
    </div>

    <KCircularLoader v-if="loading" />

    <div v-else-if="assignments.length === 0" class="empty-text">
      <p :style="{ color: $themeTokens.annotation }">
        {{ noAssignmentsMessage$() }}
      </p>
    </div>

    <div v-else class="items-list">
      <BlockItem
        v-for="assignment in recentAssignments"
        :key="assignment.id"
      >
        <div class="item-content">
          <div class="item-title" :style="{ color: $themeTokens.text }">
            {{ assignment.title }}
          </div>
          <div class="item-meta" :style="{ color: $themeTokens.annotation }">
            <span v-if="assignment.due_date">
              📅 {{ formatDate(assignment.due_date) }}
            </span>
            <span>
              📥 {{ assignment.submissions_count || 0 }} {{ submissionsLabel$() }}
            </span>
            <span v-if="(assignment.submissions_count || 0) > (assignment.graded_count || 0)" class="needs-grading">
              ⚠️ {{ (assignment.submissions_count || 0) - (assignment.graded_count || 0) }} {{ needsGradingLabel$() }}
            </span>
          </div>
        </div>
      </BlockItem>
    </div>
  </Block>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { createTranslator } from 'kolibri/utils/i18n';
import AssignmentResource from 'kolibri-common/apiResources/AssignmentResource';
import useCoreCoach from '../../../composables/useCoreCoach';
import { PageNames } from '../../../constants';
import Block from './Block.vue';
import BlockItem from './BlockItem.vue';

const strings = createTranslator('CoachCourseworkBlockStrings', {
  blockTitle: { message: 'Assignments & Homework', context: 'Block header' },
  viewAllAction: { message: 'View all assignments', context: 'All link' },
  newAssignmentAction: { message: 'New Assignment', context: 'Button' },
  gradebookAction: { message: 'Gradebook', context: 'Button' },
  discussionsAction: { message: 'Discussions', context: 'Button' },
  noAssignmentsMessage: { message: 'No homework or assignments created yet. Create one to collect student submissions.', context: 'Empty state' },
  submissionsLabel: { message: 'submissions', context: 'Count' },
  needsGradingLabel: { message: 'awaiting review', context: 'Pending badge' },
});

export default {
  name: 'CourseworkBlock',
  components: {
    Block,
    BlockItem,
  },
  setup() {
    const { classId } = useCoreCoach();
    const loading = ref(false);
    const assignments = ref([]);

    const {
      blockTitle$,
      viewAllAction$,
      newAssignmentAction$,
      gradebookAction$,
      discussionsAction$,
      noAssignmentsMessage$,
      submissionsLabel$,
      needsGradingLabel$,
    } = strings;

    async function loadData() {
      loading.value = true;
      try {
        const data = await AssignmentResource.fetchCollection({
          getParams: { collection: classId.value },
          force: true,
        });
        assignments.value = data;
      } catch (err) {
        console.error('Failed to load coursework block data', err);
      } finally {
        loading.value = false;
      }
    }

    onMounted(() => {
      loadData();
    });

    const recentAssignments = computed(() => {
      return assignments.value.slice(0, 3);
    });

    function classRoute(name) {
      return {
        name,
        params: { classId: classId.value },
      };
    }

    function formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
      });
    }

    return {
      classId,
      PageNames,
      loading,
      assignments,
      recentAssignments,
      classRoute,
      formatDate,
      blockTitle$,
      viewAllAction$,
      newAssignmentAction$,
      gradebookAction$,
      discussionsAction$,
      noAssignmentsMessage$,
      submissionsLabel$,
      needsGradingLabel$,
    };
  },
};
</script>

<style lang="scss" scoped>
.block-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.empty-text {
  padding: 12px 0;
  font-size: 14px;
}

.items-list {
  display: flex;
  flex-direction: column;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-title {
  font-size: 14px;
  font-weight: 600;
}

.item-meta {
  font-size: 12px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.needs-grading {
  color: #b45309;
  font-weight: 600;
}
</style>
