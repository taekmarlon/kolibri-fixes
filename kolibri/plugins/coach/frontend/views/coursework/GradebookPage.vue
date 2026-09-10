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
          <!-- View Mode Toggle -->
          <div class="view-mode-toggle">
            <button
              type="button"
              class="mode-btn"
              :class="{ active: viewMode === 'deped_summary' }"
              @click="viewMode = 'deped_summary'"
            >
              🇵🇭 DepEd 3-Term Summary (DO 009, s. 2026)
            </button>
            <button
              type="button"
              class="mode-btn"
              :class="{ active: viewMode === 'assignments_grid' }"
              @click="viewMode = 'assignments_grid'"
            >
              📝 Assignments Grid
            </button>
          </div>

          <KButton
            v-if="viewMode === 'deped_summary'"
            text="Export DepEd Form 138 (SF9) CSV"
            :primary="true"
            appearance="raised-button"
            icon="download"
            :disabled="!depEdLearnerSummaries || depEdLearnerSummaries.length === 0"
            @click="exportDepEdSummaryCSV"
          />
          <KButton
            v-else
            :text="exportCsvAction$()"
            :primary="true"
            appearance="raised-button"
            icon="download"
            :disabled="!gradebookData || !gradebookData.learners || gradebookData.learners.length === 0"
            @click="exportAssignmentsCSV"
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

      <!-- Main Content -->
      <div v-else>
        <!-- ============================================================ -->
        <!-- VIEW 1: DepEd 3-Term Composite Transmuted Summary Mode       -->
        <!-- ============================================================ -->
        <div v-if="viewMode === 'deped_summary'" class="deped-summary-section">
          <!-- Official DepEd Policy Banner -->
          <div class="deped-banner">
            <div class="banner-title">
              🇵🇭 Cedarhall Academy Inc. — Official DepEd Three-Term School Calendar (DO No. 009, s. 2026)
            </div>
            <div class="banner-desc">
              School Year 2026–2027 (201 Class Days) • Official DepEd Transmutation Scale (DO No. 8, s. 2015: 60% Passing Mark = 75).
              Final Rating is computed from Term 1, Term 2, and Term 3 composite evaluations.
            </div>
          </div>

          <!-- Summary KPI Cards -->
          <div class="kpi-grid">
            <div class="kpi-card" :style="{ backgroundColor: $themeTokens.surface, border: `1px solid ${$themeTokens.fineLine}` }">
              <div class="kpi-icon">👥</div>
              <div class="kpi-content">
                <div class="kpi-value" :style="{ color: $themeTokens.text }">{{ depEdStatistics.total }}</div>
                <div class="kpi-label" :style="{ color: $themeTokens.annotation }">Total Enrolled Students</div>
              </div>
            </div>

            <div class="kpi-card" :style="{ backgroundColor: $themeTokens.surface, border: `1px solid ${$themeTokens.fineLine}` }">
              <div class="kpi-icon">🏅</div>
              <div class="kpi-content">
                <div class="kpi-value passed-text">{{ depEdStatistics.passed }} ({{ depEdStatistics.passedRate }}%)</div>
                <div class="kpi-label" :style="{ color: $themeTokens.annotation }">Promoted / Passed (Grade &ge; 75)</div>
              </div>
            </div>

            <div class="kpi-card" :style="{ backgroundColor: $themeTokens.surface, border: `1px solid ${$themeTokens.fineLine}` }">
              <div class="kpi-icon">⚠️</div>
              <div class="kpi-content">
                <div class="kpi-value remediation-text">{{ depEdStatistics.remediation }} ({{ depEdStatistics.remediationRate }}%)</div>
                <div class="kpi-label" :style="{ color: $themeTokens.annotation }">Needs Remediation — ARAL Program (&lt; 75)</div>
              </div>
            </div>
          </div>

          <!-- DepEd Transmuted Summary Table -->
          <div
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
                    Learner (Name & LRN)
                  </th>
                  <th class="header-term term-1-head">
                    <div class="term-name">Term 1</div>
                    <div class="term-date">Jun 8 – Sep 15, 2026</div>
                  </th>
                  <th class="header-term term-2-head">
                    <div class="term-name">Term 2</div>
                    <div class="term-date">Sep 16 – Dec 18, 2026</div>
                  </th>
                  <th class="header-term term-3-head">
                    <div class="term-name">Term 3</div>
                    <div class="term-date">Jan 4 – Apr 8, 2027</div>
                  </th>
                  <th class="header-summary">
                    Final Rating
                  </th>
                  <th class="header-summary">
                    DepEd Action Taken
                  </th>
                  <th class="header-summary">
                    Descriptor
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="s in depEdLearnerSummaries"
                  :key="s.id"
                  :style="{ borderTop: `1px solid ${$themeTokens.fineLine}` }"
                >
                  <!-- Student Info -->
                  <td class="sticky-col cell-student" :style="{ backgroundColor: $themeTokens.surface }">
                    <div class="student-name">{{ s.fullName }}</div>
                    <div class="student-user" :style="{ color: $themeTokens.annotation }">
                      @{{ s.username }}
                    </div>
                  </td>

                  <!-- Term 1 -->
                  <td class="cell-term">
                    <div v-if="s.terms.term_1.transmuted !== null" class="term-grade-box">
                      <span class="raw-pct">{{ s.terms.term_1.rawPercentage }}%</span>
                      <span class="transmuted-badge" :class="getScoreBadgeClass(s.terms.term_1.transmuted)">
                        {{ s.terms.term_1.transmuted }}
                      </span>
                    </div>
                    <span v-else class="empty-score">-</span>
                  </td>

                  <!-- Term 2 -->
                  <td class="cell-term">
                    <div v-if="s.terms.term_2.transmuted !== null" class="term-grade-box">
                      <span class="raw-pct">{{ s.terms.term_2.rawPercentage }}%</span>
                      <span class="transmuted-badge" :class="getScoreBadgeClass(s.terms.term_2.transmuted)">
                        {{ s.terms.term_2.transmuted }}
                      </span>
                    </div>
                    <span v-else class="empty-score">-</span>
                  </td>

                  <!-- Term 3 -->
                  <td class="cell-term">
                    <div v-if="s.terms.term_3.transmuted !== null" class="term-grade-box">
                      <span class="raw-pct">{{ s.terms.term_3.rawPercentage }}%</span>
                      <span class="transmuted-badge" :class="getScoreBadgeClass(s.terms.term_3.transmuted)">
                        {{ s.terms.term_3.transmuted }}
                      </span>
                    </div>
                    <span v-else class="empty-score">-</span>
                  </td>

                  <!-- Final General Average -->
                  <td class="cell-summary">
                    <span v-if="s.finalRating !== null" class="final-rating-pill" :class="getScoreBadgeClass(s.finalRating)">
                      {{ s.finalRating }}
                    </span>
                    <span v-else class="empty-score">-</span>
                  </td>

                  <!-- Action Taken / Remarks -->
                  <td class="cell-summary">
                    <span
                      v-if="s.finalRating !== null"
                      class="deped-status-badge"
                      :class="s.finalRemarks.badgeClass"
                    >
                      {{ s.finalRemarks.status }}
                    </span>
                    <span v-else class="empty-score">Pending</span>
                  </td>

                  <!-- Descriptor -->
                  <td class="cell-summary">
                    <span class="descriptor-text" :style="{ color: $themeTokens.annotation }">
                      {{ s.finalRemarks.descriptor }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ============================================================ -->
        <!-- VIEW 2: Standard Assignments Grid Mode (with Term Filter)    -->
        <!-- ============================================================ -->
        <div v-else class="assignments-grid-section">
          <!-- Term Filter Controls -->
          <div class="term-filter-row">
            <span class="term-filter-heading">Filter Assignments by DepEd Term:</span>
            <div class="filter-pill-group">
              <button
                type="button"
                class="filter-pill"
                :class="{ active: selectedTermFilter === 'all' }"
                @click="selectedTermFilter = 'all'"
              >
                All Assignments ({{ gradebookData.assignments.length }})
              </button>
              <button
                v-for="term in depEdTermConfig"
                :key="term.key"
                type="button"
                class="filter-pill"
                :class="[term.badgeClass, { active: selectedTermFilter === term.key }]"
                @click="selectedTermFilter = term.key"
              >
                {{ term.shortLabel }} ({{ countAssignmentsByTerm(term.key) }})
              </button>
            </div>
          </div>

          <!-- Gradebook Table Grid -->
          <div
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
                    v-for="assignment in visibleAssignments"
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
                  v-for="learner in filteredLearnersData"
                  :key="learner.id"
                  :style="{ borderTop: `1px solid ${$themeTokens.fineLine}` }"
                >
                  <!-- Student Info -->
                  <td class="sticky-col cell-student" :style="{ backgroundColor: $themeTokens.surface }">
                    <div class="student-name">{{ learner.fullName }}</div>
                    <div class="student-user" :style="{ color: $themeTokens.annotation }">
                      @{{ learner.username }}
                    </div>
                  </td>

                  <!-- Scores for Each Visible Assignment -->
                  <td
                    v-for="assignment in visibleAssignments"
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

                  <!-- Total Score for Filtered Scope -->
                  <td class="cell-summary">
                    <strong>{{ learner.totalEarned }}</strong>
                    <span :style="{ color: $themeTokens.annotation }">/ {{ learner.totalPossible }}</span>
                  </td>

                  <!-- Percentage for Filtered Scope -->
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
      </div>
    </div>
  </CoachAppBarPage>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router/composables';
import { createTranslator } from 'kolibri/utils/i18n';
import AssignmentResource from 'kolibri-common/apiResources/AssignmentResource';
import useCoreCoach from '../../composables/useCoreCoach';
import CoachAppBarPage from '../CoachAppBarPage';
import { PageNames } from '../../constants';
import {
  getItemTerm,
  DEPED_TERM_CONFIG,
  DEPED_TERMS,
  transmuteDepEdScore,
  getDepEdRemarks,
} from '../../utils/depEdTerms';

const strings = createTranslator('CoachGradebookStrings', {
  backToAssignments: { message: 'Assignments', context: 'Back link' },
  pageTitle: { message: 'Classroom Gradebook & DepEd Grading Center', context: 'Header title' },
  pageSubtitle: {
    message: 'Official DepEd Three-Term School Calendar (DO No. 009, s. 2026) consolidated ratings and gradebook.',
    context: 'Subheader',
  },
  exportCsvAction: { message: 'Export Assignments CSV', context: 'Button' },
  noAssignmentsTitle: { message: 'No assignments to grade', context: 'Empty state title' },
  noAssignmentsDesc: { message: 'Create assignments first to start tracking learner submissions and grades.', context: 'Empty state desc' },
  createAssignmentAction: { message: 'Create Assignment', context: 'Button' },
  studentHeader: { message: 'Learner', context: 'Table column' },
  totalScoreHeader: { message: 'Total Pts', context: 'Table column' },
  percentageHeader: { message: 'Percentage', context: 'Table column' },
  ptsLabel: { message: 'pts', context: 'Points abbreviation' },
  submittedLabel: { message: 'Submitted', context: 'Badge' },
  pendingGradingTooltip: { message: 'Submitted and awaiting faculty review', context: 'Tooltip' },
});

export default {
  name: 'GradebookPage',
  components: { CoachAppBarPage },
  setup() {
    const route = useRoute();
    const { classId } = useCoreCoach();
    const loading = ref(false);
    const gradebookData = ref(null);
    const viewMode = ref('deped_summary'); // 'deped_summary' | 'assignments_grid'
    const selectedTermFilter = ref('all');

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
        const targetClassId = classId.value || (route.params && route.params.classId);
        const data = await AssignmentResource.fetchGradebook(targetClassId);
        const payload = data && data.data ? data.data : data;
        gradebookData.value = payload;
      } catch (err) {
        console.error('Failed to load gradebook', err);
      } finally {
        loading.value = false;
      }
    }

    onMounted(() => {
      loadGradebook();
    });

    function countAssignmentsByTerm(termKey) {
      if (!gradebookData.value || !gradebookData.value.assignments) return 0;
      return gradebookData.value.assignments.filter(a => getItemTerm(a) === termKey).length;
    }

    const visibleAssignments = computed(() => {
      if (!gradebookData.value || !gradebookData.value.assignments) return [];
      if (selectedTermFilter.value === 'all') {
        return gradebookData.value.assignments;
      }
      return gradebookData.value.assignments.filter(
        a => getItemTerm(a) === selectedTermFilter.value,
      );
    });

    const filteredLearnersData = computed(() => {
      if (!gradebookData.value || !gradebookData.value.learners) return [];
      const currentAssignments = visibleAssignments.value;

      return gradebookData.value.learners.map(learner => {
        let totalEarned = 0;
        let totalPossible = 0;

        currentAssignments.forEach(a => {
          totalPossible += a.max_points;
          const sub = learner.submissions && learner.submissions[a.id];
          if (sub && sub.grade !== null) {
            totalEarned += sub.grade;
          }
        });

        const percentage =
          totalPossible > 0 ? Number(((totalEarned / totalPossible) * 100).toFixed(1)) : null;

        return {
          id: learner.id,
          username: learner.username,
          fullName: learner.full_name || learner.username,
          submissions: learner.submissions || {},
          totalEarned,
          totalPossible,
          percentage,
        };
      });
    });

    // DepEd 3-Term Composite Transmuted Summary per learner
    const depEdLearnerSummaries = computed(() => {
      if (!gradebookData.value || !gradebookData.value.learners) return [];
      const assignments = gradebookData.value.assignments || [];
      const learners = gradebookData.value.learners || [];

      const assignmentsByTerm = {
        term_1: assignments.filter(a => getItemTerm(a) === DEPED_TERMS.TERM_1),
        term_2: assignments.filter(a => getItemTerm(a) === DEPED_TERMS.TERM_2),
        term_3: assignments.filter(a => getItemTerm(a) === DEPED_TERMS.TERM_3),
      };

      return learners.map(learner => {
        const terms = {};
        const validTransmutedGrades = [];

        ['term_1', 'term_2', 'term_3'].forEach(termKey => {
          const termAssigns = assignmentsByTerm[termKey];
          let earned = 0;
          let possible = 0;
          let hasAnyGraded = false;

          termAssigns.forEach(a => {
            const sub = learner.submissions && learner.submissions[a.id];
            possible += a.max_points;
            if (sub && sub.grade !== null) {
              earned += sub.grade;
              hasAnyGraded = true;
            }
          });

          const rawPercentage =
            possible > 0 ? Number(((earned / possible) * 100).toFixed(1)) : null;
          const transmuted =
            hasAnyGraded && rawPercentage !== null ? transmuteDepEdScore(rawPercentage) : null;
          const remarks = getDepEdRemarks(transmuted);

          if (transmuted !== null) {
            validTransmutedGrades.push(transmuted);
          }

          terms[termKey] = {
            earned,
            possible,
            rawPercentage,
            transmuted,
            remarks,
            assignmentCount: termAssigns.length,
          };
        });

        let finalRating = null;
        let finalRemarks = {
          status: 'No Grade',
          badgeClass: 'status-pending',
          aral: false,
          descriptor: 'Pending',
        };

        if (validTransmutedGrades.length > 0) {
          const sum = validTransmutedGrades.reduce((acc, g) => acc + g, 0);
          finalRating = Math.round(sum / validTransmutedGrades.length);
          finalRemarks = getDepEdRemarks(finalRating);
        }

        return {
          id: learner.id,
          username: learner.username,
          fullName: learner.full_name || learner.username,
          terms,
          finalRating,
          finalRemarks,
        };
      });
    });

    const depEdStatistics = computed(() => {
      const summaries = depEdLearnerSummaries.value;
      const total = summaries.length;
      if (total === 0) {
        return { total: 0, passed: 0, passedRate: 0, remediation: 0, remediationRate: 0 };
      }
      const passed = summaries.filter(s => s.finalRating !== null && s.finalRating >= 75).length;
      const remediation = summaries.filter(s => s.finalRemarks.aral).length;
      const passedRate = Math.round((passed / total) * 100);
      const remediationRate = Math.round((remediation / total) * 100);

      return { total, passed, passedRate, remediation, remediationRate };
    });

    function getScoreBadgeClass(grade) {
      if (grade === null || grade === undefined) return '';
      if (grade >= 90) return 'score-outstanding';
      if (grade >= 85) return 'score-very-satisfactory';
      if (grade >= 80) return 'score-satisfactory';
      if (grade >= 75) return 'score-fairly-satisfactory';
      return 'score-remediation';
    }

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

    function exportDepEdSummaryCSV() {
      if (!depEdLearnerSummaries.value || depEdLearnerSummaries.value.length === 0) return;
      const className = (gradebookData.value && gradebookData.value.classroom_name) || 'Class';

      const headers = [
        'Learner Name',
        'LRN / Username',
        'Term 1 Raw (%)',
        'Term 1 Transmuted Grade (DO 8 / DO 009)',
        'Term 2 Raw (%)',
        'Term 2 Transmuted Grade',
        'Term 3 Raw (%)',
        'Term 3 Transmuted Grade',
        'Final General Average',
        'Action Taken / Status',
        'Descriptor',
      ];

      const rows = [headers.join(',')];

      depEdLearnerSummaries.value.forEach(s => {
        const t1 = s.terms.term_1;
        const t2 = s.terms.term_2;
        const t3 = s.terms.term_3;

        const row = [
          `"${s.fullName}"`,
          `"${s.username}"`,
          t1.rawPercentage !== null ? `"${t1.rawPercentage}%"` : '""',
          t1.transmuted !== null ? t1.transmuted : '""',
          t2.rawPercentage !== null ? `"${t2.rawPercentage}%"` : '""',
          t2.transmuted !== null ? t2.transmuted : '""',
          t3.rawPercentage !== null ? `"${t3.rawPercentage}%"` : '""',
          t3.transmuted !== null ? t3.transmuted : '""',
          s.finalRating !== null ? s.finalRating : '""',
          `"${s.finalRemarks.status}"`,
          `"${s.finalRemarks.descriptor}"`,
        ];
        rows.push(row.join(','));
      });

      const csvContent =
        'data:text/csv;charset=utf-8,\uFEFF' + encodeURIComponent(rows.join('\n'));
      const link = document.createElement('a');
      link.setAttribute('href', csvContent);
      const safeName = className.replace(/[^a-zA-Z0-9_-]/g, '_');
      link.setAttribute('download', `deped_form138_summary_${safeName}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    function exportAssignmentsCSV() {
      if (!gradebookData.value) return;
      const { classroom_name } = gradebookData.value;
      const assigns = visibleAssignments.value;
      const learners = filteredLearnersData.value;

      const headers = ['Learner Name', 'Username'];
      assigns.forEach(a => {
        headers.push(`"${a.title} (${a.max_points} pts)"`);
      });
      headers.push('Total Points Earned', 'Total Possible', 'Percentage');

      const rows = [headers.join(',')];

      learners.forEach(learner => {
        const row = [`"${learner.fullName}"`, `"${learner.username}"`];
        assigns.forEach(a => {
          const sub = learner.submissions[a.id];
          if (sub && sub.grade !== null) {
            row.push(sub.grade);
          } else if (sub && sub.status === 'submitted') {
            row.push('"Submitted (Pending)"');
          } else {
            row.push('""');
          }
        });
        row.push(learner.totalEarned);
        row.push(learner.totalPossible);
        row.push(learner.percentage !== null ? `"${learner.percentage}%"` : '""');
        rows.push(row.join(','));
      });

      const csvContent =
        'data:text/csv;charset=utf-8,\uFEFF' + encodeURIComponent(rows.join('\n'));
      const link = document.createElement('a');
      link.setAttribute('href', csvContent);
      const safeName = (classroom_name || 'class').replace(/[^a-zA-Z0-9_-]/g, '_');
      link.setAttribute('download', `assignments_gradebook_${safeName}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    return {
      classId,
      PageNames,
      loading,
      gradebookData,
      viewMode,
      selectedTermFilter,
      depEdTermConfig: DEPED_TERM_CONFIG,
      visibleAssignments,
      filteredLearnersData,
      depEdLearnerSummaries,
      depEdStatistics,
      countAssignmentsByTerm,
      getScoreBadgeClass,
      getScoreClass,
      getPercentClass,
      exportDepEdSummaryCSV,
      exportAssignmentsCSV,
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
  align-items: center;
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

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.view-mode-toggle {
  display: flex;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #d1d5db;
  background-color: #f3f4f6;

  .mode-btn {
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 700;
    border: none;
    background: transparent;
    cursor: pointer;
    color: #4b5563;
    transition: all 0.2s ease;

    &.active {
      background-color: #0d47a1;
      color: #ffffff;
      box-shadow: 0 2px 4px rgba(13, 71, 161, 0.2);
    }
  }
}

/* DepEd Summary Banner */
.deped-banner {
  background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
  color: #ffffff;
  padding: 16px 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  box-shadow: 0 3px 8px rgba(13, 71, 161, 0.15);

  .banner-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 4px;
    letter-spacing: 0.3px;
  }

  .banner-desc {
    font-size: 13px;
    opacity: 0.9;
    line-height: 1.4;
  }
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);

  .kpi-icon {
    font-size: 32px;
  }

  .kpi-value {
    font-size: 22px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 4px;

    &.passed-text {
      color: #166534;
    }

    &.remediation-text {
      color: #dc2626;
    }
  }

  .kpi-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
}

/* Term Filter Row */
.term-filter-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
}

.term-filter-heading {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #4b5563;
}

.filter-pill-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-pill {
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 20px;
  border: 1px solid #d1d5db;
  background-color: #f9fafb;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: #f3f4f6;
  }

  &.active {
    background-color: #0d47a1;
    color: #ffffff;
    border-color: #0d47a1;
    box-shadow: 0 2px 4px rgba(13, 71, 161, 0.25);
  }
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
  min-width: 220px;
}

