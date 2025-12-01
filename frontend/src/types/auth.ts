/**
 * Authentication & Authorization Type Definitions
 * Backend API ref: AuthController.java, LoginRequest.java, LoginResponse.java
 * Follows backend standard ApiResponse wrapper pattern
 */

/**
 * Login request payload
 * Backend: LoginRequest.java
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * User information within login response
 * Backend: LoginResponse.UserInfoDto
 */
export interface UserInfo {
  id: number;
  name: string;
  role: string;
  firstLogin: boolean;
}

/**
 * Login response from backend
 * Backend: LoginResponse.java
 */
export interface LoginResponse {
  accessToken: string;
  tokenType: string;
  user: UserInfo;
}

/**
 * User response from /api/v1/auth/me endpoint
 * Backend: UserResponse.java
 */
export interface UserResponse {
  userId: number;
  userName: string;
  email: string;
  userRole: string;
  firstLoginFlag: boolean;
  accountLocked: boolean;
  passwordUpdatedAt: string;
  createdAt: string;
}

/**
 * Set password request payload (for first login)
 * Backend: SetPasswordRequest.java
 */
export interface SetPasswordRequest {
  newPassword: string;
}

/**
 * Change password request payload (for profile)
 * Backend: ChangePasswordRequest.java
 */
export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

/**
 * Standard API response wrapper from backend
 * Backend: ApiResponse.java
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ErrorDetail;
  meta?: MetaData;
}

/**
 * API error structure
 * Backend: ApiResponse.ErrorDetail
 */
export interface ErrorDetail {
  code: string;
  message: string;
  detail?: string;
  timestamp: string;
}

/**
 * API metadata
 * Backend: ApiResponse.MetaData
 */
export interface MetaData {
  traceId?: string;
  timestamp: string;
}
