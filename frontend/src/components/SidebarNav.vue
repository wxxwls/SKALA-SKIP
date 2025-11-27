<script setup lang="ts">
import { ref, markRaw } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import {
  Home,
  Newspaper,
  List,
  FileText,
  Leaf,
  MessageSquare,
  Bell,
  Settings,
  User,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  LogOut
} from 'lucide-vue-next';
import { useAuthStore } from '@/stores';

// Store & Router
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

// State
const isCollapsed = ref(false);
const showProfileMenu = ref(false);

// Menu Items
const menuItems = [
  { id: 'Home', path: '/', label: 'Home', title: 'Home', icon: markRaw(Home) },
  { id: 'News', path: '/news', label: '뉴스', title: '뉴스', icon: markRaw(Newspaper) },
  { id: 'IssuePool', path: '/issue-pool', label: '이슈풀 구성', title: '이슈풀 구성', icon: markRaw(List) },
  { id: 'Materiality', path: '/materiality', label: '중대성 평가', title: '중대성 평가', icon: markRaw(BarChart3) },
  { id: 'Report', path: '/report', label: '보고서 작성', title: '보고서 작성', icon: markRaw(FileText) },
  { id: 'Carbon', path: '/carbon', label: '탄소 예측', title: '탄소 예측', icon: markRaw(Leaf) },
  { id: 'Chat', path: '/chat', label: 'AI Chat', title: 'AI Chat', icon: markRaw(MessageSquare) }
];

// Methods
function navigateTo(path: string) {
  router.push(path);
}

function handleLogout() {
  showProfileMenu.value = false;
  authStore.logout();
  router.push('/login');
}

function isActive(routeName: string) {
  return route.name === routeName;
}
</script>

<template>
  <aside
    class="sidebar"
    :class="{ 'sidebar-collapsed': isCollapsed }"
  >
    <div class="sidebar-inner">
      <!-- Top Menu Items -->
      <div class="menu-top">
        <div
          v-for="item in menuItems"
          :key="item.id"
          class="menu-item"
          :class="{ 'menu-item-active': isActive(item.id) }"
          :title="item.title"
          @click="navigateTo(item.path)"
        >
          <div
            class="menu-icon"
            :class="{ 'menu-icon-home': item.id === 'Home' }"
          >
            <component :is="item.icon" class="w-5 h-5 text-white" />
          </div>
          <span v-if="!isCollapsed" class="menu-label">
            {{ item.label }}
          </span>
        </div>
      </div>

      <!-- Bottom Menu Items -->
      <div class="menu-bottom">
        <div class="menu-item" title="알림">
          <div class="menu-icon">
            <Bell class="w-[22px] h-[22px] text-white opacity-70" />
          </div>
          <span v-if="!isCollapsed" class="menu-label opacity-70">알림</span>
        </div>

        <div class="menu-item" title="설정">
          <div class="menu-icon">
            <Settings class="w-[22px] h-[22px] text-white opacity-70" />
          </div>
          <span v-if="!isCollapsed" class="menu-label opacity-70">설정</span>
        </div>

        <!-- Profile Button -->
        <div class="profile-container">
          <div
            class="menu-item"
            title="프로필"
            @click="showProfileMenu = !showProfileMenu"
          >
            <div class="profile-avatar">
              <User class="w-4 h-4 text-white" />
            </div>
            <span v-if="!isCollapsed" class="menu-label opacity-70">프로필</span>
          </div>

          <!-- Dropdown Menu -->
          <div v-if="showProfileMenu" class="profile-dropdown">
            <div class="dropdown-item" @click="handleLogout">
              <LogOut class="w-4 h-4" />
              <span>로그아웃</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toggle Button -->
    <button
      class="toggle-button"
      :title="isCollapsed ? '사이드바 펼치기' : '사이드바 접기'"
      @click="isCollapsed = !isCollapsed"
    >
      <ChevronRight v-if="isCollapsed" class="w-5 h-5" :stroke-width="2.5" />
      <ChevronLeft v-else class="w-5 h-5" :stroke-width="2.5" />
    </button>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100%;
  width: 200px;
  background: var(--gradient-sidebar);
  z-index: var(--z-fixed);
  transition: width var(--transition-slow);
}

.sidebar-collapsed {
  width: 54px;
}

.sidebar-inner {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.08);
}

.menu-top {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding-top: var(--spacing-md);
  gap: 20px;
}

.menu-bottom {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding-bottom: 20px;
  gap: var(--spacing-md);
}

.menu-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: var(--spacing-sm) 11px;
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-normal);
  background: transparent;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.menu-item-active {
  background: rgba(255, 255, 255, 0.15);
}

.menu-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.menu-icon-home {
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
}

.menu-label {
  margin-left: 12px;
  color: var(--color-surface);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
}

.profile-container {
  position: relative;
}

.profile-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  margin-bottom: var(--spacing-sm);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 140px;
  overflow: hidden;
  z-index: var(--z-dropdown);
}

.sidebar-collapsed .profile-dropdown {
  left: 54px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 10px 14px;
  cursor: pointer;
  transition: all var(--transition-normal);
  color: var(--color-text-secondary);
}

.dropdown-item:hover {
  background: #f9fafb;
}

.dropdown-item span {
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.toggle-button {
  position: absolute;
  top: 50%;
  right: -15px;
  transform: translateY(-50%);
  width: 30px;
  height: 30px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--color-border);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  z-index: 10;
  transition: all var(--transition-normal);
}

.toggle-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.opacity-70 {
  opacity: 0.7;
}
</style>
