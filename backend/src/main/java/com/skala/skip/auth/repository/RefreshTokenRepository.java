package com.skala.skip.auth.repository;

import com.skala.skip.auth.entity.RefreshToken;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Optional;

/**
 * Refresh Token Repository
 */
@Repository
public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {

    /**
     * 유효한 Refresh Token 조회
     * @param token JWT Refresh Token
     * @return RefreshToken (revoked = false인 토큰)
     */
    Optional<RefreshToken> findByTokenAndRevokedFalse(String token);

    /**
     * 사용자의 모든 Refresh Token 무효화 (전체 기기 로그아웃)
     * @param userId 사용자 ID
     * @return 업데이트된 레코드 수
     */
    @Modifying
    @Query("UPDATE RefreshToken rt SET rt.revoked = true WHERE rt.userId = :userId AND rt.revoked = false")
    int revokeAllByUserId(@Param("userId") Long userId);

    /**
     * 특정 토큰 무효화 (단일 기기 로그아웃)
     * @param userId 사용자 ID
     * @param token JWT Refresh Token
     * @return 업데이트된 레코드 수
     */
    @Modifying
    @Query("UPDATE RefreshToken rt SET rt.revoked = true WHERE rt.userId = :userId AND rt.token = :token")
    int revokeByUserIdAndToken(@Param("userId") Long userId, @Param("token") String token);

    /**
     * 만료된 Refresh Token 삭제 (스케줄러에서 호출)
     * @param now 현재 시간
     * @return 삭제된 레코드 수
     */
    @Modifying
    @Query("DELETE FROM RefreshToken rt WHERE rt.expiresAt < :now OR rt.revoked = true")
    int deleteExpiredOrRevokedTokens(@Param("now") LocalDateTime now);

    /**
     * 사용자의 유효한 Refresh Token 수 조회
     * @param userId 사용자 ID
     * @return 유효한 토큰 수
     */
    @Query("SELECT COUNT(rt) FROM RefreshToken rt WHERE rt.userId = :userId AND rt.revoked = false AND rt.expiresAt > :now")
    long countValidTokensByUserId(@Param("userId") Long userId, @Param("now") LocalDateTime now);
}
