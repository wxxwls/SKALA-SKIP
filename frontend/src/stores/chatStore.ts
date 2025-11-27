import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Message, ChatSession } from '@/types';

export const useChatStore = defineStore('chat', () => {
  // State
  const currentSessionId = ref<string>('');
  const messages = ref<Message[]>([]);
  const sessions = ref<ChatSession[]>([]);
  const isTyping = ref(false);

  // Getters
  const currentSession = computed(() =>
    sessions.value.find((s) => s.id === currentSessionId.value)
  );

  const hasMessages = computed(() => messages.value.length > 0);

  // Actions
  function loadSessions() {
    const sessionsData = localStorage.getItem('chatSessions');
    if (sessionsData) {
      sessions.value = JSON.parse(sessionsData);
    }
  }

  function loadSession(sessionId: string) {
    const session = sessions.value.find((s) => s.id === sessionId);
    if (session) {
      currentSessionId.value = sessionId;
      messages.value = [...session.messages];
      localStorage.setItem('currentChatSessionId', sessionId);
    }
  }

  function saveSession() {
    if (!currentSessionId.value || messages.value.length === 0) return;

    const firstUserMessage = messages.value.find((m) => m.type === 'user');
    const title = firstUserMessage
      ? firstUserMessage.text.slice(0, 40) + (firstUserMessage.text.length > 40 ? '...' : '')
      : 'New Chat';

    const sessionData: ChatSession = {
      id: currentSessionId.value,
      title,
      messages: [...messages.value],
      lastUpdated: Date.now()
    };

    const sessionIndex = sessions.value.findIndex((s) => s.id === currentSessionId.value);
    if (sessionIndex >= 0) {
      sessions.value[sessionIndex] = sessionData;
    } else {
      sessions.value.push(sessionData);
    }

    localStorage.setItem('chatSessions', JSON.stringify(sessions.value));
  }

  function createNewSession() {
    const newSessionId = `session_${Date.now()}`;
    currentSessionId.value = newSessionId;
    messages.value = [];
    localStorage.setItem('currentChatSessionId', newSessionId);
  }

  function deleteSession(sessionId: string) {
    sessions.value = sessions.value.filter((s) => s.id !== sessionId);
    localStorage.setItem('chatSessions', JSON.stringify(sessions.value));

    if (currentSessionId.value === sessionId) {
      if (sessions.value.length > 0) {
        loadSession(sessions.value[0].id);
      } else {
        createNewSession();
      }
    }
  }

  function addMessage(message: Message) {
    messages.value.push(message);
    saveSession();
  }

  function generateBotResponse(userInput: string): string {
    const lowerInput = userInput.toLowerCase();

    if (lowerInput.includes('안녕') || lowerInput.includes('hello') || lowerInput.includes('hi')) {
      return '안녕하세요! 저는 AI 어시스턴트입니다. 무엇을 도와드릴까요?';
    } else if (lowerInput.includes('이름')) {
      return '저는 AI Chat 어시스턴트입니다. 다양한 질문에 답변해드릴 수 있어요.';
    } else if (lowerInput.includes('날씨')) {
      return '죄송합니다. 실시간 날씨 정보는 제공할 수 없지만, 날씨 관련 일반적인 정보는 도와드릴 수 있습니다.';
    } else if (lowerInput.includes('esg') || lowerInput.includes('탄소')) {
      return 'ESG는 환경(Environmental), 사회(Social), 지배구조(Governance)의 약자로, 기업의 비재무적 성과를 측정하는 지표입니다. ESG 관련하여 구체적으로 어떤 부분이 궁금하신가요?';
    } else if (lowerInput.includes('도움') || lowerInput.includes('help')) {
      return '저는 다양한 주제에 대해 도움을 드릴 수 있습니다. ESG, 탄소 예측, 보고서 작성 등에 대해 질문해주세요!';
    } else {
      return `"${userInput}"에 대해 질문해주셨군요. 제가 도와드릴 수 있는 구체적인 내용이 있으신가요? ESG, 탄소 예측, 데이터 분석 등 다양한 주제로 대화를 나눌 수 있습니다.`;
    }
  }

  async function sendMessage(text: string) {
    if (!text.trim() || isTyping.value) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      text: text,
      timestamp: Date.now()
    };

    addMessage(userMessage);
    isTyping.value = true;

    // Simulate bot response delay
    await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 700));

    const botResponse = generateBotResponse(text);
    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'bot',
      text: botResponse,
      timestamp: Date.now()
    };

    addMessage(botMessage);
    isTyping.value = false;
  }

  function initializeChat() {
    loadSessions();
    const savedCurrentSession = localStorage.getItem('currentChatSessionId');

    if (savedCurrentSession) {
      loadSession(savedCurrentSession);
    } else {
      createNewSession();
    }
  }

  return {
    // State
    currentSessionId,
    messages,
    sessions,
    isTyping,
    // Getters
    currentSession,
    hasMessages,
    // Actions
    loadSessions,
    loadSession,
    saveSession,
    createNewSession,
    deleteSession,
    addMessage,
    sendMessage,
    initializeChat
  };
});
