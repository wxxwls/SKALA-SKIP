<template>
  <div
    class="w-full h-full flex flex-col"
    :style="{
      background: '#F7F8FA',
      paddingRight: '320px'
    }"
  >
    <!-- Top Input Hint -->
    <div
      v-if="messages.length === 0"
      class="absolute flex items-center justify-center gap-2"
      :style="{
        top: '136px',
        left: 'calc(50% - 160px)',
        transform: 'translateX(-50%)'
      }"
    >
      <Pencil
        class="w-[18px] h-[18px]"
        :style="{
          color: '#9CA3AF',
          strokeWidth: 1.5
        }"
      />
      <span
        class="text-[14px] tracking-[-0.1px]"
        :style="{ color: '#9CA3AF' }"
      >
        공감된 내용을 말씀해주요.
      </span>
    </div>

    <!-- Center Greeting -->
    <div
      v-if="messages.length === 0"
      class="absolute flex flex-col items-center"
      :style="{
        top: '50%',
        left: 'calc(50% - 160px)',
        transform: 'translate(-50%, calc(-50% - 120px))'
      }"
    >
      <h1
        class="text-center tracking-[-0.8px]"
        :style="{
          fontSize: '40px',
          fontWeight: 600,
          color: '#1A1F2E',
          lineHeight: '48px'
        }"
      >
        안녕하세요.
      </h1>

      <!-- Suggestion Cards -->
      <div
        class="flex gap-4"
        :style="{ marginTop: '52px' }"
      >
        <SuggestionCard text="저렴한 ESG 관련 정보 예열할 방어 더 고체적인 단말을 생성해 보세요." />
        <SuggestionCard text="지금부지역 DB(이모 주곤 단말을 확인해 보세요. 타 기업치 비교해보세요." />
      </div>
    </div>

    <!-- Chat Messages Area -->
    <div
      v-if="messages.length > 0"
      class="flex-1 overflow-y-auto"
      :style="{
        padding: '32px 48px 120px 48px',
        maxWidth: '880px',
        margin: '0 auto',
        width: '100%'
      }"
    >
      <div
        v-for="message in messages"
        :key="message.id"
        class="flex mb-6"
        :style="{
          justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
          gap: '12px',
          alignItems: 'flex-start'
        }"
      >
        <div v-if="message.type === 'bot'" class="flex flex-col items-center gap-1">
          <div
            class="flex-shrink-0"
            :style="{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #FF9933, #FF7A00)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '18px',
              fontWeight: 600,
              color: '#FFFFFF'
            }"
          >
            AI
          </div>
        </div>
        <div :style="{ display: 'flex', flexDirection: 'column', gap: '4px', maxWidth: message.type === 'user' ? '70%' : '75%' }">
          <div v-if="message.type === 'bot'" class="flex items-center gap-2" :style="{ marginBottom: '4px' }">
            <span :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E' }">slothGPT</span>
            <span :style="{ fontSize: '11px', color: '#9CA3AF' }">
              {{ formatTime(message.timestamp) }}
            </span>
          </div>
          <div v-if="message.type === 'user'" class="flex items-center justify-end gap-2" :style="{ marginBottom: '4px' }">
            <span :style="{ fontSize: '11px', color: '#9CA3AF' }">
              {{ formatTime(message.timestamp) }}
            </span>
            <span :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E' }">You</span>
          </div>
          <div
            :style="{
              padding: '14px 16px',
              borderRadius: '12px',
              background: message.type === 'user' ? '#F3F4F6' : '#FFFFFF',
              color: '#1A1F2E',
              fontSize: '13px',
              lineHeight: '1.7',
              border: message.type === 'bot' ? '1px solid #E8EAED' : 'none',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }"
          >
            {{ message.text }}
          </div>
        </div>
        <div
          v-if="message.type === 'user'"
          class="flex-shrink-0"
          :style="{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: '2px solid rgba(255,255,255,0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '14px',
            fontWeight: 600,
            color: '#FFFFFF'
          }"
        >
          U
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isTyping" class="flex mb-6" :style="{ gap: '12px', alignItems: 'flex-start' }">
        <div class="flex flex-col items-center gap-1">
          <div
            class="flex-shrink-0"
            :style="{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #FF9933, #FF7A00)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '18px',
              fontWeight: 600,
              color: '#FFFFFF'
            }"
          >
            AI
          </div>
        </div>
        <div :style="{ display: 'flex', flexDirection: 'column', gap: '4px' }">
          <div class="flex items-center gap-2" :style="{ marginBottom: '4px' }">
            <span :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E' }">slothGPT</span>
            <span :style="{ fontSize: '11px', color: '#9CA3AF' }">
              {{ formatTime(Date.now()) }}
            </span>
          </div>
          <div
            :style="{
              padding: '14px 16px',
              borderRadius: '12px',
              background: '#FFFFFF',
              border: '1px solid #E8EAED',
              display: 'flex',
              gap: '4px',
              alignItems: 'center'
            }"
          >
            <div
              v-for="i in 3"
              :key="i"
              class="animate-bounce"
              :style="{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#9CA3AF',
                animationDelay: `${(i - 1) * 150}ms`,
                animationDuration: '1s'
              }"
            />
          </div>
        </div>
      </div>

      <div ref="messagesEndRef" />
    </div>

    <!-- Bottom Input Bar -->
    <div
      class="absolute bottom-0 left-0 flex items-center justify-center"
      :style="{
        right: '320px',
        height: '96px',
        background: '#FFFFFF',
        borderTop: '1px solid #E8EAED',
        padding: '24px 48px'
      }"
    >
      <div
        class="relative flex items-center"
        :style="{
          width: '100%',
          maxWidth: '880px',
          height: '48px',
          background: '#FFFFFF',
          border: '1.5px solid #DFE1E6',
          borderRadius: '24px',
          paddingLeft: '20px',
          paddingRight: '136px',
          boxShadow: '0px 1px 2px rgba(0,0,0,0.03)'
        }"
      >
        <input
          v-model="inputValue"
          type="text"
          placeholder="메시지를 입력하세요..."
          class="flex-1 bg-transparent outline-none text-[14px]"
          :style="{ color: '#1A1F2E' }"
          @keypress="handleKeyPress"
        />

        <!-- Send Button -->
        <button
          class="absolute flex items-center justify-center gap-[6px] transition-all duration-200 hover:shadow-lg cursor-pointer"
          :style="{
            right: '6px',
            width: '116px',
            height: '36px',
            background: 'linear-gradient(120deg, #FF9933, #FF7A00)',
            borderRadius: '18px',
            border: 'none',
            boxShadow: '0px 2px 6px rgba(255,122,0,0.28)'
          }"
          @click="handleSend"
        >
          <span
            class="text-white tracking-[0.2px]"
            :style="{
              fontSize: '14px',
              fontWeight: 600
            }"
          >
            Send
          </span>
          <ArrowRight
            class="w-4 h-4 text-white"
            :stroke-width="2"
          />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { Pencil, ArrowRight } from 'lucide-vue-next'
