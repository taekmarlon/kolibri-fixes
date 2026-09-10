<template>
  <KModal
    :title="modalTitle$()"
    :cancelText="closeButton$()"
    size="large"
    @cancel="$emit('close')"
  >
    <div v-if="learner" class="ews-modal-body">
      <!-- Learner Header Banner -->
      <div
        class="learner-summary-header"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
        }"
      >
        <div class="learner-identity">
          <div class="learner-avatar">
            {{ getInitials(learner.name) }}
          </div>
          <div>
            <h2 class="learner-name" :style="{ color: $themeTokens.text }">
              {{ learner.name }}
            </h2>
            <span class="learner-username" :style="{ color: $themeTokens.annotation }">
              @{{ learner.username }} &bull; {{ className }}
            </span>
          </div>
        </div>

        <div class="header-badges">
          <span
            class="risk-badge"
            :class="`risk-${learner.risk_level}`"
          >
            {{ riskLevelLabel$(learner.risk_level) }}
          </span>
          <span class="risk-score-pill">
            {{ riskScoreLabel$({ score: learner.risk_score || 0 }) }}
          </span>
        </div>
      </div>

      <!-- Quick Action Toolbar -->
      <div class="quick-toolbar">
        <KButton
          :text="chatButton$()"
          icon="chat"
          appearance="raised-button"
          :primary="true"
          @click="handleStartChat"
        />
        <KButton
          :text="exportDorpCsv$()"
          icon="download"
          appearance="flat-button"
          @click="exportDorpCSV"
        />
        <KButton
          :text="printReport$()"
          icon="print"
          appearance="flat-button"
          @click="handlePrintReport"
        />
      </div>

      <!-- 4-Stat Diagnostic Grid -->
      <div class="diagnostic-grid">
        <!-- Attendance -->
        <div
          class="diag-card"
          :class="{ 'card-flagged': learner.attendance_rate !== null && learner.attendance_rate < 80 }"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
        >
          <div class="diag-header">
            <span class="diag-icon">📅</span>
            <span class="diag-title">{{ attendanceMetricLabel$() }}</span>
          </div>
          <div class="diag-val">
            {{ learner.attendance_rate !== null ? `${learner.attendance_rate}%` : 'N/A' }}
          </div>
          <div class="diag-sub" :style="{ color: $themeTokens.annotation }">
            {{ attendedSessionsLabel$({ present: learner.attendance_present || 0, total: learner.attendance_total || 0 }) }}
          </div>
        </div>

        <!-- Quiz Performance -->
        <div
          class="diag-card"
          :class="{ 'card-flagged': learner.quiz_average !== null && learner.quiz_average < 75 }"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
        >
          <div class="diag-header">
            <span class="diag-icon">📝</span>
            <span class="diag-title">{{ quizMetricLabel$() }}</span>
          </div>
          <div class="diag-val">
            {{ learner.quiz_average !== null ? `${learner.quiz_average}%` : 'N/A' }}
          </div>
          <div class="diag-sub" :style="{ color: $themeTokens.annotation }">
            {{ learner.quiz_average !== null && learner.quiz_average < 75 ? depEdPassingAlert$() : depEdPassingOk$() }}
          </div>
        </div>

        <!-- Missing Tasks -->
        <div
          class="diag-card"
          :class="{ 'card-flagged': learner.missing_assignments >= 2 }"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
        >
          <div class="diag-header">
            <span class="diag-icon">📥</span>
            <span class="diag-title">{{ missingTasksMetricLabel$() }}</span>
          </div>
          <div class="diag-val">
            {{ learner.missing_assignments || 0 }}
          </div>
          <div class="diag-sub" :style="{ color: $themeTokens.annotation }">
            {{ outOfTotalAssignmentsLabel$({ total: learner.total_assignments || 0 }) }}
          </div>
        </div>

        <!-- Inactivity -->
        <div
          class="diag-card"
          :class="{ 'card-flagged': isInactive(learner.last_active) }"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
        >
          <div class="diag-header">
            <span class="diag-icon">⏳</span>
            <span class="diag-title">{{ activityMetricLabel$() }}</span>
          </div>
          <div class="diag-val">
            {{ formatLastActive(learner.last_active) }}
          </div>
          <div class="diag-sub" :style="{ color: $themeTokens.annotation }">
            {{ learner.last_active ? formatDate(learner.last_active) : noActivityRecorded$() }}
          </div>
        </div>
      </div>

      <!-- Specific Risk Factors Triggered -->
      <div v-if="learner.risk_factors && learner.risk_factors.length > 0" class="risk-factors-section">
        <h3 class="section-title" :style="{ color: $themeTokens.text }">
          ⚠️ {{ identifiedTriggersTitle$() }}
        </h3>
        <div class="triggers-list">
          <div
            v-for="(factor, idx) in learner.risk_factors"
            :key="idx"
            class="trigger-item"
            :class="`trigger-${factor.severity}`"
          >
            <div class="trigger-label">
              {{ factor.label }}
            </div>
            <div class="trigger-detail">
              {{ factor.detail }}
            </div>
          </div>
        </div>
      </div>

      <!-- Log New Intervention Section -->
      <div
        class="intervention-form-container"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
        }"
      >
        <h3 class="section-title" :style="{ color: $themeTokens.text }">
          📝 {{ logInterventionTitle$() }}
        </h3>

        <div class="form-row">
          <KSelect
            v-model="selectedType"
            :label="interventionTypeLabel$()"
            :options="typeOptions"
            style="flex: 1; min-width: 240px;"
          />
          <KSelect
            v-model="selectedStatus"
            :label="interventionStatusLabel$()"
            :options="statusOptions"
            style="flex: 1; min-width: 180px;"
          />
        </div>

        <KTextbox
          v-model="interventionNotes"
          :label="clinicalNotesLabel$()"
          :placeholder="clinicalNotesPlaceholder$()"
          :textArea="true"
          style="margin-top: 8px;"
        />

        <div class="form-submit-row">
          <KButton
            :text="submittingIntervention ? saving$() : saveInterventionButton$()"
            :primary="true"
            appearance="raised-button"
            icon="add"
            :disabled="submittingIntervention || !selectedType"
            @click="handleSubmitIntervention"
          />
          <span v-if="saveSuccess" class="save-success-tag">
            ✓ {{ interventionSaved$() }}
          </span>
        </div>
      </div>

      <!-- Past Interventions History Timeline -->
      <div class="intervention-history-section">
        <h3 class="section-title" :style="{ color: $themeTokens.text }">
          📋 {{ pastInterventionsTitle$() }} ({{ interventionsList.length }})
        </h3>

        <p
          v-if="interventionsList.length === 0"
          class="no-history-text"
          :style="{ color: $themeTokens.annotation }"
        >
          {{ noPastInterventions$() }}
        </p>

        <div v-else class="history-list">
          <div
            v-for="itv in interventionsList"
            :key="itv.id"
            class="history-card"
            :style="{
              backgroundColor: $themeTokens.surface,
              border: `1px solid ${$themeTokens.fineLine}`,
            }"
          >
            <div class="history-header">
              <div class="history-meta">
                <span class="history-type-badge">
                  {{ formatInterventionType(itv.intervention_type) }}
                </span>
                <span
                  class="history-status-badge"
                  :class="`status-${itv.status}`"
                >
                  {{ formatStatus(itv.status) }}
                </span>
              </div>
              <div class="history-date" :style="{ color: $themeTokens.annotation }">
                {{ formatDate(itv.date_created) }} &bull; {{ itv.coach_name || facultyLabel$() }}
              </div>
            </div>

            <p v-if="itv.notes" class="history-notes" :style="{ color: $themeTokens.text }">
              "{{ itv.notes }}"
            </p>

            <!-- Quick Status Transition Buttons -->
            <div class="history-actions">
              <button
                v-if="itv.status !== 'resolved'"
                type="button"
                class="status-btn btn-resolve"
                @click="updateInterventionStatus(itv, 'resolved')"
              >
                ✓ {{ markResolvedAction$() }}
              </button>
              <button
                v-if="itv.status === 'pending'"
                type="button"
                class="status-btn btn-progress"
                @click="updateInterventionStatus(itv, 'in_progress')"
              >
                🔄 {{ markInProgressAction$() }}
              </button>
              <button
                v-if="itv.status === 'resolved'"
                type="button"
                class="status-btn btn-reopen"
                @click="updateInterventionStatus(itv, 'in_progress')"
              >
                ↩ {{ reopenAction$() }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </KModal>
</template>

<script>
import { ref, computed } from 'vue';
import { createTranslator } from 'kolibri/utils/i18n';
import useChat from 'kolibri/composables/useChat';
import LearnerInterventionResource from 'kolibri-common/apiResources/LearnerInterventionResource';

const strings = createTranslator('AtRiskDiagnosticsModalStrings', {
  modalTitle: { message: 'At-Risk Diagnostics & Remedial Intervention', context: 'Modal title' },
  closeButton: { message: 'Close', context: 'Button' },
  chatButton: { message: 'Message Student', context: 'Button' },
  exportDorpCsv: { message: 'Export DepEd DORP CSV', context: 'Button' },
  printReport: { message: 'Print Summary', context: 'Button' },
  highRisk: { message: 'High Risk (Intervention Urgent)', context: 'Badge' },
  moderateRisk: { message: 'Moderate Risk', context: 'Badge' },
  onTrack: { message: 'On Track', context: 'Badge' },
  riskScoreLabel: { message: 'Risk Index: {score}/100', context: 'Pill' },
  attendanceMetricLabel: { message: 'Attendance Rate', context: 'Metric card' },
  attendedSessionsLabel: { message: '{present} of {total} sessions attended', context: 'Metric sub' },
  quizMetricLabel: { message: 'Quiz Performance', context: 'Metric card' },
  depEdPassingAlert: { message: 'Below 75% DepEd Standard', context: 'Alert' },
  depEdPassingOk: { message: 'Meets 75% Passing Standard', context: 'Text' },
  missingTasksMetricLabel: { message: 'Missing Assignments', context: 'Metric card' },
  outOfTotalAssignmentsLabel: { message: 'Out of {total} active assignments', context: 'Metric sub' },
  activityMetricLabel: { message: 'Platform Activity', context: 'Metric card' },
  noActivityRecorded: { message: 'No activity recorded yet', context: 'Metric sub' },
  identifiedTriggersTitle: { message: 'Identified Risk Triggers & Diagnostic Factors', context: 'Section' },
  logInterventionTitle: { message: 'Log New Remedial Intervention', context: 'Section' },
  interventionTypeLabel: { message: 'Intervention Program', context: 'Dropdown' },
  interventionStatusLabel: { message: 'Initial Status', context: 'Dropdown' },
  clinicalNotesLabel: { message: 'Teacher Remarks & Action Plan', context: 'Textarea' },
  clinicalNotesPlaceholder: {
    message: 'Detail specific remedial instruction given, peer tutoring buddy assigned, or parent consultation agreement...',
    context: 'Placeholder',
  },
  saveInterventionButton: { message: 'Save Intervention Record', context: 'Button' },
  saving: { message: 'Saving...', context: 'Status' },
  interventionSaved: { message: 'Intervention logged successfully!', context: 'Notification' },
  pastInterventionsTitle: { message: 'Intervention & Remedial History', context: 'Section' },
  noPastInterventions: {
    message: 'No intervention records logged yet for this student. Use the form above to record your first remedial session.',
    context: 'Empty text',
  },
  facultyLabel: { message: 'Faculty', context: 'Label' },
  markResolvedAction: { message: 'Mark as Resolved', context: 'Button' },
  markInProgressAction: { message: 'Set In Progress', context: 'Button' },
  reopenAction: { message: 'Reopen Intervention', context: 'Button' },
});

export default {
  name: 'AtRiskDiagnosticsModal',
  props: {
    learner: {
      type: Object,
      required: true,
    },
    classId: {
      type: String,
      required: true,
    },
    className: {
      type: String,
      default: 'Classroom',
    },
  },
  emits: ['close', 'interventionUpdated'],
  setup(props, { emit }) {
    const { startDirectChat } = useChat();

    const selectedType = ref({
      value: 'remedial_instruction',
      label: 'Remedial Instruction (DepEd DO No. 8, s. 2015)',
    });
    const selectedStatus = ref({
      value: 'in_progress',
      label: 'In Progress',
    });
    const interventionNotes = ref('');
    const submittingIntervention = ref(false);
    const saveSuccess = ref(false);

    const interventionsList = ref(props.learner.interventions ? [...props.learner.interventions] : []);

    const typeOptions = [
      { value: 'remedial_instruction', label: 'Remedial Instruction (DepEd DO No. 8, s. 2015)' },
      { value: 'peer_tutoring', label: 'Peer Tutoring & Study Buddy Program' },
      { value: 'parent_contact', label: 'Parent / Guardian Conference & Notice' },
      { value: 'counseling', label: 'Guidance Counselor Consultation' },
      { value: 'assignment_extension', label: 'Assignment Deadline Extension' },
      { value: 'learning_materials', label: 'Supplemental Modules & Reviewers' },
    ];

    const statusOptions = [
      { value: 'pending', label: 'Pending' },
      { value: 'in_progress', label: 'In Progress' },
      { value: 'resolved', label: 'Resolved' },
    ];

    function getInitials(name) {
      if (!name) return '?';
      return name
        .split(' ')
        .filter(p => p.length > 0)
        .slice(0, 2)
        .map(p => p[0].toUpperCase())
        .join('');
    }

    function riskLevelLabel$(level) {
      if (level === 'high') return strings.highRisk$();
      if (level === 'moderate') return strings.moderateRisk$();
      return strings.onTrack$();
    }

    function isInactive(dateStr) {
      if (!dateStr) return true;
      const days = (Date.now() - new Date(dateStr).getTime()) / (1000 * 60 * 60 * 24);
      return days >= 7;
    }

    function formatLastActive(dateStr) {
      if (!dateStr) return 'Inactive';
      const days = Math.floor((Date.now() - new Date(dateStr).getTime()) / (1000 * 60 * 60 * 24));
      if (days === 0) return 'Active Today';
      if (days === 1) return '1 day ago';
      return `${days} days ago`;
    }

    function formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    }

    function formatInterventionType(val) {
      const match = typeOptions.find(o => o.value === val);
      return match ? match.label : val;
    }

    function formatStatus(val) {
      const match = statusOptions.find(o => o.value === val);
      return match ? match.label : val;
    }

    function handleStartChat() {
      if (!props.learner || !props.learner.id) return;
      startDirectChat(props.learner.id);
      emit('close');
    }

    async function handleSubmitIntervention() {
      if (!selectedType.value || submittingIntervention.value) return;
      submittingIntervention.value = true;
      saveSuccess.value = false;

      try {
        const payload = {
          collection: props.classId,
          learner: props.learner.id,
          risk_level: props.learner.risk_level || 'moderate',
          reasons: (props.learner.risk_factors || []).map(f => f.category),
          intervention_type: selectedType.value.value || selectedType.value,
          status: selectedStatus.value.value || selectedStatus.value,
          notes: interventionNotes.value,
        };

        const saved = await LearnerInterventionResource.saveModel({
          data: payload,
        });

        interventionsList.value.unshift(saved);
        interventionNotes.value = '';
        saveSuccess.value = true;
        emit('interventionUpdated');

        setTimeout(() => {
          saveSuccess.value = false;
        }, 4000);
      } catch (err) {
        console.error('Failed to save intervention', err);
      } finally {
        submittingIntervention.value = false;
      }
    }

    async function updateInterventionStatus(itv, newStatus) {
      try {
        const updated = await LearnerInterventionResource.saveModel({
          id: itv.id,
          data: { status: newStatus },
          exists: true,
        });
        itv.status = newStatus;
        emit('interventionUpdated');
      } catch (err) {
        console.error('Failed to update intervention status', err);
      }
    }

    function exportDorpCSV() {
      const l = props.learner;
      const headers = [
        'Student ID',
        'Full Name',
        'Username',
        'Classroom',
        'Risk Level',
        'Risk Score',
        'Attendance Rate (%)',
        'Attended Sessions',
        'Total Sessions',
        'Quiz Average (%)',
        'Missing Tasks',
        'Last Active',
        'Interventions Count',
        'Latest Intervention',
        'Intervention Notes',
      ];

      const latestItv = interventionsList.value[0] || {};
      const row = [
        `"${l.id}"`,
        `"${l.name}"`,
        `"${l.username}"`,
        `"${props.className}"`,
        `"${l.risk_level.toUpperCase()}"`,
        `"${l.risk_score || 0}"`,
        `"${l.attendance_rate !== null ? l.attendance_rate : 'N/A'}"`,
        `"${l.attendance_present || 0}"`,
        `"${l.attendance_total || 0}"`,
        `"${l.quiz_average !== null ? l.quiz_average : 'N/A'}"`,
        `"${l.missing_assignments || 0}"`,
        `"${l.last_active || 'None'}"`,
        `"${interventionsList.value.length}"`,
        `"${latestItv.intervention_type || 'None'}"`,
        `"${(latestItv.notes || '').replace(/"/g, '""')}"`,
      ];

      const csvContent = '\uFEFF' + [headers.join(','), row.join(',')].join('\r\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute(
        'download',
        `DepEd_DORP_Intervention_${l.username}_${new Date().toISOString().slice(0, 10)}.csv`,
      );
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    function handlePrintReport() {
      window.print();
    }

    return {
      selectedType,
      selectedStatus,
      interventionNotes,
      submittingIntervention,
      saveSuccess,
      interventionsList,
      typeOptions,
      statusOptions,
      getInitials,
      riskLevelLabel$,
      isInactive,
      formatLastActive,
      formatDate,
      formatInterventionType,
      formatStatus,
      handleStartChat,
      handleSubmitIntervention,
      updateInterventionStatus,
      exportDorpCSV,
      handlePrintReport,
      ...strings,
    };
  },
};
</script>

<style lang="scss" scoped>
.ews-modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 75vh;
  overflow-y: auto;
  padding: 4px;
}

