<template>
  <KPageContainer
    class="at-risk-block"
    :style="{
      backgroundColor: $themeTokens.surface,
      border: `1.5px solid ${hasHighRisk ? '#f87171' : $themeTokens.fineLine}`,
    }"
  >
    <!-- Header Section -->
    <div class="block-header">
      <div>
        <div class="header-tag-row">
          <span class="ews-badge">
            🚨 {{ earlyWarningBadge$() }}
          </span>
          <span class="dorp-tag">
            {{ depEdDorpLabel$() }}
          </span>
        </div>
        <h2 class="block-title" :style="{ color: $themeTokens.text }">
          {{ blockTitle$() }}
        </h2>
        <p class="block-desc" :style="{ color: $themeTokens.annotation }">
          {{ blockDesc$() }}
        </p>
      </div>

      <div class="header-actions">
        <KButton
          v-if="learners.length > 0 && isExpanded"
          :text="exportAllDorpCsv$()"
          icon="download"
          appearance="flat-button"
          @click="exportClassDorpCSV"
        />
        <SectionToggleButton
          :isExpanded="isExpanded"
          @click="toggleExpand"
        />
      </div>
    </div>

    <transition name="section-collapse">
      <div v-show="isExpanded">
        <!-- Metrics Summary & Filter Pills -->
        <div class="metrics-row">
      <button
        type="button"
        class="metric-pill pill-high"
        :class="{ active: currentFilter === 'high' }"
        @click="currentFilter = 'high'"
      >
        <span class="pill-dot dot-high"></span>
        <span class="pill-label">{{ highRiskPill$({ count: highRiskCount }) }}</span>
      </button>

      <button
        type="button"
        class="metric-pill pill-moderate"
        :class="{ active: currentFilter === 'moderate' }"
        @click="currentFilter = 'moderate'"
      >
        <span class="pill-dot dot-moderate"></span>
        <span class="pill-label">{{ moderateRiskPill$({ count: moderateRiskCount }) }}</span>
      </button>

      <button
        type="button"
        class="metric-pill pill-on-track"
        :class="{ active: currentFilter === 'low' }"
        @click="currentFilter = 'low'"
      >
        <span class="pill-dot dot-low"></span>
        <span class="pill-label">{{ onTrackPill$({ count: onTrackCount }) }}</span>
      </button>

      <button
        type="button"
        class="metric-pill pill-all"
        :class="{ active: currentFilter === 'all' }"
        @click="currentFilter = 'all'"
      >
        <span class="pill-label">{{ allStudentsPill$({ count: learners.length }) }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loader-container">
      <KCircularLoader />
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredLearners.length === 0" class="empty-state">
      <p :style="{ color: $themeTokens.annotation }">
        {{ currentFilter === 'high' ? noHighRiskMessage$() : noLearnersMessage$() }}
      </p>
    </div>

    <!-- Learner Cards List -->
    <div v-else class="learners-list">
      <div
        v-for="l in displayedLearners"
        :key="l.id"
        class="learner-card"
        :class="`border-risk-${l.risk_level}`"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
        }"
      >
        <div class="card-left">
          <div class="avatar" :class="`avatar-risk-${l.risk_level}`">
            {{ getInitials(l.name) }}
          </div>
          <div class="info-col">
            <div class="name-row">
              <span class="student-name" :style="{ color: $themeTokens.text }">
                {{ l.name }}
              </span>
              <span class="risk-badge" :class="`risk-${l.risk_level}`">
                {{ riskBadgeLabel$(l.risk_level) }}
              </span>
              <span v-if="l.risk_score > 0" class="risk-score">
                {{ riskScoreText$({ score: l.risk_score }) }}
              </span>
            </div>

            <!-- Trigger Pills Row -->
            <div class="trigger-pills-row">
              <!-- Attendance -->
              <span
                v-if="l.attendance_rate !== null"
                class="trigger-tag"
                :class="{ 'tag-flagged': l.attendance_rate < 80 }"
              >
                📅 {{ attendanceTag$({ rate: l.attendance_rate }) }}
              </span>

              <!-- Quiz Average -->
              <span
                v-if="l.quiz_average !== null"
                class="trigger-tag"
                :class="{ 'tag-flagged': l.quiz_average < 75 }"
              >
                📝 {{ quizAvgTag$({ avg: l.quiz_average }) }}
              </span>

              <!-- Missing Assignments -->
              <span
                v-if="l.missing_assignments > 0"
                class="trigger-tag"
                :class="{ 'tag-flagged': l.missing_assignments >= 2 }"
              >
                📥 {{ missingTasksTag$({ count: l.missing_assignments }) }}
              </span>

              <!-- Inactivity -->
              <span
                v-if="isInactive(l.last_active)"
                class="trigger-tag tag-flagged"
              >
                ⏳ {{ formatInactiveDays(l.last_active) }}
              </span>
            </div>

            <!-- Active Intervention Status Indicator -->
            <div v-if="l.latest_intervention" class="intervention-status-row">
              <span
                class="itv-pill"
                :class="`itv-status-${l.latest_intervention.status}`"
              >
                ⚡ {{ formatInterventionName(l.latest_intervention.intervention_type) }} ({{ l.latest_intervention.status }})
              </span>
              <span
                v-if="l.latest_intervention.notes"
                class="itv-note-preview"
                :style="{ color: $themeTokens.annotation }"
              >
                "{{ l.latest_intervention.notes }}"
              </span>
            </div>
            <div v-else-if="l.risk_level !== 'low'" class="needs-itv-row">
              <span class="needs-itv-tag">
                ⚠️ {{ needsInterventionNotice$() }}
              </span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="card-right-actions">
          <KButton
            :text="diagnosticsButton$()"
            icon="reports"
            appearance="raised-button"
            :primary="l.risk_level === 'high'"
            @click="openDiagnostics(l)"
          />
          <KButton
            :text="messageButton$()"
            icon="chat"
            appearance="flat-button"
            @click="handleMessageLearner(l)"
          />
        </div>
      </div>

      <!-- View More Toggle -->
      <div v-if="filteredLearners.length > maxVisible" class="show-more-row">
        <KButton
          :text="showAll ? showLess$() : showAllLearners$({ count: filteredLearners.length })"
          appearance="basic-link"
          @click="showAll = !showAll"
        />
      </div>
    </div>
  </div>
