import { ref, computed } from 'vue';
import client from 'kolibri/client';
import urls from 'kolibri/urls';

// Global reactive state for AI enablement
const isAiEnabled = ref(false);
const aiProvider = ref('gemini');
const aiModelName = ref('');
const isCheckingStatus = ref(false);
const statusLoaded = ref(false);

async function checkAiStatus(force = false) {
  if (statusLoaded.value && !force) {
    return {
      enabled: isAiEnabled.value,
      provider: aiProvider.value,
      model_name: aiModelName.value,
    };
  }
  if (isCheckingStatus.value) {
    return { enabled: isAiEnabled.value };
  }
  isCheckingStatus.value = true;
  try {
    const response = await client({
      url: '/api/ai/status/',
      method: 'GET',
    });
    isAiEnabled.value = Boolean(response.data?.enabled);
    aiProvider.value = response.data?.provider || 'gemini';
    aiModelName.value = response.data?.model_name || '';
    statusLoaded.value = true;
    return response.data;
  } catch (err) {
    isAiEnabled.value = false;
    statusLoaded.value = true;
    return { enabled: false };
  } finally {
    isCheckingStatus.value = false;
  }
}

// Auto-run status check on script initialization
checkAiStatus();

export default function useAiTutor() {
  const messages = ref([]);
  const isLoading = ref(false);
  const errorMessage = ref('');

  if (!statusLoaded.value && !isCheckingStatus.value) {
    checkAiStatus();
  }

  async function sendChatMessage(userText, resourceContext = {}) {
    if (!userText || !userText.trim()) return;

    errorMessage.value = '';
    const userMessage = { role: 'user', content: userText.trim() };
    messages.value.push(userMessage);
    isLoading.value = true;

    try {
      const response = await client({
        url: '/api/ai/chat/',
        method: 'POST',
        data: {
          messages: messages.value,
          context: resourceContext,
        },
      });

      const replyContent = response.data?.response || 'No response from AI.';
      messages.value.push({
        role: 'assistant',
        content: replyContent,
      });
      return replyContent;
    } catch (err) {
      const errText = err.response?.data?.error || err.message || 'Failed to get response from AI.';
      errorMessage.value = errText;
      messages.value.push({
        role: 'assistant',
        content: `⚠️ Error: ${errText}`,
        isError: true,
      });
    } finally {
      isLoading.value = false;
    }
  }

  async function generateQuiz(params) {
    isLoading.value = true;
    errorMessage.value = '';
    try {
      const response = await client({
        url: '/api/ai/generate_quiz/',
        method: 'POST',
        data: params,
      });
      return response.data;
    } catch (err) {
      const errText = err.response?.data?.error || err.message || 'Quiz generation failed.';
      errorMessage.value = errText;
      throw new Error(errText);
    } finally {
      isLoading.value = false;
    }
  }

  async function generateLesson(params) {
    isLoading.value = true;
    errorMessage.value = '';
    try {
      const response = await client({
        url: '/api/ai/generate_lesson/',
        method: 'POST',
        data: params,
      });
      return response.data;
    } catch (err) {
      const errText = err.response?.data?.error || err.message || 'Lesson generation failed.';
      errorMessage.value = errText;
      throw new Error(errText);
    } finally {
      isLoading.value = false;
    }
  }

  async function testAiConnection(credentials) {
    try {
      const response = await client({
        url: '/api/ai/test_connection/',
        method: 'POST',
        data: credentials,
      });
      return response.data;
    } catch (err) {
      const errText = err.response?.data?.error || err.message || 'Connection test failed.';
      throw new Error(errText);
    }
  }

  function clearChat() {
    messages.value = [];
    errorMessage.value = '';
  }

  return {
    isAiEnabled: computed(() => isAiEnabled.value),
    aiProvider: computed(() => aiProvider.value),
    aiModelName: computed(() => aiModelName.value),
    isCheckingStatus: computed(() => isCheckingStatus.value),
    statusLoaded: computed(() => statusLoaded.value),
    messages,
    isLoading,
    errorMessage,
    checkAiStatus,
    sendChatMessage,
    generateQuiz,
    generateLesson,
    testAiConnection,
    clearChat,
  };
}
