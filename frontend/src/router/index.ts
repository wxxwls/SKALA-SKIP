import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: {
      title: '로그인',
      requiresAuth: false,
      layout: 'none'
    }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/views/auth/ChangePasswordView.vue'),
    meta: {
      title: '비밀번호 설정',
      requiresAuth: true,
      layout: 'none'
    }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/home/HomeView.vue'),
    meta: {
      title: 'Home',
      requiresAuth: true,
      layout: 'default'
    }
  },
  {
    path: '/news',
    name: 'News',
    component: () => import('@/views/news/NewsView.vue'),
    meta: {
      title: '뉴스',
      requiresAuth: true
    }
  },
  {
    path: '/issue-pool',
    name: 'IssuePool',
    component: () => import('@/views/issuepool/IssuePoolView.vue'),
    meta: {
      title: '이슈풀 구성',
      requiresAuth: true
    }
  },
  {
    path: '/documents',
    name: 'Documents',
    component: () => import('@/views/documents/DocumentsView.vue'),
    meta: {
      title: '문서목록',
      requiresAuth: true
    }
  },
  {
    path: '/materiality',
    name: 'Materiality',
    component: () => import('@/views/materiality/MaterialityView.vue'),
    meta: {
      title: '중대성 평가',
      requiresAuth: true
    }
  },
  {
    path: '/report',
    name: 'Report',
    component: () => import('@/views/report/ReportView.vue'),
    meta: {
      title: '보고서 작성',
      requiresAuth: true
    }
  },
  {
    path: '/carbon',
    name: 'Carbon',
    component: () => import('@/views/carbon/CarbonView.vue'),
    meta: {
      title: '탄소 예측',
      requiresAuth: true
    }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/chat/ChatView.vue'),
    meta: {
      title: 'AI Chat',
      requiresAuth: true
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard for authentication
router.beforeEach(async (to, _from, next) => {
  const requiresAuth = to.meta.requiresAuth;
  const token = localStorage.getItem('access_token');
  const authStore = useAuthStore();

  // 인증이 필요한 페이지인데 토큰이 없으면 로그인 페이지로
  if (requiresAuth && !token) {
    next('/login');
    return;
  }

  // 로그인 페이지인데 이미 로그인 되어 있으면 홈으로
  if (to.path === '/login' && token) {
    next('/');
    return;
  }

  // 토큰이 있으면 항상 API로 최신 유저 정보 조회
  if (token && to.name !== 'ChangePassword') {
    await authStore.checkAuth();

    // 최초 로그인 사용자는 비밀번호 변경 페이지만 접근 가능
    if (authStore.isFirstLogin) {
      alert('보안을 위해 비밀번호를 먼저 변경해주세요.');
      next('/change-password');
      return;
    }
  }

  next();
});

export default router;
