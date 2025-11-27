package com.skala.skip.auth.service.impl;

import com.skala.skip.auth.dto.request.ChangePasswordRequest;
import com.skala.skip.auth.dto.request.CreateUserRequest;
import com.skala.skip.auth.dto.request.LoginRequest;
import com.skala.skip.auth.dto.request.RegisterRequest;
import com.skala.skip.auth.dto.request.SetPasswordRequest;
import com.skala.skip.auth.dto.response.CreateUserResponse;
import com.skala.skip.auth.dto.response.LoginResponse;
import com.skala.skip.auth.dto.response.TokenResponse;
import com.skala.skip.auth.dto.response.UserResponse;
import com.skala.skip.auth.entity.RefreshToken;
import com.skala.skip.auth.entity.User;
import com.skala.skip.auth.exception.AccountLockedException;
import com.skala.skip.auth.exception.AuthErrorCode;
import com.skala.skip.auth.exception.AuthenticationException;
import com.skala.skip.auth.exception.InvalidCredentialsException;
import com.skala.skip.auth.repository.RefreshTokenRepository;
import com.skala.skip.auth.repository.UserRepository;
import com.skala.skip.auth.service.AuthService;
import com.skala.skip.auth.service.TokenBlacklistService;
import com.skala.skip.auth.util.JwtTokenProvider;
import org.springframework.util.StringUtils;
import lombok.RequiredArgsConstructor;

import java.time.LocalDateTime;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 인증 서비스 구현체
 */
@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
@Slf4j
public class AuthServiceImpl implements AuthService {

    private final UserRepository userRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final LoginAttemptService loginAttemptService;
    private final TokenBlacklistService tokenBlacklistService;

    /**
     * 사용자 로그인
     */
    @Override
    @Transactional
    public LoginResponse login(LoginRequest request) {
        log.info("로그인 시도: {}", request.getEmail());

        // 이메일로 사용자 조회
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new InvalidCredentialsException("잘못된 이메일 또는 비밀번호"));

        // 계정 잠금 확인
        if (user.isLocked()) {
            log.warn("잠긴 계정으로 로그인 시도: {}", request.getEmail());
            throw new AccountLockedException("계정이 잠겼습니다. 관리자에게 문의하세요.");
        }

