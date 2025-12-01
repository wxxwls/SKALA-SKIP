/**
 * Authentication API Module
 * Backend ref: AuthController.java
 * Follows frontend standard: api/auth.api.ts naming convention
 */

import apiClient from './axios.config';
import type {
  LoginRequest,
  LoginResponse,
  UserResponse,
  SetPasswordRequest,
  ChangePasswordRequest,
  ApiResponse
} from '@/types/auth';

const BASE_URL = '/api/v1/auth';

/**
 * Auth API endpoints
 */
export const authApi = {
  /**
   * Login
   * POST /api/v1/auth/login
   * Backend ref: AuthController.login() - AUTH-001
   */
  async login(request: LoginRequest): Promise<LoginResponse> {
    const { data } = await apiClient.post<ApiResponse<LoginResponse>>(
      `${BASE_URL}/login`,
      request
    );
    return data.data!;
  },

  /**
   * Get current user information
   * GET /api/v1/auth/me
   * Backend ref: AuthController.getCurrentUser()
   */
  async getCurrentUser(): Promise<UserResponse> {
    const { data } = await apiClient.get<ApiResponse<UserResponse>>(`${BASE_URL}/me`);
    return data.data!;
  },

  /**
   * Set password (for first login)
   * POST /api/v1/auth/set-password
   * Backend ref: AuthController.setPassword()
   */
  async setPassword(request: SetPasswordRequest): Promise<void> {
    await apiClient.post<ApiResponse<void>>(`${BASE_URL}/set-password`, request);
  },

  /**
   * Change password (requires current password)
   * POST /api/v1/auth/change-password
   * Backend ref: AuthController.changePassword()
   */
  async changePassword(request: ChangePasswordRequest): Promise<void> {
    await apiClient.post<ApiResponse<void>>(`${BASE_URL}/change-password`, request);
  }
};
