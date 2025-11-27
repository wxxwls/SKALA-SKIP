package com.skala.skip.auth.service.impl;

import com.skala.skip.auth.entity.User;
import com.skala.skip.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

/**
 * 로그인 시도 관리 서비스
 * 로그인 실패 횟수 관리 및 계정 잠금 처리
 * Ref: authentication_login_standard.md - Section 5.2
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class LoginAttemptService {

    private final UserRepository userRepository;

    @Value("${app.security.max-login-attempts:5}")
    private int maxLoginAttempts;

    /**
     * 로그인 실패 처리 (별도 트랜잭션으로 실행)
     * @param userId 사용자 ID
     * @return 남은 로그인 시도 횟수
     */
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public int handleFailedLogin(Long userId) {
        // 새 트랜잭션에서 사용자를 다시 조회
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found: " + userId));

        user.incrementLoginFailCount();

        int remainingAttempts = maxLoginAttempts - user.getLoginFailCount();

        if (remainingAttempts <= 0) {
            user.lockAccount();
            log.warn("{}회 로그인 실패로 계정 잠금: {}", maxLoginAttempts, user.getEmail());
            remainingAttempts = 0;
        }

        userRepository.saveAndFlush(user);

        log.info("로그인 실패: {} (남은 시도 횟수: {})", user.getEmail(), remainingAttempts);

        return remainingAttempts;
    }

    /**
     * 로그인 성공 시 실패 횟수 초기화
     * @param userId 사용자 ID
     */
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void resetFailCount(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found: " + userId));

        user.resetLoginFailCount();
        userRepository.saveAndFlush(user);
    }
}
