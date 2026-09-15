<template>
  <KPageContainer
    v-if="isAiEnabled"
    class="ai-block"
    :style="{ border: `1px solid ${$themeTokens.fineLine}` }"
  >
    <div class="ai-block-header">
      <div class="header-left">
        <KIcon icon="practice" class="ai-icon" :style="{ color: $themeTokens.primary }" />
        <div>
          <h2 class="ai-title" :style="{ color: $themeTokens.text }">
            {{ aiAssistantTitle$() }}
          </h2>
          <p class="ai-subtitle" :style="{ color: $themeTokens.annotation }">
            {{ aiAssistantSubtitle$() }}
          </p>
        </div>
      </div>
      <SectionToggleButton
        :isExpanded="isExpanded"
        @click="toggleExpand"
      />
    </div>

    <transition name="section-collapse">
      <div v-show="isExpanded" class="ai-actions-row">
        <KButton
          :text="generateQuizBtn$()"
          :primary="true"
          appearance="raised-button"
          icon="quiz"
          class="action-btn"
          @click="showQuizModal = true"
        />
        <KButton
          :text="planLessonBtn$()"
          :primary="false"
          appearance="raised-button"
          icon="lesson"
          class="action-btn"
          @click="showLessonModal = true"
        />
      </div>
    </transition>

    <!-- Modals -->
    <AiQuizGeneratorModal
      v-if="showQuizModal"
      @close="showQuizModal = false"
    />
    <AiLessonGeneratorModal
      v-if="showLessonModal"
      @close="showLessonModal = false"
    />
  </KPageContainer>
</template>

<script>
  import { ref } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useAiTutor from 'kolibri-common/composables/useAiTutor';
  import SectionToggleButton from 'kolibri-common/components/SectionToggleButton';
  import useCollapsible from 'kolibri-common/composables/useCollapsible';
  import AiQuizGeneratorModal from '../../common/AiQuizGeneratorModal.vue';
  import AiLessonGeneratorModal from '../../common/AiLessonGeneratorModal.vue';

  const strings = createTranslator('AiAssistantBlockStrings', {
    aiAssistantTitle: {
      message: 'AI Teaching Assistant',
      context: 'Header for the AI Teaching Assistant block on Coach Home',
    },
    aiAssistantSubtitle: {
      message: 'Draft custom quizzes, practice problem sets, and full lesson plans in seconds with AI.',
      context: 'Subtitle for the AI Teaching Assistant block',
    },
    generateQuizBtn: {
      message: 'Generate Quiz with AI',
      context: 'Button to open AI quiz generator modal',
    },
    planLessonBtn: {
      message: 'Plan Lesson with AI',
      context: 'Button to open AI lesson generator modal',
    },
  });

  export default {
    name: 'AiAssistantBlock',
    components: {
      AiQuizGeneratorModal,
      AiLessonGeneratorModal,
      SectionToggleButton,
    },
    setup() {
      const { isExpanded, toggleExpand } = useCollapsible('coach_ai_assistant', true);
      const { aiAssistantTitle$, aiAssistantSubtitle$, generateQuizBtn$, planLessonBtn$ } = strings;
      const { isAiEnabled } = useAiTutor();
      const showQuizModal = ref(false);
      const showLessonModal = ref(false);

      return {
        isExpanded,
        toggleExpand,
        isAiEnabled,
        showQuizModal,
        showLessonModal,
        aiAssistantTitle$,
        aiAssistantSubtitle$,
        generateQuizBtn$,
        planLessonBtn$,
      };
    },
  };
</script>

<style lang="scss" scoped>
  .ai-block {
    margin-bottom: 24px;
    padding: 20px 24px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
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

  .ai-block-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .ai-icon {
    font-size: 32px;
  }

  .ai-title {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
  }

  .ai-subtitle {
    margin: 4px 0 0;
    font-size: 13px;
  }

  .ai-actions-row {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
  }

  .action-btn {
    min-width: 180px;
  }
</style>