import SuggestionCard from './SuggestionCard.vue'

interface Message {
  id: string
  type: 'user' | 'bot'
  text: string
  isTyping?: boolean
  timestamp: number
}

interface ChatSession {
  id: string
  title: string
  messages: Message[]
  lastUpdated: number
}

const currentSessionId = ref<string>('')
const messages = ref<Message[]>([])
const inputValue = ref('')
const isTyping = ref(false)
const messagesEndRef = ref<HTMLDivElement | null>(null)

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

const loadSession = (sessionId: string) => {
  const sessionsData = localStorage.getItem('chatSessions')
  if (sessionsData) {
    const sessions: ChatSession[] = JSON.parse(sessionsData)
    const session = sessions.find(s => s.id === sessionId)
    if (session) {
      currentSessionId.value = sessionId
      messages.value = session.messages
    }
  }
}

const saveSession = () => {
  const sessionsData = localStorage.getItem('chatSessions')
  const sessions: ChatSession[] = sessionsData ? JSON.parse(sessionsData) : []

  const firstUserMessage = messages.value.find(m => m.type === 'user')
  const title = firstUserMessage
    ? firstUserMessage.text.slice(0, 40) + (firstUserMessage.text.length > 40 ? '...' : '')
    : 'New Chat'

  const sessionIndex = sessions.findIndex(s => s.id === currentSessionId.value)
  const sessionData: ChatSession = {
    id: currentSessionId.value,
    title,
    messages: messages.value,
    lastUpdated: Date.now()
  }

  if (sessionIndex >= 0) {
    sessions[sessionIndex] = sessionData
  } else {
    sessions.push(sessionData)
  }

  localStorage.setItem('chatSessions', JSON.stringify(sessions))
}

