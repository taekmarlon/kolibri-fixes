<template>
  <LearnAppBarPage
    :appBarTitle="learnString('learnLabel')"
    :loading="pageLoading"
  >
    <div role="main" class="ai-tutor-hub">
      <!-- Top Grade & Companion Selection Bar -->
      <div class="tutor-top-bar" :style="{ backgroundColor: $themeTokens.surface, borderColor: $themeTokens.fineLine }">
        <!-- Grade Mode Selector Tabs -->
        <div class="grade-tabs-wrapper">
          <span class="bar-label" :style="{ color: $themeTokens.annotation }">Grade Level:</span>
          <div class="grade-pills">
            <button
              v-for="grade in gradeOptions"
              :key="grade.id"
              type="button"
              class="grade-pill-btn"
              :class="{ active: selectedGradeLevel === grade.id }"
              :style="selectedGradeLevel === grade.id
                ? { backgroundColor: grade.color, color: '#ffffff', borderColor: grade.color }
                : { color: $themeTokens.text, borderColor: $themeTokens.fineLine, backgroundColor: $themePalette.grey.v_100 }"
              @click="selectGrade(grade.id)"
            >
              <span class="pill-emoji">{{ grade.emoji }}</span>
              <span class="pill-name">{{ grade.name }}</span>
            </button>
          </div>
        </div>

        <!-- Companion Mascot Selector -->
        <div class="mascot-selector-wrapper">
          <span class="bar-label" :style="{ color: $themeTokens.annotation }">Mascot:</span>
          <div class="mascot-avatars">
            <button
              v-for="p in personaOptions"
              :key="p.id"
              type="button"
              class="mascot-btn"
              :class="{ active: selectedPersona === p.id }"
              :title="p.title"
              @click="selectedPersona = p.id"
            >
              <span class="mascot-icon">{{ p.emoji }}</span>
            </button>
          </div>
        </div>

        <!-- Star Rewards Counter -->
        <div class="stars-badge" :style="{ backgroundColor: '#fefce8', borderColor: '#fde047', color: '#854d0e' }">
          <span class="star-icon">⭐</span>
          <span class="star-count">{{ starsEarned }} Stars</span>
        </div>
      </div>

      <!-- Main Interactive Chat Card -->
      <div class="tutor-card-container" :style="{ backgroundColor: $themeTokens.surface, borderColor: $themeTokens.fineLine }">
        <!-- Companion Greeting Banner Header -->
        <div class="companion-header-banner" :style="{ background: currentThemeGradient, color: '#ffffff' }">
          <div class="companion-avatar-circle">
            <span class="avatar-big-emoji">{{ currentPersonaObj.emoji }}</span>
          </div>
          <div class="companion-meta">
            <div class="companion-name-row">
              <h1 class="companion-name">{{ currentPersonaObj.name }}</h1>
              <span class="companion-tag">{{ currentPersonaObj.role }}</span>
            </div>
            <p class="companion-quote">{{ currentPersonaObj.greeting }}</p>
          </div>
          <div class="header-actions">
            <button
              v-if="messages.length > 0"
              type="button"
              class="clear-convo-btn"
              @click="clearChat"
            >
              <span>🗑️ Clear</span>
            </button>
          </div>
        </div>

        <!-- Starter Exploration Prompts (when no messages yet) -->
        <div v-if="messages.length === 0" class="starter-hub-section">
          <div class="welcome-mascot-box">
            <div class="speech-bubble-welcome" :style="{ backgroundColor: $themePalette.grey.v_100, borderColor: $themeTokens.fineLine, color: $themeTokens.text }">
              <span class="welcome-sparkle">✨</span>
              <strong>{{ welcomePromptTitle }}</strong>
              <p :style="{ color: $themeTokens.annotation, margin: '4px 0 0 0' }">
                {{ welcomePromptSubtitle }}
              </p>
            </div>
          </div>

          <!-- Dynamic Prompts Grid according to grade level -->
          <div class="starter-grid">
            <button
              v-for="(prompt, idx) in currentGradePrompts"
              :key="idx"
              type="button"
              class="starter-card-btn"
              :style="{
                backgroundColor: $themePalette.grey.v_100,
                borderColor: $themeTokens.fineLine,
                color: $themeTokens.text,
              }"
              @click="askQuickPrompt(prompt.text)"
            >
              <div class="prompt-icon-badge" :style="{ backgroundColor: prompt.bg }">
                <span>{{ prompt.icon }}</span>
              </div>
              <div class="prompt-text-group">
                <span class="prompt-topic-tag" :style="{ color: $themeTokens.annotation }">{{ prompt.topic }}</span>
                <span class="prompt-main-text">{{ prompt.text }}</span>
              </div>
            </button>
          </div>
        </div>

        <!-- Messages History Stream -->
        <div v-else ref="chatScrollArea" class="chat-messages-stream">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="message-bubble-wrapper"
            :class="msg.role === 'user' ? 'user-bubble-wrapper' : 'assistant-bubble-wrapper'"
          >
            <!-- User message bubble -->
            <div
              v-if="msg.role === 'user'"
              class="user-speech-bubble"
              :style="{ backgroundColor: $themeTokens.primary, color: '#ffffff' }"
            >
              <div class="user-bubble-text">{{ msg.content }}</div>
            </div>

            <!-- AI Companion message card -->
            <div
              v-else
              class="assistant-response-card"
              :style="{
                backgroundColor: $themeTokens.surface,
                borderColor: $themeTokens.fineLine,
              }"
            >
              <div class="assistant-card-header" :style="{ borderBottom: `1px solid ${$themeTokens.fineLine}` }">
                <div class="assistant-identity">
                  <span class="assistant-mini-emoji">{{ currentPersonaObj.emoji }}</span>
                  <span class="assistant-name-label" :style="{ color: $themeTokens.text }">{{ currentPersonaObj.name }}</span>
                  <span class="grade-mode-badge" :style="{ backgroundColor: currentGradeObj.color, color: '#ffffff' }">
                    {{ currentGradeObj.name }}
                  </span>
                </div>
                <!-- Reward star button -->
                <button
                  type="button"
                  class="reward-star-btn"
                  :class="{ awarded: awardedMessages.includes(i) }"
                  @click="awardStar(i)"
                >
                  <span>{{ awardedMessages.includes(i) ? '⭐ Star Awarded!' : '⭐ Helpful?' }}</span>
                </button>
              </div>

              <!-- Rich Rendered Content (Math, Cards, Solutions, Steps) -->
              <div class="assistant-card-body">
                <AiMessageRenderer
                  :content="msg.content"
                  :gradeLevel="selectedGradeLevel"
                />
              </div>

              <!-- Quick Action Follow-Ups -->
              <div class="assistant-quick-followups" :style="{ borderTop: `1px solid ${$themeTokens.fineLine}` }">
                <span class="followup-label" :style="{ color: $themeTokens.annotation }">Next Step:</span>
                <button
                  v-for="(action, aIdx) in quickActionFollowups"
                  :key="aIdx"
                  type="button"
                  class="followup-chip-btn"
                  :style="{
                    backgroundColor: $themePalette.grey.v_100,
                    borderColor: $themeTokens.fineLine,
                    color: $themeTokens.text,
                  }"
                  @click="askQuickPrompt(action.prompt)"
                >
                  <span>{{ action.icon }}</span>
                  <span>{{ action.label }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Thinking / Generating Animation Bubble -->
          <div v-if="isLoading" class="assistant-bubble-wrapper">
            <div class="assistant-response-card thinking-card" :style="{ backgroundColor: $themePalette.grey.v_100, borderColor: $themeTokens.fineLine }">
              <div class="thinking-content">
                <span class="thinking-mascot-anim">{{ currentPersonaObj.emoji }}</span>
                <KCircularLoader size="small" />
                <span class="thinking-text" :style="{ color: $themeTokens.text }">
                  {{ currentPersonaObj.name }} is thinking and writing step-by-step...
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Input Bar & Quick Helper Chips -->
        <div class="tutor-input-dock" :style="{ borderTop: `1px solid ${$themeTokens.fineLine}`, backgroundColor: $themeTokens.surface }">
          <!-- Quick Action Helper Chips Row -->
          <div class="quick-chips-dock">
            <button
              v-for="(chip, cIdx) in quickHelperChips"
              :key="cIdx"
              type="button"
              class="helper-chip"
              :style="{
                backgroundColor: $themePalette.grey.v_100,
                borderColor: $themeTokens.fineLine,
                color: $themeTokens.text,
              }"
              @click="appendHelperQuery(chip.template)"
            >
              <span>{{ chip.icon }}</span>
              <span>{{ chip.label }}</span>
            </button>
          </div>

          <!-- Textarea Input and Send Button -->
          <div class="input-action-row">
            <textarea
              v-model="inputQuery"
              class="tutor-textarea"
              rows="2"
              :placeholder="dynamicPlaceholder"
              :style="{
                color: $themeTokens.text,
                backgroundColor: $themeTokens.surface,
                borderColor: $themeTokens.fineLine,
              }"
              @keydown.enter.exact.prevent="handleSend"
            ></textarea>
            <KButton
              :text="sendButtonText"
              :primary="true"
              appearance="raised-button"
              :disabled="!inputQuery.trim() || isLoading"
              class="tutor-send-btn"
              @click="handleSend"
            />
          </div>
        </div>
      </div>
    </div>
  </LearnAppBarPage>
