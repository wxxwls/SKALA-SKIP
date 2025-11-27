<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue';
import { Pencil, ArrowRight } from 'lucide-vue-next';
import { useChatStore } from '@/stores';
import SuggestionCard from '@/components/SuggestionCard.vue';

// Store
const chatStore = useChatStore();

// Refs
const inputValue = ref('');
const messagesEndRef = ref<HTMLDivElement | null>(null);

// Methods
function formatTime(timestamp: number) {
  return new Date(timestamp).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
  nextTick(() => {
    messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' });
  });
}

async function handleSend() {
  if (!inputValue.value.trim() || chatStore.isTyping) return;

  const text = inputValue.value;
  inputValue.value = '';
  await chatStore.sendMessage(text);
}

function handleKeyPress(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}

// Lifecycle
onMounted(() => {
  chatStore.initializeChat();
});

// Watchers
watch([() => chatStore.messages, () => chatStore.isTyping], () => {
  scrollToBottom();
}, { deep: true });
</script>

<template>
  <div class="chat-container">
    <!-- Top Input Hint -->
    <div v-if="!chatStore.hasMessages" class="input-hint">
      <Pencil class="w-[18px] h-[18px]" />
      <span>공감된 내용을 말씀해주세요.</span>
    </div>

    <!-- Center Greeting -->
    <div v-if="!chatStore.hasMessages" class="greeting-section">
      <h1 class="greeting-title">안녕하세요.</h1>
      <div class="suggestion-cards">
        <SuggestionCard text="저렴한 ESG 관련 정보 예열할 방어 더 고체적인 단말을 생성해 보세요." />
        <SuggestionCard text="지금부지역 DB(이모 주곤 단말을 확인해 보세요. 타 기업치 비교해보세요." />
      </div>
    </div>

    <!-- Chat Messages Area -->
    <div v-if="chatStore.hasMessages" class="messages-area">
      <div
        v-for="message in chatStore.messages"
        :key="message.id"
        class="message-row"
        :class="{ 'message-row-user': message.type === 'user' }"
      >
        <!-- Bot Avatar -->
        <div v-if="message.type === 'bot'" class="avatar-container">
          <div class="bot-avatar">AI</div>
        </div>

        <!-- Message Content -->
        <div class="message-content" :class="{ 'message-content-user': message.type === 'user' }">
          <div class="message-header" :class="{ 'message-header-user': message.type === 'user' }">
            <span v-if="message.type === 'user'" class="message-time">
              {{ formatTime(message.timestamp) }}
            </span>
            <span class="message-sender">{{ message.type === 'bot' ? 'slothGPT' : 'You' }}</span>
            <span v-if="message.type === 'bot'" class="message-time">
              {{ formatTime(message.timestamp) }}
            </span>
          </div>
          <div class="message-bubble" :class="{ 'message-bubble-user': message.type === 'user' }">
            {{ message.text }}
          </div>
        </div>

        <!-- User Avatar -->
        <div v-if="message.type === 'user'" class="user-avatar">U</div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="chatStore.isTyping" class="message-row">
        <div class="avatar-container">
          <div class="bot-avatar">AI</div>
        </div>
        <div class="message-content">
          <div class="message-header">
            <span class="message-sender">slothGPT</span>
            <span class="message-time">{{ formatTime(Date.now()) }}</span>
          </div>
          <div class="typing-indicator">
            <div v-for="i in 3" :key="i" class="typing-dot" :style="{ animationDelay: `${(i - 1) * 150}ms` }" />
          </div>
        </div>
      </div>

      <div ref="messagesEndRef" />
    </div>

    <!-- Bottom Input Bar -->
    <div class="input-bar">
      <div class="input-wrapper">
        <input
          v-model="inputValue"
          type="text"
          placeholder="메시지를 입력하세요..."
          class="message-input"
          @keypress="handleKeyPress"
        />
        <button class="send-button" @click="handleSend">
          <span>Send</span>
          <ArrowRight class="w-4 h-4" :stroke-width="2" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-background);
  padding-right: 320px;
  position: relative;
}

/* Input Hint */
.input-hint {
  position: absolute;
  top: 136px;
  left: calc(50% - 160px);
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--color-text-muted);
}

.input-hint span {
  font-size: var(--font-size-md);
  letter-spacing: -0.1px;
}

/* Greeting Section */
.greeting-section {
  position: absolute;
  top: 50%;
  left: calc(50% - 160px);
  transform: translate(-50%, calc(-50% - 120px));
  display: flex;
  flex-direction: column;
  align-items: center;
}

.greeting-title {
  font-size: 40px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  line-height: 48px;
  letter-spacing: -0.8px;
  text-align: center;
}

.suggestion-cards {
  display: flex;
  gap: var(--spacing-md);
  margin-top: 52px;
}

/* Messages Area */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-xl) var(--spacing-2xl) 120px;
  max-width: 880px;
  margin: 0 auto;
  width: 100%;
}

.message-row {
  display: flex;
  gap: 12px;
  margin-bottom: var(--spacing-lg);
  align-items: flex-start;
}

.message-row-user {
  justify-content: flex-end;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.bot-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #ff9933, #ff7a00);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-surface);
  flex-shrink: 0;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 2px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-surface);
  flex-shrink: 0;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 75%;
}

.message-content-user {
  max-width: 70%;
  align-items: flex-end;
}

.message-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: 4px;
}

.message-header-user {
  justify-content: flex-end;
}

.message-sender {
  font-size: 13px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.message-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.message-bubble {
  padding: 14px 16px;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 13px;
  line-height: 1.7;
  border: 1px solid var(--color-border);
  white-space: pre-wrap;
  word-break: break-word;
}

.message-bubble-user {
  background: #f3f4f6;
  border: none;
}

/* Typing Indicator */
.typing-indicator {
  padding: 14px 16px;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-muted);
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(-25%);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}

/* Input Bar */
.input-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 320px;
  height: 96px;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  padding: var(--spacing-lg) var(--spacing-2xl);
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 880px;
  height: 48px;
  background: var(--color-surface);
  border: 1.5px solid #dfe1e6;
  border-radius: 24px;
  padding-left: 20px;
  padding-right: 136px;
  box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.03);
}

.message-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: var(--font-size-md);
  color: var(--color-text-primary);
}

.message-input::placeholder {
  color: var(--color-text-muted);
}

.send-button {
  position: absolute;
  right: 6px;
  width: 116px;
  height: 36px;
  background: var(--gradient-primary-hover);
  border-radius: 18px;
  border: none;
  box-shadow: 0px 2px 6px rgba(255, 122, 0, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.send-button:hover {
  box-shadow: var(--shadow-lg);
}

.send-button span {
  color: var(--color-surface);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  letter-spacing: 0.2px;
}

.send-button svg {
  color: var(--color-surface);
}
</style>
