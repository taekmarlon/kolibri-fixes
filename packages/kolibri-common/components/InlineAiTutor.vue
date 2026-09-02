<template>

  <div
    v-if="isAiEnabled"
    class="inline-ai-tutor-container"
    :style="{
      backgroundColor: $themeTokens.surface,
      border: `1px solid ${$themeTokens.fineLine}`,
    }"
  >
    <!-- Header Bar (Clickable to expand/collapse) -->
    <div
      class="tutor-header"
      :style="{
        backgroundColor: isExpanded ? $themePalette.grey.v_100 : $themeTokens.surface,
        borderBottom: isExpanded ? `1px solid ${$themeTokens.fineLine}` : 'none',
      }"
      @click="toggleExpand"
    >
      <div class="header-title-section">
        <span class="ai-badge" :style="{ backgroundColor: $themeTokens.primary, color: 'white' }">
          AI
        </span>
        <div class="title-text">
          <span class="main-title" :style="{ color: $themeTokens.text }">
            {{ tutorTitle$() }}
          </span>
          <span class="sub-title" :style="{ color: $themeTokens.annotation }">
            {{ tutorSubtitle$({ provider: formattedProviderName }) }}
          </span>
        </div>
      </div>

      <div class="header-actions">
        <KIconButton
          :icon="isExpanded ? 'chevronUp' : 'chevronDown'"
          :tooltip="isExpanded ? collapseLabel$() : expandLabel$()"
          @click.stop="toggleExpand"
        />
      </div>
    </div>

    <!-- Expanded Body -->
    <div v-show="isExpanded" class="tutor-body">
      <!-- Quick Prompt Chips -->
      <div class="quick-chips">
        <button
          v-for="chip in quickChips"
          :key="chip.text"
          class="chip-button"
          :style="{
            backgroundColor: $themePalette.grey.v_200,
            color: $themeTokens.text,
            borderColor: $themeTokens.fineLine,
          }"
          :disabled="isLoading"
          @click="sendQuickPrompt(chip.prompt)"
        >
          {{ chip.text }}
        </button>
      </div>

      <!-- Chat Messages Scroll Area -->
      <div ref="chatContainer" class="messages-container">
        <!-- Empty State -->
        <div v-if="!messages.length && !isLoading" class="empty-state">
          <KIcon icon="help" class="empty-icon" :style="{ color: $themeTokens.annotation }" />
          <p class="empty-text" :style="{ color: $themeTokens.annotation }">
            {{ emptyStateText$() }}
          </p>
        </div>

        <!-- Message List -->
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="message-wrapper"
          :class="msg.role === 'user' ? 'user-msg' : 'ai-msg'"
        >
          <div
            class="message-bubble"
            :style="
              msg.role === 'user'
                ? { backgroundColor: $themeTokens.primary, color: 'white' }
                : {
                  backgroundColor: $themePalette.grey.v_100,
                  color: $themeTokens.text,
                  border: `1px solid ${$themeTokens.fineLine}`,
                }
            "
          >
            <div class="message-role-label">
              {{ msg.role === 'user' ? youLabel$() : tutorLabel$() }}
            </div>
            <div class="message-content">
              {{ msg.content }}
            </div>
          </div>
        </div>

        <!-- Typing / Loading indicator -->
        <div v-if="isLoading" class="loading-bubble" :style="{ color: $themeTokens.annotation }">
          <KCircularLoader :delay="false" size="small" />
          <span>{{ thinking$() }}</span>
        </div>
      </div>

      <!-- Chat Input Bar -->
      <div class="input-bar" :style="{ borderTop: `1px solid ${$themeTokens.fineLine}` }">
        <input
          v-model="inputQuery"
          type="text"
          class="chat-input"
          :placeholder="inputPlaceholder$()"
          :style="{
            backgroundColor: $themeTokens.surface,
            color: $themeTokens.text,
            borderColor: $themeTokens.fineLine,
          }"
          :disabled="isLoading"
          @keydown.enter="submitMessage"
        />
        <KButton
          :text="sendLabel$()"
          :primary="true"
          appearance="raised-button"
          :disabled="!inputQuery.trim() || isLoading"
          @click="submitMessage"
        />
        <KIconButton
          v-if="messages.length"
          icon="clear"
          :tooltip="clearChatLabel$()"
          @click="clearChat"
        />
      </div>
    </div>
  </div>