</template>

<script>
  import { ref, computed, nextTick } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import useAiTutor from 'kolibri-common/composables/useAiTutor';
  import AiMessageRenderer from 'kolibri-common/components/AiMessageRenderer';
  import commonLearnStrings from './commonLearnStrings';
  import LearnAppBarPage from './LearnAppBarPage';

  const aiTutorStrings = createTranslator('LearnerAiTutorPageStrings', {
    aiTutorTitle: {
      message: 'AI Personal Tutor',
      context: 'Title of the AI Personal Tutor page for learners',
    },
    sendButtonLabel: {
      message: 'Ask Tutor',
      context: 'Button label to send chat query',
    },
  });

  export default {
    name: 'LearnerAiTutorPage',
    components: {
      AiMessageRenderer,
      LearnAppBarPage,
    },
    mixins: [commonLearnStrings],
    setup() {
      const {
        messages,
        isLoading,
        sendChatMessage,
        clearChat,
        selectedGradeLevel,
        selectedPersona,
      } = useAiTutor();

      const inputQuery = ref('');
      const chatScrollArea = ref(null);
      const starsEarned = ref(5);
      const awardedMessages = ref([]);

      const gradeOptions = [
        { id: 'pre_elementary', name: 'Pre-Elementary (Ages 4-7)', emoji: '🧸', color: '#ec4899' },
        { id: 'elementary', name: 'Elementary (Grades 1-5)', emoji: '🚀', color: '#3b82f6' },
        { id: 'secondary', name: 'Secondary (Grades 6-12)', emoji: '🎓', color: '#8b5cf6' },
      ];

      const personaOptions = [
        {
          id: 'owl',
          name: 'Koli the Owl',
          emoji: '🦉',
          role: 'Patient & Wise Guide',
          greeting: 'Hoo-hoo! Let’s explore and learn something wonderful together today!',
          title: 'Koli the Owl',
          gradient: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
        },
        {
          id: 'robot',
          name: 'Sparky the Robot',
          emoji: '🤖',
          role: 'Fun Tech Buddy',
          greeting: 'Beep boop! Ready to compute fun answers and solve problems with you!',
          title: 'Sparky the Robot',
          gradient: 'linear-gradient(135deg, #10b981 0%, #047857 100%)',
        },
        {
          id: 'astronaut',
          name: 'Nova the Astronaut',
          emoji: '🚀',
          role: 'Space & Science Explorer',
          greeting: 'Blast off! No question is too big for our space mission!',
          title: 'Nova the Astronaut',
          gradient: 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
        },
        {
          id: 'wizard',
          name: 'Merlin the Math Wizard',
          emoji: '🧙',
          role: 'Logic & Formula Sage',
          greeting: 'Abracadabra! Let us unlock the secrets of math and science!',
          title: 'Merlin the Wizard',
          gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        },
      ];

      const currentPersonaObj = computed(() => {
        return personaOptions.find(p => p.id === selectedPersona.value) || personaOptions[0];
      });

      const currentGradeObj = computed(() => {
        return gradeOptions.find(g => g.id === selectedGradeLevel.value) || gradeOptions[1];
      });

      const currentThemeGradient = computed(() => {
        return currentPersonaObj.value.gradient;
      });

      const preElemPrompts = [
        { icon: '🐱', topic: 'Animal Stories', text: 'Tell me a fun counting story about 5 playful kittens', bg: '#ec4899' },
        { icon: '🍎', topic: 'Nature & Food', text: 'Why do apples grow on trees and why are they crunchy?', bg: '#f43f5e' },
        { icon: '🎨', topic: 'Colors & Art', text: 'What magical colors do we get when we mix blue and yellow?', bg: '#8b5cf6' },
        { icon: '🌟', topic: 'Space & Sky', text: 'Where does the Sun go when we go to sleep at night?', bg: '#eab308' },
      ];

      const elementaryPrompts = [
        { icon: '🍕', topic: 'Fractions', text: 'Explain how 1/2 and 3/4 fractions work using a pepperoni pizza', bg: '#f97316' },
        { icon: '🚀', topic: 'Space Science', text: 'How do rocket engines push spacecraft into Earth orbit?', bg: '#3b82f6' },
        { icon: '🦖', topic: 'History & Earth', text: 'What happened to the dinosaurs and how did they live?', bg: '#10b981' },
        { icon: '🎮', topic: 'Multiplication', text: 'Show me how to multiply 345 × 12 with easy step-by-step boxes', bg: '#8b5cf6' },
      ];

      const secondaryPrompts = [
        { icon: '📐', topic: 'Linear Algebra', text: 'Show me how to multiply two 2x2 matrices with step-by-step equations', bg: '#3b82f6' },
        { icon: '⚛️', topic: 'Physics', text: 'Explain Newton’s Three Laws of Motion with physics formula derivations', bg: '#6366f1' },
        { icon: '🧬', topic: 'Biology', text: 'Explain DNA transcription, translation, and mRNA protein synthesis', bg: '#10b981' },
        { icon: '📊', topic: 'Algebra', text: 'Derive the quadratic formula x = (-b ± √(b² - 4ac)) / 2a from scratch', bg: '#8b5cf6' },
      ];

      const currentGradePrompts = computed(() => {
        if (selectedGradeLevel.value === 'pre_elementary') return preElemPrompts;
        if (selectedGradeLevel.value === 'secondary') return secondaryPrompts;
        return elementaryPrompts;
      });

      const welcomePromptTitle = computed(() => {
        if (selectedGradeLevel.value === 'pre_elementary') return 'Hi little explorer! What fun question do you have? 🎈';
        if (selectedGradeLevel.value === 'secondary') return 'Welcome, Scholar! What concept or derivation are we mastering today? 🎓';
        return 'Ready for your learning quest? Ask any math, science, or reading question! 🚀';
      });

      const welcomePromptSubtitle = computed(() => {
        if (selectedGradeLevel.value === 'pre_elementary') return 'Pick a story below or type anything you want to know!';
        if (selectedGradeLevel.value === 'secondary') return 'Enter equations, physics questions, or paste a practice problem for step derivations.';
        return 'Choose a popular topic below or type your homework problem to get step-by-step help.';
      });

      const dynamicPlaceholder = computed(() => {
        if (selectedGradeLevel.value === 'pre_elementary') return 'Type or ask anything (e.g., Why is the sky blue?)...';
        if (selectedGradeLevel.value === 'secondary') return 'Ask a question, enter a formula, or paste a problem...';
        return 'Ask a homework problem or paste a question (Press Enter to send)...';
      });

      const quickHelperChips = [
        { icon: '🧩', label: 'Explain like I’m 5', template: 'Can you explain this in the simplest way possible with a fun analogy?' },
        { icon: '🎨', label: 'Draw an Emoji Diagram', template: 'Can you show this using a visual emoji picture diagram?' },
        { icon: '🔍', label: 'Give me a hint', template: 'Don’t give me the full answer yet, just give me a helpful hint!' },
        { icon: '🪜', label: 'Step-by-Step Breakdown', template: 'Can you break this down into Step 1, Step 2, and Step 3?' },
        { icon: '🏆', label: 'Quiz me on this!', template: 'Can you give me 1 fun practice question to test if I understood this?' },
      ];

      const quickActionFollowups = [
        { icon: '🔍', label: 'Give me a hint', prompt: 'Can you give me a hint for the next step?' },
        { icon: '📝', label: 'Another example', prompt: 'Can you give me another example problem to practice?' },
        { icon: '🏆', label: 'Quiz me!', prompt: 'Quiz me on this topic with 1 practice question!' },
      ];

      function selectGrade(gradeId) {
        selectedGradeLevel.value = gradeId;
      }

      function appendHelperQuery(template) {
        if (inputQuery.value.trim()) {
          inputQuery.value += ` (${template})`;
        } else {
          inputQuery.value = template;
        }
      }

      function askQuickPrompt(promptText) {
        inputQuery.value = promptText;
        handleSend();
      }

      function awardStar(messageIdx) {
        if (!awardedMessages.value.includes(messageIdx)) {
          awardedMessages.value.push(messageIdx);
          starsEarned.value += 1;
        }
      }

      async function handleSend() {
        if (!inputQuery.value.trim() || isLoading.value) return;
        const text = inputQuery.value;
        inputQuery.value = '';
        await sendChatMessage(text);
        await nextTick();
        if (chatScrollArea.value) {
          chatScrollArea.value.scrollTop = chatScrollArea.value.scrollHeight;
        }
      }

      return {
        pageLoading,
        messages,
        isLoading,
        inputQuery,
        chatScrollArea,
        starsEarned,
        awardedMessages,
        selectedGradeLevel,
        selectedPersona,
        gradeOptions,
        personaOptions,
        currentPersonaObj,
        currentGradeObj,
        currentThemeGradient,
        currentGradePrompts,
        welcomePromptTitle,
        welcomePromptSubtitle,
        dynamicPlaceholder,
        quickHelperChips,
        quickActionFollowups,
        sendButtonText: aiTutorStrings.sendButtonLabel$(),
        selectGrade,
        appendHelperQuery,
        askQuickPrompt,
        awardStar,
        handleSend,
        clearChat,
      };
    },
  };
