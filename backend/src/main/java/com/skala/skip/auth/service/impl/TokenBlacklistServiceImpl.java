package com.skala.skip.auth.service.impl;

import com.skala.skip.auth.service.TokenBlacklistService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.RedisConnectionFailureException;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

/**
 * Token Blacklist Service 구현체
 * Redis를 사용하여 로그아웃된 Access Token을 관리
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TokenBlacklistServiceImpl implements TokenBlacklistService {

    private final StringRedisTemplate stringRedisTemplate;

    /**
     * Redis Key Prefix
     * 네이밍 규칙: auth:blacklist:{token}
     */
    private static final String BLACKLIST_PREFIX = "auth:blacklist:";

    /**
     * 블랙리스트 등록 값
     */
    private static final String REVOKED_VALUE = "revoked";

    @Override
    public void blacklist(String token, long expirationInSeconds) {
        if (expirationInSeconds <= 0) {
            log.debug("Token already expired, skipping blacklist");
            return;
        }

        try {
            String key = BLACKLIST_PREFIX + token;
            stringRedisTemplate.opsForValue().set(key, REVOKED_VALUE, expirationInSeconds, TimeUnit.SECONDS);
            log.info("Token blacklisted, TTL: {} seconds", expirationInSeconds);
        } catch (RedisConnectionFailureException e) {
            log.error("Redis connection failed while blacklisting token: {}", e.getMessage());
            // Redis 장애 시에도 로그아웃 처리는 진행 (가용성 우선)
        }
    }

    @Override
    public boolean isBlacklisted(String token) {
        try {
            String key = BLACKLIST_PREFIX + token;
            Boolean exists = stringRedisTemplate.hasKey(key);
            return Boolean.TRUE.equals(exists);
        } catch (RedisConnectionFailureException e) {
            log.error("Redis connection failed while checking blacklist: {}", e.getMessage());
            // Redis 장애 시 정책:
            // - 가용성 우선: false 반환 (요청 허용)
            // - 보안 우선: true 반환 (요청 거부)
            // 현재는 가용성 우선으로 설정
            return false;
        }
    }
}
