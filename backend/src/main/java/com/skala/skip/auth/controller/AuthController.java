package com.skala.skip.auth.controller;

import com.skala.skip.auth.dto.request.ChangePasswordRequest;
import com.skala.skip.auth.dto.request.LoginRequest;
import com.skala.skip.auth.dto.request.RefreshTokenRequest;
import com.skala.skip.auth.dto.request.RegisterRequest;
import com.skala.skip.auth.dto.request.SetPasswordRequest;
import com.skala.skip.auth.dto.response.CreateUserResponse;
import com.skala.skip.auth.dto.response.LoginResponse;
import com.skala.skip.auth.dto.response.TokenResponse;
import com.skala.skip.auth.dto.response.UserResponse;
import com.skala.skip.auth.service.AuthService;
import com.skala.skip.common.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/**
 * 인증 컨트롤러
 * 로그인, 비밀번호 변경, 사용자 정보 조회 엔드포인트 처리
 */
@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "인증", description = "인증 및 사용자 관리 API")
public class AuthController {

    private final AuthService authService;

    /**
     * 로그인
     * POST /api/v1/auth/login
     */
    @PostMapping("/login")
    @Operation(summary = "로그인", description = "사용자 인증 및 JWT 액세스 토큰 발급")
    public ResponseEntity<ApiResponse<LoginResponse>> login(@Valid @RequestBody LoginRequest request) {
        log.info("로그인 요청 수신: {}", request.getEmail());

        LoginResponse response = authService.login(request);

        return ResponseEntity.ok(ApiResponse.success(response));
    }

    /**
     * 비밀번호 변경 (현재 비밀번호 검증 필요)
     * POST /api/v1/auth/change-password
     */
    @PostMapping("/change-password")
    @Operation(summary = "비밀번호 변경", description = "사용자 비밀번호 변경 - 현재 비밀번호 검증 필요 (인증 필요)")
    public ResponseEntity<ApiResponse<Void>> changePassword(
            Authentication authentication,
            @Valid @RequestBody ChangePasswordRequest request
    ) {
        String email = authentication.getName();
        log.info("비밀번호 변경 요청: {}", email);

        authService.changePassword(email, request);

        return ResponseEntity.ok(ApiResponse.success());
    }

    /**
     * 비밀번호 설정 (최초 로그인 시, 현재 비밀번호 불필요)
     * POST /api/v1/auth/set-password
     */
    @PostMapping("/set-password")
    @Operation(summary = "비밀번호 설정", description = "최초 로그인 시 비밀번호 설정 - 현재 비밀번호 불필요 (인증 필요)")
    public ResponseEntity<ApiResponse<Void>> setPassword(
            Authentication authentication,
            @Valid @RequestBody SetPasswordRequest request
    ) {
        String email = authentication.getName();
        log.info("최초 비밀번호 설정 요청: {}", email);

        authService.setPassword(email, request);

        return ResponseEntity.ok(ApiResponse.success());
    }

    /**
     * 현재 사용자 정보 조회
     * GET /api/v1/auth/me
     */
    @GetMapping("/me")
    @Operation(summary = "현재 사용자 조회", description = "인증된 사용자 정보 조회")
    public ResponseEntity<ApiResponse<UserResponse>> getCurrentUser(Authentication authentication) {
        String email = authentication.getName();
        log.debug("현재 사용자 조회 요청: {}", email);

        UserResponse response = authService.getCurrentUser(email);

        return ResponseEntity.ok(ApiResponse.success(response));
    }

    /**
     * 로그아웃
     * POST /api/v1/auth/logout
     */
    @PostMapping("/logout")
    @Operation(summary = "로그아웃", description = "현재 Access Token 무효화")
    public ResponseEntity<ApiResponse<Void>> logout(
            @RequestHeader("Authorization") String authHeader,
            @RequestBody(required = false) RefreshTokenRequest refreshTokenRequest
    ) {
        String accessToken = authHeader.substring(7); // "Bearer " 제거
        String refreshToken = refreshTokenRequest != null ? refreshTokenRequest.getRefreshToken() : null;

        log.info("로그아웃 요청");
        authService.logout(accessToken, refreshToken);

        return ResponseEntity.ok(ApiResponse.success());
    }

    /**
     * 전체 기기 로그아웃
     * POST /api/v1/auth/logout-all
     */
    @PostMapping("/logout-all")
    @Operation(summary = "전체 기기 로그아웃", description = "모든 기기에서 로그아웃 (모든 Refresh Token 무효화)")
    public ResponseEntity<ApiResponse<Void>> logoutAll(
            @RequestAttribute("userId") Long userId
    ) {
        log.info("전체 기기 로그아웃 요청: userId={}", userId);
        authService.logoutAllDevices(userId);

        return ResponseEntity.ok(ApiResponse.success());
    }

    /**
     * Access Token 재발급
     * POST /api/v1/auth/refresh
     */
    @PostMapping("/refresh")
    @Operation(summary = "토큰 재발급", description = "Refresh Token으로 Access Token 재발급")
    public ResponseEntity<ApiResponse<TokenResponse>> refresh(
            @RequestBody @Valid RefreshTokenRequest request
    ) {
        log.info("Access Token 재발급 요청");
        TokenResponse response = authService.refreshAccessToken(request.getRefreshToken());

        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
