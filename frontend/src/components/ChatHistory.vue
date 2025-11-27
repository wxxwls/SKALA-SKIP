<template>
  <div
    class="h-full flex flex-col overflow-y-auto"
    :style="{
      width: '320px',
      padding: '20px 16px 20px 20px',
      background: 'linear-gradient(to bottom, #FF9933, #FF7A00)'
    }"
  >
    <!-- New Chat Button -->
    <button
      class="w-full mb-4 px-3 py-2 rounded-[8px] transition-all duration-200 hover:bg-white/30"
      :style="{
        background: 'rgba(255,255,255,0.2)',
        border: '1px solid rgba(255,255,255,0.3)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        cursor: 'pointer'
      }"
      @click="handleNewChat"
    >
      <Plus class="w-4 h-4 text-white" />
      <span class="text-white text-[13px]" :style="{ fontWeight: 600 }">
        New Chat
      </span>
    </button>

    <!-- Today Section -->
    <template v-if="todaySessions.length > 0">
      <div class="flex items-center justify-between h-[32px] w-full">
        <h3 class="text-white text-[15px] tracking-[-0.2px]" :style="{ fontWeight: 600 }">
          Today
        </h3>
        <div
          class="flex items-center gap-1 px-[10px] py-1 rounded-[12px] cursor-pointer"
          :style="{ background: 'rgba(255,255,255,0.15)' }"
        >
          <span class="text-white text-[12px]" :style="{ fontWeight: 500 }">
            {{ todaySessions.length }} Total
          </span>
          <ChevronDown class="w-3 h-3 text-white" />
        </div>
      </div>

      <div class="flex flex-col mt-3" :style="{ gap: '2px' }">
        <div
          v-for="session in todaySessions"
          :key="session.id"
          class="w-full h-[40px] px-3 py-[10px] rounded-[6px] cursor-pointer transition-all duration-200"
          :style="{
            background: currentSessionId === session.id ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.08)',
            opacity: currentSessionId === session.id ? 1 : 0.9
          }"
          @click="handleSessionClick(session.id)"
        >
          <p class="text-white text-[13px] leading-[20px] truncate">
            {{ session.title }}
          </p>
        </div>
      </div>
    </template>

    <!-- Previous 7 Days Section -->
    <template v-if="weekSessions.length > 0">
      <div :style="{ marginTop: '22px' }">
        <div class="flex items-center justify-between h-[32px] w-full">
          <h3 class="text-white text-[15px] tracking-[-0.2px]" :style="{ fontWeight: 600 }">
            Previous 7 Days
          </h3>
          <div
            class="flex items-center gap-1 px-[10px] py-1 rounded-[12px] cursor-pointer"
            :style="{ background: 'rgba(255,255,255,0.15)' }"
          >
            <span class="text-white text-[12px]" :style="{ fontWeight: 500 }">
              {{ weekSessions.length }}
            </span>
            <ChevronDown class="w-3 h-3 text-white" />
          </div>
        </div>
      </div>

      <div class="flex flex-col mt-3" :style="{ gap: '2px' }">
        <div
          v-for="session in weekSessions"
          :key="session.id"
          class="w-full h-[40px] px-3 py-[10px] rounded-[6px] cursor-pointer transition-all duration-200"
          :style="{
            background: currentSessionId === session.id ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.08)',
            opacity: currentSessionId === session.id ? 1 : 0.9
          }"
          @click="handleSessionClick(session.id)"
        >
          <p class="text-white text-[13px] leading-[20px] truncate">
            {{ session.title }}
          </p>
        </div>
      </div>
    </template>

    <!-- Empty State -->
    <div v-if="sessions.length === 0" class="flex flex-col items-center justify-center" :style="{ marginTop: '60px' }">
      <p class="text-white text-[13px] opacity-70" :style="{ textAlign: 'center' }">
        No chat history yet.
        <br />
        Start a new conversation!
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronDown, Plus } from 'lucide-vue-next'

interface ChatSession {
  id: string
  title: string
  messages: any[]
  lastUpdated: number
}

const sessions = ref<ChatSession[]>([])
const currentSessionId = ref<string | null>(null)
let intervalId: number | null = null

const loadSessions = () => {
  const sessionsData = localStorage.getItem('chatSessions')
  if (sessionsData) {
    const loadedSessions: ChatSession[] = JSON.parse(sessionsData)
    loadedSessions.sort((a, b) => b.lastUpdated - a.lastUpdated)
    sessions.value = loadedSessions
  }
}

const handleSessionClick = (sessionId: string) => {
  localStorage.setItem('currentChatSessionId', sessionId)
  currentSessionId.value = sessionId
  window.location.reload()
}

const handleNewChat = () => {
  const newSessionId = `session_${Date.now()}`
  localStorage.setItem('currentChatSessionId', newSessionId)
  window.location.reload()
}

const isToday = (timestamp: number) => {
  const today = new Date()
  const date = new Date(timestamp)
  return today.toDateString() === date.toDateString()
}

const isWithinWeek = (timestamp: number) => {
  const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000
  return timestamp > weekAgo && !isToday(timestamp)
}

const todaySessions = computed(() => sessions.value.filter(s => isToday(s.lastUpdated)))
const weekSessions = computed(() => sessions.value.filter(s => isWithinWeek(s.lastUpdated)))

onMounted(() => {
  loadSessions()

  const savedCurrentSession = localStorage.getItem('currentChatSessionId')
  currentSessionId.value = savedCurrentSession

  const handleStorageChange = () => {
    loadSessions()
    const updatedCurrentSession = localStorage.getItem('currentChatSessionId')
    currentSessionId.value = updatedCurrentSession
  }

  window.addEventListener('storage', handleStorageChange)
  intervalId = window.setInterval(loadSessions, 1000)
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>
