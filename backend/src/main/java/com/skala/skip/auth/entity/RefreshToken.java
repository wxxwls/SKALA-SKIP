package com.skala.skip.auth.entity;

import com.skala.skip.common.entity.BaseTimeEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Refresh Token 엔티티
 * JWT Refresh Token을 PostgreSQL에 저장하여 관리
 * - Refresh Token은 Redis/DB에만 저장
 * - 로그아웃 시 해당 토큰 무효화 (revoked = true)
 */
@Entity
@Table(name = "refresh_tokens")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class RefreshToken extends BaseTimeEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "token", nullable = false, unique = true, length = 512)
    private String token;

    @Column(name = "device_info", length = 255)
    private String deviceInfo;

    @Column(name = "expires_at", nullable = false)
    private LocalDateTime expiresAt;

    @Column(name = "revoked", nullable = false)
    private Boolean revoked;

    /**
     * Refresh Token 생성 팩토리 메서드
     * @param userId 사용자 ID
     * @param token JWT Refresh Token
     * @param deviceInfo 디바이스 정보 (User-Agent 등)
     * @param expiresAt 만료 시간
     * @return RefreshToken 엔티티
     */
    public static RefreshToken create(Long userId, String token, String deviceInfo, LocalDateTime expiresAt) {
        RefreshToken refreshToken = new RefreshToken();
        refreshToken.userId = userId;
        refreshToken.token = token;
        refreshToken.deviceInfo = deviceInfo;
        refreshToken.expiresAt = expiresAt;
        refreshToken.revoked = false;
        return refreshToken;
    }

    /**
     * 토큰 무효화 (로그아웃 시 호출)
     */
    public void revoke() {
        this.revoked = true;
    }

    /**
     * 토큰 유효성 확인
     * @return 유효 여부 (무효화되지 않고 만료되지 않은 경우 true)
     */
    public boolean isValid() {
        return !this.revoked && this.expiresAt.isAfter(LocalDateTime.now());
    }
}
