/**
 * Auth Store
 * Manages authentication state and actions
 * Follows Pinia Composition API pattern
 * Backend API ref: AuthController.java
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types';
import { authApi } from '@/api/auth.api';
import type { LoginRequest, SetPasswordRequest } from '@/types/auth';
import { AUTH_MESSAGES } from '@/constants/messages';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  const isAuthenticated = ref(false);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const failedAttempts = ref(0);
  const maxAttempts = 5;

  // Getters
  const userName = computed(() => user.value?.name ?? '');
  const userEmail = computed(() => user.value?.email ?? '');
  const userRole = computed(() => user.value?.role ?? '');
  const isFirstLogin = computed(() => user.value?.firstLogin ?? false);
  const remainingAttempts = computed(() => maxAttempts - failedAttempts.value);

  // Actions
  function setAuth(userInfo: User, authToken: string) {
    user.value = userInfo;
    token.value = authToken;
    isAuthenticated.value = true;
    localStorage.setItem('access_token', authToken);
  }

  function clearAuth() {
    user.value = null;
    token.value = null;
    isAuthenticated.value = false;
    error.value = null;
    localStorage.removeItem('access_token');
  }

  async function checkAuth() {
    const savedToken = localStorage.getItem('access_token');
    if (savedToken) {
      token.value = savedToken;
      isAuthenticated.value = true;

      try {
        const userResponse = await authApi.getCurrentUser();
        user.value = {
          id: userResponse.userId,
          name: userResponse.userName,
          email: userResponse.email,
          role: userResponse.userRole,
          firstLogin: userResponse.firstLoginFlag
        };
      } catch (e) {
        clearAuth();
      }
    }
  }

  async function login(email: string, password: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      const request: LoginRequest = { email, password };
      const response = await authApi.login(request);

      // 토큰 먼저 저장
      token.value = response.accessToken;
      isAuthenticated.value = true;
      localStorage.setItem('access_token', response.accessToken);

      // /api/v1/auth/me로 최신 사용자 정보 조회
      const userResponse = await authApi.getCurrentUser();
      user.value = {
        id: userResponse.userId,
        name: userResponse.userName,
        email: userResponse.email,
        role: userResponse.userRole,
        firstLogin: userResponse.firstLoginFlag
      };

      // 성공 시 실패 횟수 초기화
      failedAttempts.value = 0;

      return true;
    } catch (e: unknown) {
      // 실패 시 횟수 증가
      failedAttempts.value++;
      const errorMessage = e instanceof Error ? e.message : AUTH_MESSAGES.LOGIN_FAILED;
      error.value = errorMessage;
      console.error('Login failed:', e);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  function logout() {
    clearAuth();
  }

  async function setPassword(newPassword: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      const request: SetPasswordRequest = { newPassword };
      await authApi.setPassword(request);

      // Update firstLogin flag after successful password change
      if (user.value) {
        user.value.firstLogin = false;
      }

      return true;
    } catch (e: unknown) {
      const errorMessage = e instanceof Error ? e.message : AUTH_MESSAGES.PASSWORD_CHANGE_FAILED;
      error.value = errorMessage;
      console.error('Password change failed:', e);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    // State
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    failedAttempts,
    // Getters
    userName,
    userEmail,
    userRole,
    isFirstLogin,
    remainingAttempts,
    // Actions
    setAuth,
    clearAuth,
    checkAuth,
    login,
    logout,
    setPassword
  };
});
