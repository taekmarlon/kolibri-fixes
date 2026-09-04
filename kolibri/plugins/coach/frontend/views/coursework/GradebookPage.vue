<template>
  <CoachAppBarPage>
    <div class="gradebook-container">
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
            📊 {{ pageTitle$() }}
          </h1>
          <p class="page-subtitle" :style="{ color: $themeTokens.annotation }">
            {{ pageSubtitle$() }}
          </p>
        </div>
        <div class="header-actions">
          <KButton
            :text="exportCsvAction$()"
            :primary="true"
            appearance="raised-button"
            icon="download"
            :disabled="!gradebookData || !gradebookData.learners || gradebookData.learners.length === 0"
            @click="exportToCSV"
          />
        </div>
      </div>

      <!-- Loading State -->
      <KCircularLoader v-if="loading" />

      <!-- Empty State -->
      <div
        v-else-if="!gradebookData || !gradebookData.assignments || gradebookData.assignments.length === 0"
        class="empty-state"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px dashed ${$themeTokens.fineLine}`,
        }"
      >
        <span class="empty-icon">📈</span>
        <h2 :style="{ color: $themeTokens.text }">{{ noAssignmentsTitle$() }}</h2>
        <p :style="{ color: $themeTokens.annotation }">
          {{ noAssignmentsDesc$() }}
        </p>
        <KRouterLink
          :text="createAssignmentAction$()"
          :primary="true"
          appearance="raised-button"
          :to="{ name: PageNames.COURSEWORK_ASSIGNMENTS, params: { classId } }"
        />
      </div>

      <!-- Gradebook Table Grid -->
      <div
        v-else
        class="table-scroll-container"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
        }"
      >
        <table class="gradebook-table">
          <thead>
            <tr :style="{ backgroundColor: $themePalette.grey.v_100 }">
              <th class="sticky-col header-student">
                {{ studentHeader$() }}
              </th>
              <th
                v-for="assignment in gradebookData.assignments"
                :key="assignment.id"
                class="header-assignment"
              >
                <div class="assign-head-title" :title="assignment.title">
                  {{ assignment.title }}
                </div>
                <div class="assign-head-pts" :style="{ color: $themeTokens.annotation }">
                  / {{ assignment.max_points }} {{ ptsLabel$() }}
                </div>
              </th>
              <th class="header-summary">
                {{ totalScoreHeader$() }}
              </th>
              <th class="header-summary">
                {{ percentageHeader$() }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="learner in gradebookData.learners"
              :key="learner.id"
              :style="{ borderTop: `1px solid ${$themeTokens.fineLine}` }"
            >
              <!-- Student Info -->
              <td class="sticky-col cell-student" :style="{ backgroundColor: $themeTokens.surface }">
                <div class="student-name">{{ learner.full_name || learner.username }}</div>
                <div class="student-user" :style="{ color: $themeTokens.annotation }">
                  @{{ learner.username }}
                </div>
              </td>

              <!-- Scores for Each Assignment -->
              <td
                v-for="assignment in gradebookData.assignments"
                :key="assignment.id"
                class="cell-score"
              >
                <template v-if="learner.submissions && learner.submissions[assignment.id]">
                  <span
                    v-if="learner.submissions[assignment.id].grade !== null"
                    class="score-badge graded"
                    :class="getScoreClass(learner.submissions[assignment.id].grade, assignment.max_points)"
                  >
                    {{ learner.submissions[assignment.id].grade }}
                  </span>
                  <span
                    v-else
                    class="score-badge pending"
                    :title="pendingGradingTooltip$()"
                  >
                    ⏳ {{ submittedLabel$() }}
                  </span>
                </template>
                <span v-else class="empty-score">-</span>
              </td>

              <!-- Total Score -->
              <td class="cell-summary">
                <strong>{{ learner.total_earned }}</strong>
                <span :style="{ color: $themeTokens.annotation }">/ {{ learner.total_possible }}</span>
              </td>

              <!-- Overall Percentage -->
              <td class="cell-summary">
                <span
                  v-if="learner.percentage !== null"
                  class="percent-pill"
                  :class="getPercentClass(learner.percentage)"
                >
                  {{ learner.percentage }}%
                </span>
                <span v-else class="empty-score">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </CoachAppBarPage>
</template>

<script>
import { ref, onMounted } from 'vue';
import { createTranslator } from 'kolibri/utils/i18n';
import AssignmentResource from 'kolibri-common/apiResources/AssignmentResource';
import useCoreCoach from '../../composables/useCoreCoach';
import CoachAppBarPage from '../CoachAppBarPage';
import { PageNames } from '../../constants';

const strings = createTranslator('CoachGradebookStrings', {
  backToAssignments: { message: 'Assignments', context: 'Back link' },
  pageTitle: { message: 'Classroom Gradebook & Grading Center', context: 'Header title' },
  pageSubtitle: { message: 'Consolidated overview of all learner grades, homework completion, and averages.', context: 'Subheader' },
  exportCsvAction: { message: 'Export to CSV', context: 'Button' },
  noAssignmentsTitle: { message: 'No assignments to grade', context: 'Empty state title' },
  noAssignmentsDesc: { message: 'Create assignments first to start tracking learner submissions and grades.', context: 'Empty state desc' },
  createAssignmentAction: { message: 'Create Assignment', context: 'Button' },
  studentHeader: { message: 'Learner', context: 'Table column' },
  totalScoreHeader: { message: 'Total Pts', context: 'Table column' },
  percentageHeader: { message: 'Percentage', context: 'Table column' },
  ptsLabel: { message: 'pts', context: 'Points abbreviation' },
  submittedLabel: { message: 'Submitted', context: 'Badge' },
  pendingGradingTooltip: { message: 'Submitted and awaiting coach review', context: 'Tooltip' },
});

export default {
  name: 'GradebookPage',
  components: { CoachAppBarPage },
  setup() {
    const { classId } = useCoreCoach();
    const loading = ref(false);
    const gradebookData = ref(null);

    const {
      backToAssignments$,
      pageTitle$,
      pageSubtitle$,
      exportCsvAction$,
      noAssignmentsTitle$,
      noAssignmentsDesc$,
      createAssignmentAction$,
      studentHeader$,
      totalScoreHeader$,
      percentageHeader$,
      ptsLabel$,
      submittedLabel$,
      pendingGradingTooltip$,
    } = strings;

    async function loadGradebook() {
      loading.value = true;
      try {
        const data = await AssignmentResource.fetchGradebook(classId.value);
        gradebookData.value = data;
      } catch (err) {
        console.error('Failed to load gradebook', err);
      } finally {
        loading.value = false;
      }
    }

    onMounted(() => {
      loadGradebook();
    });

    function getScoreClass(grade, maxPoints) {
      if (!maxPoints) return '';
      const pct = (grade / maxPoints) * 100;
      if (pct >= 85) return 'high';
      if (pct >= 70) return 'mid';
      return 'low';
    }

    function getPercentClass(pct) {
      if (pct >= 90) return 'high';
      if (pct >= 75) return 'good';
      if (pct >= 60) return 'mid';
      return 'low';
    }

    function exportToCSV() {
      if (!gradebookData.value) return;
      const { assignments, learners, classroom_name } = gradebookData.value;

      const headers = ['Learner Name', 'Username'];
      assignments.forEach(a => {
        headers.push(`"${a.title} (${a.max_points} pts)"`);
      });
      headers.push('Total Points Earned', 'Total Possible', 'Percentage');

      const rows = [headers.join(',')];

      learners.forEach(learner => {
        const row = [
          `"${learner.full_name || learner.username}"`,
          `"${learner.username}"`,
        ];
        assignments.forEach(a => {
          const sub = learner.submissions[a.id];
          if (sub && sub.grade !== null) {
            row.push(sub.grade);
          } else if (sub && sub.status === 'submitted') {
            row.push('"Submitted (Pending)"');
          } else {
            row.push('""');
          }
        });
        row.push(learner.total_earned);
        row.push(learner.total_possible);
        row.push(learner.percentage !== null ? `"${learner.percentage}%"` : '""');
        rows.push(row.join(','));
      });

      const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + encodeURIComponent(rows.join('\n'));
      const link = document.createElement('a');
      link.setAttribute('href', csvContent);
      const safeName = (classroom_name || 'class').replace(/[^a-zA-Z0-9_-]/g, '_');
      link.setAttribute('download', `gradebook_${safeName}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    return {
      classId,
      PageNames,
      loading,
      gradebookData,
      getScoreClass,
      getPercentClass,
      exportToCSV,
      backToAssignments$,
      pageTitle$,
      pageSubtitle$,
      exportCsvAction$,
      noAssignmentsTitle$,
      noAssignmentsDesc$,
      createAssignmentAction$,
      studentHeader$,
      totalScoreHeader$,
      percentageHeader$,
      ptsLabel$,
      submittedLabel$,
      pendingGradingTooltip$,
    };
  },
};
</script>

