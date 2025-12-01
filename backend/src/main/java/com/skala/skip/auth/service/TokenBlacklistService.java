package com.skala.skip.auth.service;

/**
 * Token Blacklist Service 인터페이스
 * 로그아웃된 Access Token을 Redis에 저장하여 무효화
 */
public interface TokenBlacklistService {

    /**
     * Access Token을 블랙리스트에 추가
     * @param token JWT Access Token
     * @param expirationInSeconds 토큰 남은 만료 시간(초)
     */
    void blacklist(String token, long expirationInSeconds);

    /**
     * 토큰이 블랙리스트에 있는지 확인
     * @param token JWT Access Token
     * @return 블랙리스트 여부 (true: 무효화된 토큰)
     */
    boolean isBlacklisted(String token);
}
