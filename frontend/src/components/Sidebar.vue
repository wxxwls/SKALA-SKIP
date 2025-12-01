<template>
  <aside
    class="flex flex-col transition-all duration-300 ease-in-out fixed left-0 top-0 h-full z-50"
    :style="{
      width: isCollapsed ? '64px' : '240px',
      background: '#FFFFFF',
      borderRight: '1px solid #E2E8F0'
    }"
  >
    <!-- Sidebar Content -->
    <div class="flex flex-col h-full">
      <!-- Top Section: Logo/Brand -->
      <div
        class="flex items-center transition-all"
        :style="{
          padding: isCollapsed ? 'var(--spacing-lg)' : 'var(--spacing-xl) var(--spacing-lg)',
          borderBottom: '1px solid var(--border)',
          justifyContent: isCollapsed ? 'center' : 'flex-start'
        }"
      >
        <div
          class="flex items-center justify-center rounded-lg transition-all"
          :style="{
            width: '40px',
            height: '40px',
            background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
            boxShadow: 'var(--shadow-sm)'
          }"
        >
          <span class="text-white text-xl font-bold">SK</span>
        </div>
        <div
          v-if="!isCollapsed"
          class="ml-3 transition-opacity"
          :style="{
            fontSize: '18px',
            fontWeight: 'var(--font-weight-semibold)',
            color: 'var(--foreground)',
            opacity: isCollapsed ? 0 : 1
          }"
        >
          SKIP ESG
        </div>
      </div>

      <!-- Main Navigation -->
      <nav class="flex-1 overflow-y-auto" :style="{ padding: 'var(--spacing-md) 0' }">
        <div
          v-for="item in menuItems"
          :key="item.id"
          class="group cursor-pointer transition-all relative"
          :style="{
            margin: '0 var(--spacing-md) var(--spacing-xs) var(--spacing-md)',
            padding: 'var(--spacing-md)',
            borderRadius: 'var(--radius-lg)',
            background: activeTab === item.id ? 'var(--accent)' : 'transparent',
            color: activeTab === item.id ? 'var(--primary)' : 'var(--foreground-secondary)'
          }"
          :title="isCollapsed ? item.title : ''"
          @click="$emit('tabChange', item.id)"
          @mouseenter="hoveredItem = item.id"
          @mouseleave="hoveredItem = null"
        >
          <!-- Active Indicator -->
          <div
            v-if="activeTab === item.id"
            :style="{
              position: 'absolute',
              left: 0,
              top: '50%',
              transform: 'translateY(-50%)',
              width: '3px',
              height: '60%',
              background: 'var(--primary)',
              borderRadius: '0 var(--radius-sm) var(--radius-sm) 0'
            }"
          />

          <div class="flex items-center" :style="{ gap: 'var(--spacing-md)' }">
            <component
              :is="item.icon"
              :size="20"
              :stroke-width="activeTab === item.id ? 2.5 : 2"
              class="flex-shrink-0 transition-all"
            />
            <span
              v-if="!isCollapsed"
              class="transition-all"
              :style="{
                fontSize: '14px',
                fontWeight: activeTab === item.id ? 'var(--font-weight-semibold)' : 'var(--font-weight-medium)'
              }"
            >
              {{ item.label }}
            </span>
          </div>

          <!-- Hover background -->
          <div
            v-if="hoveredItem === item.id && activeTab !== item.id"
            :style="{
              position: 'absolute',
              inset: 0,
              background: 'var(--muted)',
              borderRadius: 'var(--radius-lg)',
              zIndex: -1
            }"
          />
        </div>
      </nav>

      <!-- Bottom Section: Settings & Profile -->
      <div
        :style="{
          padding: 'var(--spacing-lg)',
          borderTop: '1px solid var(--border)'
        }"
      >
        <!-- Settings -->
        <div
          class="group cursor-pointer transition-all flex items-center"
          :style="{
            padding: 'var(--spacing-md)',
            borderRadius: 'var(--radius-lg)',
            gap: 'var(--spacing-md)',
            color: 'var(--foreground-secondary)',
            marginBottom: 'var(--spacing-sm)'
          }"
          :title="isCollapsed ? '설정' : ''"
          @mouseenter="hoveredItem = 'settings'"
          @mouseleave="hoveredItem = null"
        >
          <Settings :size="20" class="flex-shrink-0" />
          <span
            v-if="!isCollapsed"
            :style="{
              fontSize: '14px',
              fontWeight: 'var(--font-weight-medium)'
            }"
          >
            설정
          </span>

          <!-- Hover background -->
          <div
            v-if="hoveredItem === 'settings'"
            :style="{
              position: 'absolute',
              inset: 0,
              background: 'var(--muted)',
              borderRadius: 'var(--radius-lg)',
              zIndex: -1
            }"
          />
        </div>

        <!-- Profile with Dropdown -->
        <div :style="{ position: 'relative' }">
          <div
            class="group cursor-pointer transition-all flex items-center relative"
            :style="{
              padding: 'var(--spacing-md)',
              borderRadius: 'var(--radius-lg)',
              gap: 'var(--spacing-md)',
              color: 'var(--foreground-secondary)'
            }"
            :title="isCollapsed ? '프로필' : ''"
            @click="showProfileMenu = !showProfileMenu"
            @mouseenter="hoveredItem = 'profile'"
            @mouseleave="hoveredItem = null"
          >
            <div
              class="rounded-full flex items-center justify-center flex-shrink-0"
              :style="{
                width: '32px',
                height: '32px',
                background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                color: '#FFFFFF',
                fontSize: '14px',
                fontWeight: 'var(--font-weight-semibold)'
              }"
            >
              U
            </div>
            <div
              v-if="!isCollapsed"
              class="flex-1"
              :style="{
                fontSize: '14px',
                fontWeight: 'var(--font-weight-medium)'
              }"
            >
              사용자
            </div>

            <!-- Hover background -->
            <div
              v-if="hoveredItem === 'profile'"
              :style="{
                position: 'absolute',
                inset: 0,
                background: 'var(--muted)',
                borderRadius: 'var(--radius-lg)',
                zIndex: -1
              }"
            />
          </div>

          <!-- Dropdown Menu -->
          <Transition
            name="fade-scale"
            enter-active-class="transition-all duration-200 ease-out"
            leave-active-class="transition-all duration-150 ease-in"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="showProfileMenu"
              :style="{
                position: 'absolute',
                bottom: '100%',
                left: isCollapsed ? '64px' : '0',
                marginBottom: 'var(--spacing-sm)',
                background: 'var(--card)',
                borderRadius: 'var(--radius-lg)',
                boxShadow: 'var(--shadow-lg)',
                minWidth: isCollapsed ? '160px' : '100%',
                overflow: 'hidden',
                border: '1px solid var(--border)',
                zIndex: 1000
              }"
            >
              <div
                class="cursor-pointer transition-all hover:bg-[var(--muted)]"
                :style="{
                  padding: 'var(--spacing-md)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-md)'
                }"
                @click="handleLogout"
              >
                <LogOut :size="16" :style="{ color: 'var(--foreground-secondary)' }" />
                <span
                  :style="{
                    fontSize: '14px',
                    fontWeight: 'var(--font-weight-medium)',
                    color: 'var(--foreground)'
                  }"
                >
                  로그아웃
                </span>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Toggle Button -->
    <button
      class="absolute flex items-center justify-center rounded-full transition-all duration-200"
      :style="{
        top: 'var(--spacing-3xl)',
        right: '-12px',
        width: '24px',
        height: '24px',
        background: 'var(--card)',
        border: '1px solid var(--border)',
        boxShadow: 'var(--shadow-md)',
        color: 'var(--foreground-secondary)',
        zIndex: 10
      }"
      :title="isCollapsed ? '사이드바 펼치기' : '사이드바 접기'"
      @click="isCollapsed = !isCollapsed"
      @mouseenter="hoveredItem = 'toggle'"
      @mouseleave="hoveredItem = null"
    >
      <ChevronRight v-if="isCollapsed" :size="14" :stroke-width="2.5" />
      <ChevronLeft v-else :size="14" :stroke-width="2.5" />
    </button>
  </aside>
</template>

<script setup lang="ts">
import { ref, markRaw } from 'vue'
import {
  Home, Newspaper, List, FileText, Leaf, MessageSquare,
  Settings, ChevronLeft, ChevronRight, BarChart3, LogOut
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
const hoveredItem = ref<string | null>(null)

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