</script>

<style lang="scss" scoped>
  .ai-tutor-hub {
    max-width: 1040px;
    margin: 0 auto;
    padding: 16px 12px 32px;
    font-family: inherit;
  }

  .tutor-top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px 18px;
    border-radius: 12px;
    border: 1px solid;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);

    .bar-label {
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-right: 8px;
    }

    .grade-tabs-wrapper {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 6px;

      .grade-pills {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;

        .grade-pill-btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border-radius: 20px;
          border: 1px solid;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;

          &:hover {
            transform: translateY(-1px);
          }

          &.active {
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
          }
        }
      }
    }

    .mascot-selector-wrapper {
      display: flex;
      align-items: center;
      gap: 6px;

      .mascot-avatars {
        display: flex;
        gap: 6px;

        .mascot-btn {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          border: 2px solid transparent;
          background-color: rgba(0, 0, 0, 0.04);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          transition: transform 0.15s ease;

          &:hover {
            transform: scale(1.15);
          }

          &.active {
            border-color: #3b82f6;
            background-color: #eff6ff;
            transform: scale(1.1);
          }
        }
      }
    }

    .stars-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 20px;
      border: 1px solid;
      font-weight: 700;
      font-size: 13px;
    }
  }

  .tutor-card-container {
    border: 1px solid;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
    display: flex;
    flex-direction: column;
    min-height: 540px;
  }

  .companion-header-banner {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 18px 24px;
    position: relative;

    .companion-avatar-circle {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.25);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    .companion-meta {
      flex: 1;

      .companion-name-row {
        display: flex;
        align-items: center;
        gap: 10px;

        .companion-name {
          margin: 0;
          font-size: 20px;
          font-weight: 800;
        }

        .companion-tag {
          font-size: 11.5px;
          background: rgba(255, 255, 255, 0.2);
          padding: 2px 8px;
          border-radius: 12px;
          font-weight: 600;
        }
      }

      .companion-quote {
        margin: 4px 0 0 0;
        font-size: 13.5px;
        opacity: 0.95;
      }
    }

    .clear-convo-btn {
      background: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.4);
      color: #ffffff;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s ease;

      &:hover {
        background: rgba(255, 255, 255, 0.35);
      }
    }
  }

  .starter-hub-section {
    padding: 28px 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;

    .welcome-mascot-box {
      .speech-bubble-welcome {
        border: 1px solid;
        border-radius: 12px;
        padding: 16px 20px;
        font-size: 15px;

        .welcome-sparkle {
          font-size: 18px;
          margin-right: 6px;
        }
      }
    }

    .starter-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;

      .starter-card-btn {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 14px 16px;
        border-radius: 12px;
        border: 1px solid;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        }

        .prompt-icon-badge {
          width: 36px;
          height: 36px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #ffffff;
          font-size: 20px;
          flex-shrink: 0;
        }

        .prompt-text-group {
          display: flex;
          flex-direction: column;
          gap: 3px;

          .prompt-topic-tag {
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
          }

          .prompt-main-text {
            font-size: 13px;
            font-weight: 600;
            line-height: 1.4;
          }
        }
      }
    }
  }

  .chat-messages-stream {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    max-height: 520px;
    display: flex;
    flex-direction: column;
    gap: 18px;

    .message-bubble-wrapper {
      display: flex;
      flex-direction: column;
      width: 100%;

      &.user-bubble-wrapper {
        align-items: flex-end;
      }

      &.assistant-bubble-wrapper {
        align-items: flex-start;
      }
    }

    .user-speech-bubble {
      max-width: 80%;
      padding: 12px 18px;
      border-radius: 18px 18px 4px 18px;
      font-size: 14.5px;
      font-weight: 500;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }

    .assistant-response-card {
      width: 100%;
      border: 1px solid;
      border-radius: 14px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
      overflow: hidden;

      .assistant-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 16px;

        .assistant-identity {
          display: flex;
          align-items: center;
          gap: 8px;

          .assistant-mini-emoji {
            font-size: 18px;
          }

          .assistant-name-label {
            font-weight: 700;
            font-size: 13.5px;
          }

          .grade-mode-badge {
            font-size: 10.5px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 10px;
          }
        }

        .reward-star-btn {
          background: none;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          padding: 3px 10px;
          font-size: 11.5px;
          font-weight: 600;
          cursor: pointer;
          color: #64748b;
          transition: all 0.2s ease;

          &:hover {
            border-color: #f59e0b;
            color: #b45309;
          }

          &.awarded {
            background-color: #fefce8;
            border-color: #fde047;
            color: #854d0e;
            font-weight: bold;
          }
        }
      }

      .assistant-card-body {
        padding: 16px 20px;
      }

      .assistant-quick-followups {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        padding: 10px 16px;
        background-color: rgba(0, 0, 0, 0.015);

        .followup-label {
          font-size: 11.5px;
          font-weight: 700;
          text-transform: uppercase;
        }

        .followup-chip-btn {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          padding: 4px 10px;
          border-radius: 14px;
          border: 1px solid;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.15s ease;

          &:hover {
            transform: translateY(-1px);
          }
        }
      }
    }

    .thinking-card {
      padding: 16px 20px;

      .thinking-content {
        display: flex;
        align-items: center;
        gap: 12px;

        .thinking-mascot-anim {
          font-size: 26px;
          animation: mascot-bounce 1.2s infinite ease-in-out;
        }

        .thinking-text {
          font-size: 14px;
          font-weight: 600;
        }
      }
    }
  }

  .tutor-input-dock {
    padding: 14px 18px;
    display: flex;
    flex-direction: column;
    gap: 10px;

    .quick-chips-dock {
      display: flex;
      align-items: center;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 2px;

      .helper-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 5px 11px;
        border-radius: 16px;
        border: 1px solid;
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
        cursor: pointer;
        transition: all 0.15s ease;

        &:hover {
          transform: translateY(-1px);
        }
      }
    }

    .input-action-row {
      display: flex;
      align-items: flex-end;
      gap: 12px;

      .tutor-textarea {
        flex: 1;
        border: 1px solid;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 14px;
        resize: none;
        outline: none;
        box-sizing: border-box;
      }

      .tutor-send-btn {
        margin-bottom: 2px;
        font-weight: 700;
      }
    }
  }

  @keyframes mascot-bounce {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-6px);
    }
  }
</style>