.learner-summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-radius: 8px;
  flex-wrap: wrap;
  gap: 12px;
}

.learner-identity {
  display: flex;
  align-items: center;
  gap: 12px;
}

.learner-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #2563eb;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
}

.learner-name {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.learner-username {
  font-size: 13px;
}

.header-badges {
  display: flex;
  align-items: center;
  gap: 8px;
}

.risk-badge {
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  text-transform: uppercase;
}

.risk-high {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #f87171;
}

.risk-moderate {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fcd34d;
}

.risk-low {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
}

.risk-score-pill {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
  background: #f3f4f6;
  color: #374151;
}

.quick-toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.diagnostic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.diag-card {
  padding: 12px 14px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-flagged {
  border-color: #f87171 !important;
  background: #fff5f5 !important;
}

.diag-header {
  display: flex;
  align-items: center;
  gap: 6px;
}

.diag-icon {
  font-size: 14px;
}

.diag-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.diag-val {
  font-size: 22px;
  font-weight: 800;
  margin: 2px 0;
}

.diag-sub {
  font-size: 11px;
}

.risk-factors-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}

.triggers-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trigger-item {
  padding: 10px 14px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.trigger-high {
  background: #fef2f2;
  border-left: 4px solid #dc2626;
}

.trigger-moderate {
  background: #fffbeb;
  border-left: 4px solid #f59e0b;
}

.trigger-label {
  font-size: 13px;
  font-weight: 700;
  color: #1f2937;
}

.trigger-detail {
  font-size: 12px;
  color: #4b5563;
}

.intervention-form-container {
  padding: 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.form-submit-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
}

.save-success-tag {
  color: #16a34a;
  font-weight: 700;
  font-size: 13px;
}

.intervention-history-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.no-history-text {
  font-size: 13px;
  margin: 4px 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-card {
  padding: 12px 14px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-type-badge {
  font-size: 12px;
  font-weight: 700;
  color: #1e3a8a;
  background: #dbeafe;
  padding: 2px 8px;
  border-radius: 4px;
}

.history-status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-in_progress {
  background: #e0f2fe;
  color: #0369a1;
}

.status-resolved {
  background: #dcfce7;
  color: #15803d;
}

.history-date {
  font-size: 11px;
}

.history-notes {
  margin: 0;
  font-size: 13px;
  font-style: italic;
  white-space: pre-wrap;
}

.history-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.status-btn {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn-resolve {
  background: #dcfce7;
  color: #166534;
  border-color: #86efac;
}

.btn-progress {
  background: #e0f2fe;
  color: #0284c7;
  border-color: #7dd3fc;
}

.btn-reopen {
  background: #f3f4f6;
  color: #4b5563;
  border-color: #d1d5db;
}

@media print {
  .quick-toolbar,
  .intervention-form-container,
  .history-actions {
    display: none !important;
  }
}
</style>