</transition>

    <!-- Diagnostics & Intervention Modal -->
    <AtRiskDiagnosticsModal
      v-if="selectedLearner"
      :learner="selectedLearner"
      :classId="classId"
      :className="className"
      @close="selectedLearner = null"
      @interventionUpdated="loadAnalytics"
    />
  </KPageContainer>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { createTranslator } from 'kolibri/utils/i18n';
import useChat from 'kolibri/composables/useChat';
import AtRiskAnalyticsResource from 'kolibri-common/apiResources/AtRiskAnalyticsResource';
import SectionToggleButton from 'kolibri-common/components/SectionToggleButton';
import useCollapsible from 'kolibri-common/composables/useCollapsible';
import useCoreCoach from '../../../composables/useCoreCoach';
import AtRiskDiagnosticsModal from './AtRiskDiagnosticsModal.vue';

const strings = createTranslator('AtRiskLearnersBlockStrings', {
  earlyWarningBadge: { message: 'Early Warning System (EWS)', context: 'Tag' },
  depEdDorpLabel: { message: 'DepEd Dropout Reduction Program & Child Protection', context: 'Badge' },
  blockTitle: { message: 'At-Risk Students & Remedial Interventions', context: 'Header' },
  blockDesc: {
    message: 'Proactive early identification of struggling learners based on attendance (<80%), quiz averages (<75%), missing assignments, and activity.',
    context: 'Subtitle',
  },
  highRiskPill: { message: '🔴 High Risk ({count})', context: 'Filter pill' },
  moderateRiskPill: { message: '🟠 Moderate Risk ({count})', context: 'Filter pill' },
  onTrackPill: { message: '🟢 On Track ({count})', context: 'Filter pill' },
  allStudentsPill: { message: 'All Enrolled ({count})', context: 'Filter pill' },
  exportAllDorpCsv: { message: 'Export DORP Report (CSV)', context: 'Button' },
  noHighRiskMessage: { message: 'No high-risk students identified. All students are meeting core attendance and performance benchmarks.', context: 'Empty state' },
  noLearnersMessage: { message: 'No students found in this category.', context: 'Empty state' },
  highRiskBadge: { message: 'High Risk', context: 'Badge' },
  moderateRiskBadge: { message: 'Moderate Risk', context: 'Badge' },
  onTrackBadge: { message: 'On Track', context: 'Badge' },
  riskScoreText: { message: 'Risk Index: {score}', context: 'Text' },
  attendanceTag: { message: 'Attendance: {rate}%', context: 'Tag' },
  quizAvgTag: { message: 'Quiz Avg: {avg}%', context: 'Tag' },
  missingTasksTag: { message: '{count} Missing', context: 'Tag' },
  needsInterventionNotice: { message: 'Action Needed: No active intervention recorded yet', context: 'Notice' },
  diagnosticsButton: { message: 'Diagnostics & Intervene', context: 'Button' },
  messageButton: { message: 'Message', context: 'Button' },
  showAllLearners: { message: 'Show all {count} students', context: 'Link' },
  showLess: { message: 'Show fewer', context: 'Link' },
});

