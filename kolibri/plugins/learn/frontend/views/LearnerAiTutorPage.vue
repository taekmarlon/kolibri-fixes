<template>
  <LearnAppBarPage
    :appBarTitle="learnString('learnLabel')"
    :loading="pageLoading"
  >
    <div role="main" class="ai-tutor-page">
      <div class="ai-tutor-header" :style="{ backgroundColor: $themeTokens.surface, border: `1px solid ${$themeTokens.fineLine}` }">
        <div class="header-left">
          <div class="avatar-icon" :style="{ backgroundColor: $themeTokens.primary, color: '#ffffff' }">
            <KIcon icon="practice" />
          </div>
          <div>
            <h1 class="header-title" :style="{ color: $themeTokens.text }">
              {{ aiTutorTitle$() }}
            </h1>
            <p class="header-subtitle" :style="{ color: $themeTokens.annotation }">
              {{ aiTutorSubtitle$() }}
            </p>
          </div>
        </div>
        <div class="header-right">
          <KButton
            v-if="messages.length > 0"
            :text="clearChatLabel$()"
            appearance="basic-link"
            :style="{ color: $themeTokens.annotation }"
            @click="clearChat"
          />
        </div>
      </div>

      <!-- Chat Container -->
      <div class="chat-container" :style="{ backgroundColor: $themeTokens.surface, border: `1px solid ${$themeTokens.fineLine}` }">
        <!-- Quick Starter Prompts -->
        <div v-if="messages.length === 0" class="starter-section">
          <div class="welcome-box">
            <h2 class="welcome-title" :style="{ color: $themeTokens.text }">
              {{ howCanIHelp$() }}
            </h2>
            <p class="welcome-desc" :style="{ color: $themeTokens.annotation }">
              {{ welcomeDesc$() }}
            </p>
          </div>

          <div class="prompt-chips-grid">
            <button
              v-for="(prompt, idx) in starterPrompts"
              :key="idx"
              class="prompt-chip"
              :style="{
                backgroundColor: $themePalette.grey.v_100,
                borderColor: $themeTokens.fineLine,
                color: $themeTokens.text,
              }"
              @click="selectPrompt(prompt)"
            >
              <span class="chip-icon">{{ prompt.icon }}</span>
              <span class="chip-text">{{ prompt.text }}</span>
            </button>
          </div>
        </div>

        <!-- Message List -->
        <div v-else ref="chatScrollArea" class="messages-list">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="message-row"
            :class="msg.role === 'user' ? 'user-row' : 'assistant-row'"
          >
            <div
              class="message-bubble"
              :style="msg.role === 'user'
                ? { backgroundColor: $themeTokens.primary, color: '#ffffff' }
                : { backgroundColor: $themePalette.grey.v_100, color: $themeTokens.text, border: `1px solid ${$themeTokens.fineLine}` }"
            >
              <div v-if="msg.role === 'assistant'" class="bubble-header" :style="{ color: $themeTokens.annotation }">
                <KIcon icon="practice" class="assistant-badge-icon" />
                <span>{{ tutorName$() }}</span>
              </div>
              <div class="message-content" style="white-space: pre-wrap;">{{ msg.content }}</div>
            </div>
          </div>

          <!-- Loading Indicator -->
          <div v-if="isLoading" class="message-row assistant-row">
            <div
              class="message-bubble loading-bubble"
              :style="{ backgroundColor: $themePalette.grey.v_100, border: `1px solid ${$themeTokens.fineLine}` }"
            >
              <KCircularLoader size="small" />
              <span :style="{ marginLeft: '8px', color: $themeTokens.annotation }">{{ thinkingLabel$() }}</span>
            </div>
          </div>
        </div>

        <!-- Input Bar -->
        <div class="input-bar" :style="{ borderTop: `1px solid ${$themeTokens.fineLine}` }">
          <textarea
            v-model="inputQuery"
            class="chat-textarea"
            rows="2"
            :placeholder="inputPlaceholder$()"
            :style="{
              color: $themeTokens.text,
              backgroundColor: $themeTokens.surface,
              borderColor: $themeTokens.fineLine,
            }"
            @keydown.enter.exact.prevent="handleSend"
          ></textarea>
          <KButton
            :text="sendButtonLabel$()"
            :primary="true"
            appearance="raised-button"
            :disabled="!inputQuery.trim() || isLoading"
            class="send-btn"
            @click="handleSend"
          />
        </div>
      </div>
    </div>
  </LearnAppBarPage>
</template>

