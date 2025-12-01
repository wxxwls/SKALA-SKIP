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
import skipLogo from '@/assets/SKIP-removebg-preview.png';
import esgMark from '@/assets/ESG-removebg-preview.png';

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
      <!-- Top Section: Logo/Brand -->
      <div class="logo-section" :class="{ 'justify-center': isCollapsed }">
        <div class="logo-stack" :class="{ 'logo-stack-collapsed': isCollapsed }">
          <img :src="esgMark" alt="ESG" class="logo-esg-img" />
          <img :src="skipLogo" alt="SKIP" class="logo-skip-img" />
        </div>
      </div>

      <!-- Main Navigation -->
      <nav class="menu-nav">
        <div
          v-for="item in menuItems"
          :key="item.id"
          class="menu-item"
          :class="{ 'menu-item-active': isActive(item.id) }"
          :title="isCollapsed ? item.title : ''"
          @click="navigateTo(item.path)"
        >
          <!-- Active Indicator -->
          <div v-if="isActive(item.id)" class="active-indicator" />

          <div class="menu-content">
            <component
              :is="item.icon"
              :size="20"
              :stroke-width="isActive(item.id) ? 2.5 : 2"
              class="menu-icon"
            />
            <span v-if="!isCollapsed" class="menu-label">
              {{ item.label }}
            </span>
          </div>
        </div>
      </nav>

      <!-- Bottom Section: Settings & Profile -->
      <div class="bottom-section">
        <!-- Settings -->
        <div
          class="menu-item"
          :title="isCollapsed ? '설정' : ''"
        >
          <div class="menu-content">
            <Settings :size="20" class="menu-icon" />
            <span v-if="!isCollapsed" class="menu-label">설정</span>
          </div>
        </div>

        <!-- Profile with Dropdown -->
        <div class="profile-container">
          <div
            class="menu-item"
            :title="isCollapsed ? '프로필' : ''"
            @click="showProfileMenu = !showProfileMenu"
          >
            <div class="menu-content">
              <div class="profile-avatar">
                U
              </div>
              <span v-if="!isCollapsed" class="menu-label">사용자</span>
            </div>
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
            <div v-if="showProfileMenu" class="profile-dropdown">
              <div class="dropdown-item" @click="handleLogout">
                <LogOut :size="16" />
                <span>로그아웃</span>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Toggle Button -->
    <button
      class="toggle-button"
      :title="isCollapsed ? '사이드바 펼치기' : '사이드바 접기'"
      @click="isCollapsed = !isCollapsed"
    >
      <ChevronRight v-if="isCollapsed" :size="14" :stroke-width="2.5" />
      <ChevronLeft v-else :size="14" :stroke-width="2.5" />
    </button>
  </aside>
</template>

<style scoped>
.sidebar {
  position: relative; /* Changed from fixed to flow with flex */
  height: 100%;
  width: 260px; /* Slightly wider for premium feel */
  background: #FFFFFF;
  /* border-right: 1px solid var(--border); Removed for cleaner look */
  box-shadow: 1px 0 0 0 rgba(0, 0, 0, 0.05); /* Very subtle separator */
  z-index: 50;
  transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  flex-shrink: 0; /* Prevent shrinking */
}

.sidebar-collapsed {
  width: 68px;
}

.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 12px;
}

/* Logo Section */
.logo-section {
  display: flex;
  align-items: center;
  padding: 20px 12px;
  margin-bottom: 20px;
  transition: all 0.3s;
}

.logo-section.justify-center {
  padding: 20px 0;
  justify-content: center;
}

.logo-stack {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1;
}

.logo-stack-collapsed {
  align-items: center;
}

.logo-esg-img {
  height: 32px;
  width: auto;
  margin-bottom: -40px;
  margin-left: 30px;
}

.logo-stack-collapsed .logo-esg-img {
  height: 18px;
  margin-left: 4px;
  margin-bottom: -14px;
}

.logo-skip-img {
  height: 100px;
  width: auto;
}

.logo-stack-collapsed .logo-skip-img {
  height: 44px;
}

/* Navigation */
.menu-nav {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.menu-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  border-radius: 8px; /* Slightly sharper for corporate feel */
  transition: all 0.2s ease;
  color: #52525B;
  font-weight: 500;
}

.menu-item:hover {
  background: #F4F4F5;
  color: #1D1D1F;
}

.menu-item-active {
  background: #FFF0F2; /* Very light red bg */
  color: #EA002C; /* SK Red */
}

.menu-content {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.menu-icon {
  flex-shrink: 0;
  transition: all 0.2s;
  color: inherit;
}

.menu-label {
  font-size: 15px;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.2s;
  letter-spacing: -0.01em;
}

.menu-item-active .menu-label {
  font-weight: 700;
}

.active-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: #EA002C;
  border-radius: 0 4px 4px 0;
  display: block; /* Show indicator again for corporate feel */
}

/* Bottom Section */
.bottom-section {
  padding-top: 20px;
  border-top: 1px solid #F5F5F7;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.profile-container {
  position: relative;
}

.profile-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #F5F5F7;
  color: #1D1D1F;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 11px;
  flex-shrink: 0;
  border: 1px solid rgba(0,0,0,0.05);
}

.profile-info {
  font-size: 14px;
  font-weight: 500;
  color: #1D1D1F;
}

.profile-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  margin-bottom: 8px;
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(0,0,0,0.05);
  min-width: 100%;
  overflow: hidden;
  z-index: 100;
  padding: 6px;
}

.sidebar-collapsed .profile-dropdown {
  left: 64px;
  min-width: 180px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: #1D1D1F;
  border-radius: 10px;
}

.dropdown-item:hover {
  background: #F5F5F7;
}

.dropdown-item span {
  font-size: 14px;
  font-weight: 500;
}

/* Toggle Button */
.toggle-button {
  position: absolute;
  top: 28px;
  right: -12px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #FFFFFF;
  border: 1px solid #E5E5EA;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #86868B;
  z-index: 60;
  transition: all 0.2s;
  cursor: pointer;
}

.toggle-button:hover {
  color: #1D1D1F;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}
</style>