const scrollToBottom = () => {
  nextTick(() => {
    messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' })
  })
}

const generateBotResponse = (userInput: string): string => {
  const lowerInput = userInput.toLowerCase()

  if (lowerInput.includes('안녕') || lowerInput.includes('hello') || lowerInput.includes('hi')) {
    return '안녕하세요! 저는 AI 어시스턴트입니다. 무엇을 도와드릴까요?'
  } else if (lowerInput.includes('이름')) {
    return '저는 AI Chat 어시스턴트입니다. 다양한 질문에 답변해드릴 수 있어요.'
  } else if (lowerInput.includes('날씨')) {
    return '죄송합니다. 실시간 날씨 정보는 제공할 수 없지만, 날씨 관련 일반적인 정보는 도와드릴 수 있습니다.'
  } else if (lowerInput.includes('esg') || lowerInput.includes('탄소')) {
    return 'ESG는 환경(Environmental), 사회(Social), 지배구조(Governance)의 약자로, 기업의 비재무적 성과를 측정하는 지표입니다. ESG 관련하여 구체적으로 어떤 부분이 궁금하신가요?'
  } else if (lowerInput.includes('도움') || lowerInput.includes('help')) {
    return '저는 다양한 주제에 대해 도움을 드릴 수 있습니다. ESG, 탄소 예측, 보고서 작성 등에 대해 질문해주세요!'
  } else {
    return `"${userInput}"에 대해 질문해주셨군요. 제가 도와드릴 수 있는 구체적인 내용이 있으신가요? ESG, 탄소 예측, 데이터 분석 등 다양한 주제로 대화를 나눌 수 있습니다.`
  }
}

const handleSend = () => {
  if (!inputValue.value.trim() || isTyping.value) return

  const userMessage: Message = {
    id: Date.now().toString(),
    type: 'user',
    text: inputValue.value,
    timestamp: Date.now()
  }

  const userInputText = inputValue.value
  messages.value.push(userMessage)
  inputValue.value = ''
  isTyping.value = true

  setTimeout(() => {
    const botResponse = generateBotResponse(userInputText)
    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'bot',
      text: botResponse,
      timestamp: Date.now()
    }
    messages.value.push(botMessage)
    isTyping.value = false
  }, 800 + Math.random() * 700)
}

const handleKeyPress = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

onMounted(() => {
  const savedCurrentSession = localStorage.getItem('currentChatSessionId')

  if (savedCurrentSession) {
    loadSession(savedCurrentSession)
  } else {
    const newSessionId = `session_${Date.now()}`
    currentSessionId.value = newSessionId
    localStorage.setItem('currentChatSessionId', newSessionId)
  }
})

watch([messages, isTyping], () => {
  scrollToBottom()
}, { deep: true })

watch(messages, () => {
  if (currentSessionId.value && messages.value.length > 0) {
    saveSession()
  }
}, { deep: true })
</script>