</template>


<script>

  import { ref, computed, onMounted, nextTick } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useAiTutor from 'kolibri-common/composables/useAiTutor';

  const aiStrings = createTranslator('InlineAiTutorStrings', {
    tutorTitle: {
      message: 'AI Study Assistant',
      context: 'Title of the inline AI tutor widget',
    },
    tutorSubtitle: {
      message: 'Ask any question, get step-by-step hints, or simplify concepts ({provider})',
      context: 'Subtitle explaining what the AI tutor does',
    },
    expandLabel: {
      message: 'Expand AI Assistant',
      context: 'Tooltip to expand widget',
    },
    collapseLabel: {
      message: 'Collapse AI Assistant',
      context: 'Tooltip to collapse widget',
    },
    inputPlaceholder: {
      message: 'Ask a question about this lesson or exercise...',
      context: 'Placeholder text in chat input',
    },
    sendLabel: {
      message: 'Ask',
      context: 'Button label to send question to AI',
    },
    youLabel: {
      message: 'You',
      context: 'Label for student message bubble',
    },
    tutorLabel: {
      message: 'AI Assistant',
      context: 'Label for assistant message bubble',
    },
    thinking: {
      message: 'Thinking...',
      context: 'Loading text while AI generates response',
    },
    emptyStateText: {
      message: 'How can I help you with this topic? Click a suggestion above or type your question below.',
      context: 'Empty state greeting',
    },
    clearChatLabel: {
      message: 'Clear Chat',
      context: 'Tooltip to clear conversation',
    },
    hintChip: {
      message: '💡 Give me a hint',
      context: 'Quick chip to get a hint',
    },
    explainStepChip: {
      message: '🔍 Explain step-by-step',
      context: 'Quick chip to explain steps',
    },
    workedExampleChip: {
      message: '📝 Show an example',
      context: 'Quick chip to show an example',
    },
    simplifyChip: {
      message: '✨ Simplify explanation',
      context: 'Quick chip to simplify language',
    },
  });

  export default {
    name: 'InlineAiTutor',
    props: {
      resourceTitle: {
        type: String,
        default: '',
      },
      resourceDescription: {
        type: String,
        default: '',
      },
      resourceKind: {
        type: String,
        default: '',
      },
      currentQuestion: {
        type: String,
        default: '',
      },
    },
    setup(props) {
      const {
        isAiEnabled,
        aiProvider,
        messages,
        isLoading,
        checkAiStatus,
        sendChatMessage,
        clearChat,
      } = useAiTutor();

      const isExpanded = ref(true);
      const inputQuery = ref('');
      const chatContainer = ref(null);

      const {
        tutorTitle$,
        tutorSubtitle$,
        expandLabel$,
        collapseLabel$,
        inputPlaceholder$,
        sendLabel$,
        youLabel$,
        tutorLabel$,
        thinking$,
        emptyStateText$,
        clearChatLabel$,
        hintChip$,
        explainStepChip$,
        workedExampleChip$,
        simplifyChip$,
      } = aiStrings;

      const formattedProviderName = computed(() => {
        const p = aiProvider.value || 'gemini';
        if (p === 'gemini') return 'Google Gemini';
        if (p === 'deepseek') return 'DeepSeek';
        if (p === 'groq') return 'Llama 3 (Groq)';
        if (p === 'openai') return 'OpenAI';
        if (p === 'ollama') return 'Offline Ollama';
        if (p === 'huggingface') return 'Hugging Face';
        return 'AI';
      });

      const quickChips = computed(() => [
        {
          text: hintChip$(),
          prompt: 'Please give me a helpful hint to solve this problem without giving away the final answer immediately.',
        },
        {
          text: explainStepChip$(),
          prompt: 'Please explain step-by-step how to think through and solve this concept or question.',
        },
        {
          text: workedExampleChip$(),
          prompt: 'Can you show me a worked example similar to this problem?',
        },
        {
          text: simplifyChip$(),
          prompt: 'Can you explain this concept in simpler, beginner-friendly terms with an analogy?',
        },
      ]);

      const resourceContext = computed(() => ({
        title: props.resourceTitle,
        description: props.resourceDescription,
        kind: props.resourceKind,
        question: props.currentQuestion,
      }));

      function toggleExpand() {
        isExpanded.value = !isExpanded.value;
      }

      function scrollToBottom() {
        nextTick(() => {
          if (chatContainer.value) {
            chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
          }
        });
      }

      async function submitMessage() {
        if (!inputQuery.value.trim() || isLoading.value) return;
        const query = inputQuery.value;
        inputQuery.value = '';
        scrollToBottom();
        await sendChatMessage(query, resourceContext.value);
        scrollToBottom();
      }

      async function sendQuickPrompt(promptText) {
        if (isLoading.value) return;
        scrollToBottom();
        await sendChatMessage(promptText, resourceContext.value);
        scrollToBottom();
      }

      onMounted(() => {
        checkAiStatus();
      });

      return {
        isAiEnabled,
        isExpanded,
        inputQuery,
        chatContainer,
        messages,
        isLoading,
        formattedProviderName,
        quickChips,
        tutorTitle$,
        tutorSubtitle$,
        expandLabel$,
        collapseLabel$,
        inputPlaceholder$,
        sendLabel$,
        youLabel$,
        tutorLabel$,
        thinking$,
        emptyStateText$,
        clearChatLabel$,
        toggleExpand,
        submitMessage,
        sendQuickPrompt,
        clearChat,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .inline-ai-tutor-container {
    margin-top: 24px;
    margin-bottom: 24px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
    transition: all 0.2s ease;
  }

  .tutor-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    cursor: pointer;
    user-select: none;
  }

  .header-title-section {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .ai-badge {
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
    letter-spacing: 0.5px;
  }

  .title-text {
    display: flex;
    flex-direction: column;
  }

  .main-title {
    font-weight: bold;
    font-size: 1rem;
  }

  .sub-title {
    font-size: 0.8rem;
  }

  .tutor-body {
    padding: 16px;
  }

  .quick-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;
  }

  .chip-button {
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 0.82rem;
    cursor: pointer;
    border: 1px solid transparent;
    transition: background-color 0.15s;

    &:hover:not(:disabled) {
      opacity: 0.85;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .messages-container {
    max-height: 380px;
    min-height: 120px;
    overflow-y: auto;
    padding: 8px 4px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px 0;
    text-align: center;
  }

  .empty-icon {
    font-size: 32px;
    margin-bottom: 8px;
  }

  .empty-text {
    font-size: 0.9rem;
    max-width: 450px;
    margin: 0;
  }

  .message-wrapper {
    display: flex;
    width: 100%;

    &.user-msg {
      justify-content: flex-end;
    }

    &.ai-msg {
      justify-content: flex-start;
    }
  }

  .message-bubble {
    max-width: 85%;
    padding: 10px 14px;
    border-radius: 10px;
    word-break: break-word;
    line-height: 1.5;
  }

  .message-role-label {
    font-size: 0.75rem;
    font-weight: bold;
    margin-bottom: 4px;
    opacity: 0.85;
  }

  .message-content {
    font-size: 0.92rem;
    white-space: pre-wrap;
  }

  .loading-bubble {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    padding: 8px 0;
  }

  .input-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding-top: 12px;
    margin-top: 8px;
  }

  .chat-input {
    flex: 1;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.9rem;
    border: 1px solid;
    outline: none;

    &:focus {
      border-color: #2196f3;
    }
  }

</style>