export default {
  name: 'AtRiskLearnersBlock',
  components: {
    AtRiskDiagnosticsModal,
    SectionToggleButton,
  },
  setup() {
    const { isExpanded, toggleExpand } = useCollapsible('coach_at_risk', true);
    const { classId, className } = useCoreCoach();
    const { startDirectChat } = useChat();

    const loading = ref(true);
    const learners = ref([]);
    const highRiskCount = ref(0);
    const moderateRiskCount = ref(0);
    const onTrackCount = ref(0);
    const totalSessions = ref(0);
    const totalAssignments = ref(0);

    const currentFilter = ref('high');
    const selectedLearner = ref(null);
    const showAll = ref(false);
    const maxVisible = 4;

    const hasHighRisk = computed(() => highRiskCount.value > 0);

    async function loadAnalytics() {
      if (!classId.value) return;
      loading.value = true;
      try {
        const data = await AtRiskAnalyticsResource.fetchCollection({
          getParams: { collection: classId.value },
          force: true,
        });

        learners.value = data.learners || [];
        highRiskCount.value = data.high_risk_count || 0;
        moderateRiskCount.value = data.moderate_risk_count || 0;
        onTrackCount.value = data.on_track_count || 0;
        totalSessions.value = data.total_sessions || 0;
        totalAssignments.value = data.total_assignments || 0;

        // Auto-switch filter to moderate or all if no high-risk
        if (highRiskCount.value === 0 && moderateRiskCount.value > 0) {
          currentFilter.value = 'moderate';
        } else if (highRiskCount.value === 0 && moderateRiskCount.value === 0) {
          currentFilter.value = 'all';
        }
      } catch (err) {
        console.error('Failed to load at-risk analytics', err);
      } finally {
        loading.value = false;
      }
    }

    onMounted(() => {
      loadAnalytics();
    });

    const filteredLearners = computed(() => {
      if (currentFilter.value === 'all') return learners.value;
      return learners.value.filter(l => l.risk_level === currentFilter.value);
    });

    const displayedLearners = computed(() => {
      if (showAll.value) return filteredLearners.value;
      return filteredLearners.value.slice(0, maxVisible);
    });

    function getInitials(name) {
      if (!name) return '?';
      return name
        .split(' ')
        .filter(p => p.length > 0)
        .slice(0, 2)
        .map(p => p[0].toUpperCase())
        .join('');
    }

    function riskBadgeLabel$(level) {
      if (level === 'high') return strings.highRiskBadge$();
      if (level === 'moderate') return strings.moderateRiskBadge$();
      return strings.onTrackBadge$();
    }

    function isInactive(dateStr) {
      if (!dateStr) return true;
      const days = (Date.now() - new Date(dateStr).getTime()) / (1000 * 60 * 60 * 24);
      return days >= 7;
    }

    function formatInactiveDays(dateStr) {
      if (!dateStr) return 'No activity';
      const days = Math.floor((Date.now() - new Date(dateStr).getTime()) / (1000 * 60 * 60 * 24));
      return `${days}d Inactive`;
    }

    function formatInterventionName(val) {
      const map = {
        remedial_instruction: 'Remedial Instruction',
        peer_tutoring: 'Peer Tutoring',
        parent_contact: 'Parent Conference',
        counseling: 'Counseling',
        assignment_extension: 'Assignment Extension',
        learning_materials: 'Supplemental Reviewers',
      };
      return map[val] || val;
    }

    function openDiagnostics(learner) {
      selectedLearner.value = learner;
    }

    function handleMessageLearner(learner) {
      if (!learner || !learner.id) return;
      startDirectChat(learner.id);
    }

    function exportClassDorpCSV() {
      const headers = [
        'Learner Name',
        'Username',
        'Risk Level',
        'Risk Score',
        'Attendance Rate (%)',
        'Attended Sessions',
        'Total Sessions',
        'Quiz Average (%)',
        'Missing Tasks',
        'Active Interventions',
        'Latest Action',
      ];

      const rows = learners.value.map(l => {
        const latest = l.latest_intervention || {};
        return [
          `"${l.name}"`,
          `"${l.username}"`,
          `"${l.risk_level.toUpperCase()}"`,
          `"${l.risk_score || 0}"`,
          `"${l.attendance_rate !== null ? l.attendance_rate : 'N/A'}"`,
          `"${l.attendance_present || 0}"`,
          `"${l.attendance_total || 0}"`,
          `"${l.quiz_average !== null ? l.quiz_average : 'N/A'}"`,
          `"${l.missing_assignments || 0}"`,
          `"${l.active_intervention_count || 0}"`,
          `"${latest.intervention_type || 'None'}"`,
        ].join(',');
      });

      const csvContent = '\uFEFF' + [headers.join(','), ...rows].join('\r\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute(
        'download',
        `DepEd_DORP_Class_Report_${className.value || 'Class'}_${new Date().toISOString().slice(0, 10)}.csv`,
      );
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    return {
      classId,
      className,
      loading,
      learners,
      highRiskCount,
      moderateRiskCount,
      onTrackCount,
      currentFilter,
      selectedLearner,
      showAll,
      maxVisible,
      hasHighRisk,
      filteredLearners,
      displayedLearners,
      loadAnalytics,
      getInitials,
      riskBadgeLabel$,
      isInactive,
      formatInactiveDays,
      formatInterventionName,
      openDiagnostics,
      handleMessageLearner,
      exportClassDorpCSV,
      isExpanded,
      toggleExpand,
      ...strings,
    };
  },
};
</script>

<style lang="scss" scoped>
.at-risk-block {
  margin-top: 16px;
  border-radius: 8px;
  padding: 20px;
}

.block-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
}