        // 비밀번호 검증
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            int remainingAttempts = loginAttemptService.handleFailedLogin(user.getUserId());
            throw new InvalidCredentialsException("잘못된 이메일 또는 비밀번호", remainingAttempts);
        }

        // 로그인 성공 시 실패 횟수 초기화
        user.resetLoginFailCount();
        userRepository.save(user);

        // JWT Access Token 생성
        String accessToken = jwtTokenProvider.generateAccessToken(
                user.getUserId(),
                user.getEmail(),
                user.getUserRole()
        );

        // JWT Refresh Token 생성 및 DB 저장
        String refreshTokenValue = jwtTokenProvider.generateRefreshToken(user.getUserId());
        LocalDateTime expiresAt = LocalDateTime.now().plusSeconds(
                jwtTokenProvider.getRefreshTokenExpirationInSeconds()
        );

        RefreshToken refreshToken = RefreshToken.create(
                user.getUserId(),
                refreshTokenValue,
                null, // deviceInfo - 필요시 request에서 User-Agent 추출
                expiresAt
        );
        refreshTokenRepository.save(refreshToken);

        log.info("로그인 성공: {} ({})", user.getEmail(), user.getUserId());

        // 응답 생성
        return LoginResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshTokenValue)
                .tokenType("Bearer")
                .expiresIn(jwtTokenProvider.getAccessTokenExpirationInSeconds())
                .user(LoginResponse.UserInfoDto.builder()
                        .id(user.getUserId())
                        .name(user.getUserName())
                        .role(user.getUserRole())
                        .firstLogin(user.requiresPasswordChange())
                        .build())
                .build();
    }

    /**
     * 비밀번호 변경 (현재 비밀번호 검증 필요)
     */
    @Override
    @Transactional
    public void changePassword(String email, ChangePasswordRequest request) {
        log.info("비밀번호 변경 요청: {}", email);

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new AuthenticationException(AuthErrorCode.AUTH_009));

        // 현재 비밀번호 검증
        if (!passwordEncoder.matches(request.getCurrentPassword(), user.getPassword())) {
            log.warn("현재 비밀번호 불일치: {}", email);
            throw new AuthenticationException(AuthErrorCode.AUTH_006, "현재 비밀번호가 일치하지 않습니다");
        }

        // 새 비밀번호 검증은 DTO의 @Pattern 어노테이션에서 처리됨

        // 비밀번호 암호화 및 업데이트
        String encodedPassword = passwordEncoder.encode(request.getNewPassword());
        user.updatePassword(encodedPassword);
        userRepository.save(user);

        log.info("비밀번호 변경 성공: {}", email);
    }

    /**
     * 비밀번호 설정 (최초 로그인 시, 현재 비밀번호 검증 불필요)
     */
    @Override
    @Transactional
    public void setPassword(String email, SetPasswordRequest request) {
        log.info("최초 비밀번호 설정 요청: {}", email);

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new AuthenticationException(AuthErrorCode.AUTH_009));

        // 최초 로그인 사용자만 이 API 사용 가능
        if (!user.requiresPasswordChange()) {
            log.warn("최초 로그인 사용자가 아님: {}", email);
            throw new AuthenticationException(AuthErrorCode.AUTH_006, "최초 로그인 사용자만 사용할 수 있습니다");
        }

        // 새 비밀번호 검증은 DTO의 @Pattern 어노테이션에서 처리됨

        // 비밀번호 암호화 및 업데이트
        String encodedPassword = passwordEncoder.encode(request.getNewPassword());
        user.updatePassword(encodedPassword);
        userRepository.save(user);

        log.info("최초 비밀번호 설정 성공: {}", email);
    }

    /**
     * 현재 사용자 정보 조회
     */
    @Override
    public UserResponse getCurrentUser(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new AuthenticationException(AuthErrorCode.AUTH_009));

        return UserResponse.builder()
                .userId(user.getUserId())
                .userName(user.getUserName())
                .email(user.getEmail())
                .userRole(user.getUserRole())
                .firstLoginFlag(user.getFirstLoginFlag())
                .accountLocked(user.getAccountLocked())
                .passwordUpdatedAt(user.getPasswordUpdatedAt())
                .createdAt(user.getCreatedAt())
                .build();
    }

    /**
     * 회원가입 (공개)
     */
    @Override
    @Transactional
    public CreateUserResponse register(RegisterRequest request) {
        log.info("회원가입 요청: {}", request.getEmail());

        // 중복 이메일 검증
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new AuthenticationException(AuthErrorCode.AUTH_008, "이미 존재하는 이메일입니다");
        }

        // 비밀번호 BCrypt 암호화
        String encodedPassword = passwordEncoder.encode(request.getPassword());

        User user = User.create(
                request.getUserName(),
                request.getEmail(),
                encodedPassword,
                request.getUserRole(),
                false  // 회원가입은 firstLogin이 false
        );

        User savedUser = userRepository.save(user);
        log.info("회원가입 성공: {} (ID: {})", savedUser.getEmail(), savedUser.getUserId());

        return CreateUserResponse.builder()
                .userId(savedUser.getUserId())
                .userName(savedUser.getUserName())
                .email(savedUser.getEmail())
                .userRole(savedUser.getUserRole())
                .firstLoginFlag(savedUser.getFirstLoginFlag())
                .createdAt(savedUser.getCreatedAt())
                .build();
    }

    /**
     * 사용자 생성 (관리자 전용)
     */
    @Override
    @Transactional
    public CreateUserResponse createUser(CreateUserRequest request) {
        log.info("사용자 생성 요청: {}", request.getEmail());

        // 중복 이메일 검증
        if (userRepository.existsByEmail(request.getEmail())) {
            log.warn("이미 존재하는 이메일: {}", request.getEmail());
            throw new AuthenticationException(AuthErrorCode.AUTH_008, "이미 존재하는 이메일입니다");
        }

        // 임시 비밀번호 BCrypt 암호화
        String encodedPassword = passwordEncoder.encode(request.getTemporaryPassword());

        // User 엔티티 생성
        User user = User.create(
                request.getUserName(),
                request.getEmail(),
                encodedPassword,
                request.getUserRole(),
                true  // 첫 로그인 시 비밀번호 변경 필수
        );

        User savedUser = userRepository.save(user);

        log.info("사용자 생성 성공: {} ({})", savedUser.getEmail(), savedUser.getUserId());

        return CreateUserResponse.builder()
                .userId(savedUser.getUserId())
                .userName(savedUser.getUserName())
                .email(savedUser.getEmail())
                .userRole(savedUser.getUserRole())
                .firstLoginFlag(savedUser.getFirstLoginFlag())
                .createdAt(savedUser.getCreatedAt())
                .build();
    }

    /**
     * 로그아웃 - Access Token 블랙리스트 등록 + Refresh Token 무효화
     */
    @Override
    @Transactional
    public void logout(String accessToken, String refreshToken) {
        Long userId = jwtTokenProvider.getUserIdFromToken(accessToken);
        log.info("로그아웃 요청: userId={}", userId);

        // 1. Access Token 블랙리스트 등록 (남은 만료 시간만큼 TTL 설정)
        long remainingSeconds = jwtTokenProvider.getRemainingExpirationSeconds(accessToken);
        if (remainingSeconds > 0) {
            tokenBlacklistService.blacklist(accessToken, remainingSeconds);
        }

        // 2. Refresh Token 무효화 (전달된 경우)
        if (StringUtils.hasText(refreshToken)) {
            refreshTokenRepository.revokeByUserIdAndToken(userId, refreshToken);
        }

        log.info("로그아웃 완료: userId={}", userId);
    }

    /**
     * 전체 기기 로그아웃 - 모든 Refresh Token 무효화
     */
    @Override
    @Transactional
    public void logoutAllDevices(Long userId) {
        log.info("전체 기기 로그아웃 요청: userId={}", userId);

        int revokedCount = refreshTokenRepository.revokeAllByUserId(userId);

        log.info("전체 기기 로그아웃 완료: userId={}, revokedTokens={}", userId, revokedCount);
    }

    /**
     * Access Token 재발급
     */
    @Override
    @Transactional
    public TokenResponse refreshAccessToken(String refreshToken) {
        log.info("Access Token 재발급 요청");

        // 1. Refresh Token 검증
        RefreshToken storedToken = refreshTokenRepository.findByTokenAndRevokedFalse(refreshToken)
                .orElseThrow(() -> {
                    log.warn("유효하지 않은 Refresh Token");
                    return new AuthenticationException(AuthErrorCode.AUTH_004, "유효하지 않은 Refresh Token입니다");
                });

        // 2. 만료 확인
        if (!storedToken.isValid()) {
            log.warn("만료된 Refresh Token: userId={}", storedToken.getUserId());
            throw new AuthenticationException(AuthErrorCode.AUTH_005, "Refresh Token이 만료되었습니다");
        }

        // 3. 사용자 조회
        User user = userRepository.findById(storedToken.getUserId())
                .orElseThrow(() -> new AuthenticationException(AuthErrorCode.AUTH_009));

        // 4. 새 Access Token 발급
        String newAccessToken = jwtTokenProvider.generateAccessToken(
                user.getUserId(), user.getEmail(), user.getUserRole());

        log.info("Access Token 재발급 완료: userId={}", user.getUserId());

        return TokenResponse.builder()
                .accessToken(newAccessToken)
                .tokenType("Bearer")
                .expiresIn(jwtTokenProvider.getAccessTokenExpirationInSeconds())
                .build();
    }
}