.header-term {
  text-align: center;
  min-width: 150px;

  .term-name {
    font-weight: 700;
    font-size: 14px;
  }

  .term-date {
    font-size: 11px;
    font-weight: 500;
    color: #6b7280;
  }
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
  min-width: 130px;
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

.cell-term {
  text-align: center;
}

.term-grade-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .raw-pct {
    font-size: 12px;
    color: #6b7280;
  }

  .transmuted-badge {
    display: inline-block;
    padding: 3px 8px;
    font-size: 13px;
    font-weight: 800;
    border-radius: 6px;
  }
}

.final-rating-pill {
  display: inline-block;
  font-size: 14px;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 9999px;
}

.deped-status-badge {
  display: inline-block;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 800;
  border-radius: 9999px;
  letter-spacing: 0.5px;

  &.status-outstanding,
  &.status-very-satisfactory,
  &.status-satisfactory,
  &.status-fairly-satisfactory {
    background-color: #dcfce7;
    color: #166534;
    border: 1px solid #bbf7d0;
  }

  &.status-remediation {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #fecaca;
  }

  &.status-pending {
    background-color: #f3f4f6;
    color: #4b5563;
  }
}

.descriptor-text {
  font-size: 12px;
  font-weight: 600;
}

.score-outstanding {
  background-color: #dcfce7;
  color: #166534;
}

.score-very-satisfactory {
  background-color: #dbeafe;
  color: #1e40af;
}

.score-satisfactory {
  background-color: #e0e7ff;
  color: #3730a3;
}

.score-fairly-satisfactory {
  background-color: #fef3c7;
  color: #92400e;
}

.score-remediation {
  background-color: #fee2e2;
  color: #991b1b;
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