.header-tag-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.ews-badge {
  font-size: 12px;
  font-weight: 800;
  color: #b91c1c;
  background: #fee2e2;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.3px;
}

.dorp-tag {
  font-size: 11px;
  font-weight: 600;
  color: #0369a1;
  background: #e0f2fe;
  padding: 2px 8px;
  border-radius: 4px;
}

.block-title {
  margin: 4px 0 2px 0;
  font-size: 20px;
  font-weight: 800;
}

.block-desc {
  margin: 0;
  font-size: 13px;
  max-width: 700px;
}

.metrics-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 16px 0;
}

.metric-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: 1.5px solid transparent;
  background: #f3f4f6;
  color: #374151;
  transition: all 0.15s ease;
}

.pill-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-high {
  background: #dc2626;
}

.dot-moderate {
  background: #f59e0b;
}

.dot-low {
  background: #16a34a;
}

.pill-high.active {
  background: #fee2e2;
  color: #991b1b;
  border-color: #f87171;
}

.pill-moderate.active {
  background: #fef3c7;
  color: #92400e;
  border-color: #fcd34d;
}

.pill-on-track.active {
  background: #dcfce7;
  color: #166534;
  border-color: #86efac;
}

.pill-all.active {
  background: #e5e7eb;
  color: #111827;
  border-color: #9ca3af;
}

.loader-container {
  padding: 30px;
  display: flex;
  justify-content: center;
}

.empty-state {
  padding: 20px 0;
  font-size: 14px;
}

.learners-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.learner-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 8px;
  flex-wrap: wrap;
  gap: 12px;
  transition: box-shadow 0.2s ease;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
}

.border-risk-high {
  border-left: 5px solid #dc2626 !important;
}

.border-risk-moderate {
  border-left: 5px solid #f59e0b !important;
}

.border-risk-low {
  border-left: 5px solid #16a34a !important;
}

.card-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 280px;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
  flex-shrink: 0;
}

.avatar-risk-high {
  background: #fee2e2;
  color: #991b1b;
}

.avatar-risk-moderate {
  background: #fef3c7;
  color: #92400e;
}

.avatar-risk-low {
  background: #dcfce7;
  color: #166534;
}

.info-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.student-name {
  font-size: 15px;
  font-weight: 700;
}

.risk-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  text-transform: uppercase;
}

.risk-high {
  background: #fee2e2;
  color: #991b1b;
}

.risk-moderate {
  background: #fef3c7;
  color: #92400e;
}

.risk-low {
  background: #dcfce7;
  color: #166534;
}

.risk-score {
  font-size: 11px;
  font-weight: 600;
  color: #6b7280;
}

.trigger-pills-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.trigger-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f3f4f6;
  color: #374151;
}

.tag-flagged {
  background: #fee2e2;
  color: #991b1b;
  font-weight: 700;
}

.intervention-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
  flex-wrap: wrap;
}

.itv-pill {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.itv-status-pending {
  background: #fef3c7;
  color: #92400e;
}

.itv-status-in_progress {
  background: #e0f2fe;
  color: #0369a1;
}

.itv-status-resolved {
  background: #dcfce7;
  color: #166534;
}

.itv-note-preview {
  font-size: 12px;
  font-style: italic;
}

.needs-itv-row {
  margin-top: 2px;
}

.needs-itv-tag {
  font-size: 11px;
  font-weight: 700;
  color: #b91c1c;
}

.card-right-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.show-more-row {
  display: flex;
  justify-content: center;
  padding-top: 6px;
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
