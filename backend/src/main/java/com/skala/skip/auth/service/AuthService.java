package com.skala.skip.auth.service;

import com.skala.skip.auth.dto.request.ChangePasswordRequest;
import com.skala.skip.auth.dto.request.CreateUserRequest;
import com.skala.skip.auth.dto.request.LoginRequest;
import com.skala.skip.auth.dto.request.RegisterRequest;
import com.skala.skip.auth.dto.request.SetPasswordRequest;
import com.skala.skip.auth.dto.response.CreateUserResponse;
import com.skala.skip.auth.dto.response.LoginResponse;
import com.skala.skip.auth.dto.response.TokenResponse;
import com.skala.skip.auth.dto.response.UserResponse;

/**
 * Authentication Service Interface
 */
public interface AuthService {

    /**
     * Login user
     * @param request Login request
     * @return Login response with JWT token
     */
    LoginResponse login(LoginRequest request);

    /**
     * Change user password (requires current password)
     * @param email User email
     * @param request Change password request
     */
    void changePassword(String email, ChangePasswordRequest request);

    /**
     * Set user password (for first login, no current password required)
     * @param email User email
     * @param request Set password request
     */
    void setPassword(String email, SetPasswordRequest request);

    /**
     * Get current user information
     * @param email User email
     * @return User information
     */
    UserResponse getCurrentUser(String email);

    /**
     * Register new user (Public)
     * @param request Register request
     * @return Created user information
     */
    CreateUserResponse register(RegisterRequest request);

    /**
     * Create new user (Admin only)
     * Ref: authentication_login_standard.md - Section 7.1, 7.2
     * @param request Create user request
     * @return Created user information
     */
    CreateUserResponse createUser(CreateUserRequest request);

    /**
     * 로그아웃 - 현재 Access Token 무효화
     * @param accessToken JWT Access Token
     * @param refreshToken JWT Refresh Token (optional)
     */
    void logout(String accessToken, String refreshToken);

    /**
     * 전체 기기 로그아웃 - 모든 Refresh Token 무효화
     * @param userId 사용자 ID
     */
    void logoutAllDevices(Long userId);

    /**
     * Access Token 재발급
     * @param refreshToken JWT Refresh Token
     * @return 새로운 Access Token
     */
    TokenResponse refreshAccessToken(String refreshToken);
}