<script>
  import { ref, nextTick } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import useAiTutor from 'kolibri-common/composables/useAiTutor';
  import commonLearnStrings from './commonLearnStrings';
  import LearnAppBarPage from './LearnAppBarPage';

  const aiTutorStrings = createTranslator('LearnerAiTutorPageStrings', {
    aiTutorTitle: {
      message: 'AI Personal Tutor',
      context: 'Title of the AI Personal Tutor page for learners',
    },
    aiTutorSubtitle: {
      message: 'Your 24/7 personal study buddy for math, science, reading, and problem solving',
      context: 'Subtitle of the AI Personal Tutor page',
    },
    howCanIHelp: {
      message: 'What would you like to learn today?',
      context: 'Greeting header in the AI tutor view',
    },
    welcomeDesc: {
      message: 'Choose a topic below or type your question in the box to get step-by-step guidance.',
      context: 'Instruction text in the AI tutor view',
    },
    tutorName: {
      message: 'Kolibri AI Tutor',
      context: 'Name of the assistant badge',
    },
    thinkingLabel: {
      message: 'Thinking step-by-step...',
      context: 'Loading text while AI generates explanation',
    },
    inputPlaceholder: {
      message: 'Ask a question or paste a math problem (Press Enter to send)...',
      context: 'Placeholder in query input box',
    },
    sendButtonLabel: {
      message: 'Ask Tutor',
      context: 'Send button label',
    },
    clearChatLabel: {
      message: 'Clear Conversation',
      context: 'Clear conversation button label',
    },
  });

  export default {
    name: 'LearnerAiTutorPage',
    components: {
      LearnAppBarPage,
    },
    mixins: [commonLearnStrings],
    setup() {
      const {
        aiTutorTitle$,
        aiTutorSubtitle$,
        howCanIHelp$,
        welcomeDesc$,
        tutorName$,
        thinkingLabel$,
        inputPlaceholder$,
        sendButtonLabel$,
        clearChatLabel$,
      } = aiTutorStrings;

      const { isAiEnabled, messages, isLoading, sendChatMessage, clearChat } = useAiTutor();
      const inputQuery = ref('');
      const chatScrollArea = ref(null);

      const starterPrompts = [
        { icon: '📐', text: 'How do I solve quadratic equations using the formula?' },
        { icon: '🔬', text: 'Explain photosynthesis step-by-step in simple terms.' },
        { icon: '➕', text: 'Help me understand adding and subtracting fractions.' },
        { icon: '📝', text: 'Give me 3 practice problems on linear algebra with solutions.' },
        { icon: '🌍', text: 'Why do we have different seasons on Earth?' },
        { icon: '💡', text: 'How do Newton\'s three laws of motion work?' },
      ];

      function scrollToBottom() {
        nextTick(() => {
          if (chatScrollArea.value) {
            chatScrollArea.value.scrollTop = chatScrollArea.value.scrollHeight;
          }
        });
      }

      async function handleSend() {
        if (!inputQuery.value.trim() || isLoading.value) return;
        const text = inputQuery.value;
        inputQuery.value = '';
        scrollToBottom();
        await sendChatMessage(text);
        scrollToBottom();
      }

      function selectPrompt(prompt) {
        inputQuery.value = prompt.text;
        handleSend();
      }

      return {
        pageLoading,
        isAiEnabled,
        messages,
        isLoading,
        inputQuery,
        chatScrollArea,
        starterPrompts,
        handleSend,
        selectPrompt,
        clearChat,
        aiTutorTitle$,
        aiTutorSubtitle$,
        howCanIHelp$,
        welcomeDesc$,
        tutorName$,
        thinkingLabel$,
        inputPlaceholder$,
        sendButtonLabel$,
        clearChatLabel$,
      };
    },
  };
</script>

<style lang="scss" scoped>
  .ai-tutor-page {
    max-width: 960px;
    margin: 24px auto;
    padding: 0 16px;
  }

  .ai-tutor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-radius: 8px 8px 0 0;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .avatar-icon {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
  }

  .header-title {
    margin: 0;
    font-size: 20px;
    font-weight: 700;
  }

  .header-subtitle {
    margin: 4px 0 0;
    font-size: 13px;
  }

  .chat-container {
    display: flex;
    flex-direction: column;
    height: 600px;
    border-top: none;
    border-radius: 0 0 8px 8px;
    overflow: hidden;
  }

  .starter-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 32px 24px;
    text-align: center;
    overflow-y: auto;
  }

  .welcome-title {
    font-size: 22px;
    font-weight: 600;
    margin: 0 0 8px;
  }

  .welcome-desc {
    font-size: 14px;
    margin: 0 0 24px;
  }

  .prompt-chips-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 12px;
    width: 100%;
    max-width: 720px;
  }

  .prompt-chip {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 14px;
    border: 1px solid;
    border-radius: 8px;
    cursor: pointer;
    text-align: left;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    font-size: 13px;
    line-height: 1.4;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }
  }

  .chip-icon {
    font-size: 18px;
  }

  .messages-list {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .message-row {
    display: flex;
    width: 100%;

    &.user-row {
      justify-content: flex-end;
    }

    &.assistant-row {
      justify-content: flex-start;
    }
  }

  .message-bubble {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.5;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);

    &.loading-bubble {
      display: flex;
      align-items: center;
    }
  }

  .bubble-header {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 6px;
  }

  .assistant-badge-icon {
    font-size: 14px;
  }

  .input-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 18px;
  }

  .chat-textarea {
    flex: 1;
    border: 1px solid;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 14px;
    resize: none;
    font-family: inherit;
    outline: none;

    &:focus {
      border-color: #007bff;
    }
  }

  .send-btn {
    height: 44px;
  }
</style>