<style lang="scss" scoped>
.gradebook-container {
  padding: 24px;
  max-width: 1400px;
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

.table-scroll-container {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.gradebook-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 14px;

  th,
  td {
    padding: 12px 16px;
    white-space: nowrap;
  }
}

.sticky-col {
  position: sticky;
  left: 0;
  z-index: 10;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
}

.header-student {
  font-weight: 700;
  min-width: 200px;
}

.header-assignment {
  min-width: 140px;
  text-align: center;
}

.assign-head-title {
  font-weight: 700;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.assign-head-pts {
  font-size: 12px;
  font-weight: 500;
}

.header-summary {
  font-weight: 700;
  text-align: center;
  min-width: 110px;
}

.cell-student {
  font-weight: 600;
}

.student-name {
  font-size: 14px;
}

.student-user {
  font-size: 12px;
  font-weight: 400;
}

.cell-score {
  text-align: center;
}

.score-badge {
  display: inline-block;
  font-size: 13px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;

  &.high {
    background-color: #dcfce7;
    color: #166534;
  }

  &.mid {
    background-color: #e0f2fe;
    color: #0369a1;
  }

  &.low {
    background-color: #fee2e2;
    color: #991b1b;
  }

  &.pending {
    background-color: #fef3c7;
    color: #92400e;
    font-size: 11px;
  }
}

.cell-summary {
  text-align: center;
}

.percent-pill {
  display: inline-block;
  font-size: 13px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 9999px;

  &.high {
    background-color: #22c55e;
    color: white;
  }

  &.good {
    background-color: #0284c7;
    color: white;
  }

  &.mid {
    background-color: #eab308;
    color: white;
  }

  &.low {
    background-color: #ef4444;
    color: white;
  }
}

.empty-score {
  color: #9ca3af;
}
</style>
