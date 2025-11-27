<template>
  <aside
    class="flex flex-col transition-all duration-300 ease-in-out fixed left-0 top-0 h-full z-50"
    :style="{
      width: isCollapsed ? '54px' : '200px',
      background: 'linear-gradient(to bottom, #FF9933, #FF7A00)'
    }"
  >
    <!-- Icon Navigation Strip -->
    <div
      class="absolute left-0 top-0 h-full flex flex-col"
      :style="{
        width: '100%',
        background: 'rgba(0,0,0,0.08)'
      }"
    >
      <!-- Top Icons -->
      <div class="flex flex-col w-full" :style="{ paddingTop: '16px', gap: '20px' }">
        <div
          v-for="item in menuItems"
          :key="item.id"
          class="flex items-center w-full cursor-pointer group hover:bg-white/10 transition-all py-2 rounded-lg"
          :style="{
            paddingLeft: '11px',
            paddingRight: '11px',
            background: activeTab === item.id ? 'rgba(255,255,255,0.15)' : 'transparent'
          }"
          :title="item.title"
          @click="$emit('tabChange', item.id)"
        >
          <div
            class="flex items-center justify-center flex-shrink-0"
            :style="{
              width: '32px',
              height: '32px',
              borderRadius: item.id === 'home' ? '50%' : '0',
              background: item.id === 'home' ? 'rgba(255,255,255,0.15)' : 'transparent'
            }"
          >
            <component :is="item.icon" class="w-5 h-5 text-white" />
          </div>
          <span
            v-if="!isCollapsed"
            class="ml-3 text-white text-[14px] whitespace-nowrap"
            :style="{ fontWeight: 500 }"
          >
            {{ item.label }}
          </span>
        </div>
      </div>

      <!-- Bottom Icons -->
      <div class="mt-auto flex flex-col w-full" :style="{ paddingBottom: '20px', gap: '16px' }">
        <div
          class="flex items-center w-full cursor-pointer hover:bg-white/10 transition-all py-2 rounded-lg"
          :style="{ paddingLeft: '11px', paddingRight: '11px' }"
          title="알림"
        >
          <div class="flex items-center justify-center flex-shrink-0" :style="{ width: '32px', height: '32px' }">
            <Bell class="w-[22px] h-[22px] text-white flex-shrink-0" :style="{ opacity: 0.7 }" />
          </div>
          <span
            v-if="!isCollapsed"
            class="ml-3 text-white text-[14px] whitespace-nowrap"
            :style="{ fontWeight: 500, opacity: 0.7 }"
          >
            알림
          </span>
        </div>

        <div
          class="flex items-center w-full cursor-pointer hover:bg-white/10 transition-all py-2 rounded-lg"
          :style="{ paddingLeft: '11px', paddingRight: '11px' }"
          title="설정"
        >
          <div class="flex items-center justify-center flex-shrink-0" :style="{ width: '32px', height: '32px' }">
            <Settings class="w-[22px] h-[22px] text-white flex-shrink-0" :style="{ opacity: 0.7 }" />
          </div>
          <span
            v-if="!isCollapsed"
            class="ml-3 text-white text-[14px] whitespace-nowrap"
            :style="{ fontWeight: 500, opacity: 0.7 }"
          >
            설정
          </span>
        </div>

        <!-- Profile Button with Dropdown -->
        <div :style="{ position: 'relative' }">
          <div
            class="flex items-center w-full cursor-pointer hover:bg-white/10 transition-all py-2 rounded-lg"
            :style="{ paddingLeft: '11px', paddingRight: '11px' }"
            title="프로필"
            @click="showProfileMenu = !showProfileMenu"
          >
            <div
              class="rounded-full flex items-center justify-center flex-shrink-0"
              :style="{
                width: '28px',
                height: '28px',
                border: '2px solid rgba(255,255,255,0.3)',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              }"
            >
              <User class="w-4 h-4 text-white" />
            </div>
            <span
              v-if="!isCollapsed"
              class="ml-3 text-white text-[14px] whitespace-nowrap"
              :style="{ fontWeight: 500, opacity: 0.7 }"
            >
              프로필
            </span>
          </div>

          <!-- Dropdown Menu -->
          <div
            v-if="showProfileMenu"
            :style="{
              position: 'absolute',
              bottom: '100%',
              left: isCollapsed ? '54px' : '0',
              marginBottom: '8px',
              background: '#FFFFFF',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              minWidth: isCollapsed ? '140px' : '100%',
              overflow: 'hidden',
              zIndex: 1000
            }"
          >
            <div
              class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 transition-all"
              :style="{ padding: '10px 14px' }"
              @click="handleLogout"
            >
              <LogOut class="w-4 h-4" :style="{ color: '#6B7280' }" />
              <span :style="{ fontSize: '13px', fontWeight: 500, color: '#1A1F2E' }">로그아웃</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toggle Button -->
    <button
      class="absolute flex items-center justify-center rounded-md transition-all duration-200 hover:bg-white/30"
      :style="{
        top: '50%',
        transform: 'translateY(-50%)',
        right: '-15px',
        width: '30px',
        height: '30px',
        background: 'rgba(255,255,255,0.95)',
        border: '1px solid #E8EAED',
        boxShadow: '0px 2px 6px rgba(0,0,0,0.1)',
        zIndex: 10
      }"
      :title="isCollapsed ? '사이드바 펼치기' : '사이드바 접기'"
      @click="isCollapsed = !isCollapsed"
    >
      <ChevronRight v-if="isCollapsed" class="w-5 h-5" :style="{ color: '#FF7A00' }" :stroke-width="2.5" />
      <ChevronLeft v-else class="w-5 h-5" :style="{ color: '#FF7A00' }" :stroke-width="2.5" />
    </button>
  </aside>
</template>

<script setup lang="ts">
import { ref, markRaw } from 'vue'
import {
  Home, Newspaper, List, FileText, Leaf, MessageSquare,
  Bell, Settings, User, ChevronLeft, ChevronRight, BarChart3, LogOut
} from 'lucide-vue-next'

defineProps<{
  activeTab: string
}>()

const emit = defineEmits<{
  tabChange: [tab: string]
  logout: []
}>()

const isCollapsed = ref(false)
const showProfileMenu = ref(false)

const menuItems = [
  { id: 'home', label: 'Home', title: 'Home', icon: markRaw(Home) },
  { id: 'news', label: '뉴스', title: '뉴스', icon: markRaw(Newspaper) },
  { id: 'issue-pool', label: '이슈풀 구성', title: '이슈풀 구성', icon: markRaw(List) },
  { id: 'materiality', label: '중대성 평가', title: '중대성 평가', icon: markRaw(BarChart3) },
  { id: 'report', label: '보고서 작성', title: '보고서 작성', icon: markRaw(FileText) },
  { id: 'carbon', label: '탄소 예측', title: '탄소 예측', icon: markRaw(Leaf) },
  { id: 'ai-chat', label: 'AI Chat', title: 'AI Chat', icon: markRaw(MessageSquare) },
]

const handleLogout = () => {
  showProfileMenu.value = false
  emit('logout')
}
</script>
