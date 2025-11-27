package com.skala.skip.auth.util;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

/**
 * JWT Token Provider
 * Handles JWT token generation and validation
 * Ref: authentication_login_standard.md - Section 4.2
 */
@Component
@Slf4j
public class JwtTokenProvider {

    private final SecretKey secretKey;
    private final long accessTokenExpiration;
    private final long refreshTokenExpiration;

    public JwtTokenProvider(
            @Value("${app.security.jwt-secret}") String jwtSecret,
            @Value("${app.security.jwt-expiration}") long accessTokenExpiration,
            @Value("${app.security.jwt-refresh-expiration}") long refreshTokenExpiration
    ) {
        // Validate JWT secret length (minimum 256 bits / 32 bytes for HS256)
        if (jwtSecret == null || jwtSecret.getBytes(StandardCharsets.UTF_8).length < 32) {
            throw new IllegalArgumentException(
                "JWT secret must be at least 32 characters (256 bits) for HS256 algorithm. " +
                "Please set a secure JWT_SECRET environment variable."
            );
        }

        // Security check: prevent using default/weak secrets in production
        if ("changeme".equalsIgnoreCase(jwtSecret) ||
            jwtSecret.contains("changeme") ||
            jwtSecret.contains("default") ||
            jwtSecret.contains("secret")) {
            log.warn("SECURITY WARNING: Using weak or default JWT secret. " +
                    "Please set a strong JWT_SECRET environment variable in production!");
        }

        this.secretKey = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        this.accessTokenExpiration = accessTokenExpiration;
        this.refreshTokenExpiration = refreshTokenExpiration;
    }

    /**
     * Generate access token
     * @param userId User ID
     * @param email User email
     * @param role User role
     * @return JWT access token
     */
    public String generateAccessToken(Long userId, String email, String role) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + accessTokenExpiration);

        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("email", email)
                .claim("role", role)
                .issuedAt(now)
                .expiration(expiryDate)
                .signWith(secretKey)
                .compact();
    }

    /**
     * Generate refresh token
     * @param userId User ID
     * @return JWT refresh token
     */
    public String generateRefreshToken(Long userId) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + refreshTokenExpiration);

        return Jwts.builder()
                .subject(String.valueOf(userId))
                .issuedAt(now)
                .expiration(expiryDate)
                .signWith(secretKey)
                .compact();
    }

    /**
     * Extract user ID from token
     * @param token JWT token
     * @return User ID
     */
    public Long getUserIdFromToken(String token) {
        Claims claims = parseToken(token);
        return Long.parseLong(claims.getSubject());
    }

    /**
     * Extract email from token
     * @param token JWT token
     * @return User email
     */
    public String getEmailFromToken(String token) {
        Claims claims = parseToken(token);
        return claims.get("email", String.class);
    }

    /**
     * Extract role from token
     * @param token JWT token
     * @return User role
     */
    public String getRoleFromToken(String token) {
        Claims claims = parseToken(token);
        return claims.get("role", String.class);
    }

    /**
     * Validate token
     * @param token JWT token
     * @return true if valid, false otherwise
     */
    public boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (SecurityException | MalformedJwtException e) {
            log.error("Invalid JWT signature: {}", e.getMessage());
        } catch (ExpiredJwtException e) {
            log.error("Expired JWT token: {}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            log.error("Unsupported JWT token: {}", e.getMessage());
        } catch (IllegalArgumentException e) {
            log.error("JWT claims string is empty: {}", e.getMessage());
        }
        return false;
    }

    /**
     * Parse and validate token
     * @param token JWT token
     * @return Claims
     */
    private Claims parseToken(String token) {
        return Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    /**
     * Get expiration time in seconds
     * @return Access token expiration in seconds
     */
    public long getAccessTokenExpirationInSeconds() {
        return accessTokenExpiration / 1000;
    }

    /**
     * Get refresh token expiration in seconds
     * @return Refresh token expiration in seconds
     */
    public long getRefreshTokenExpirationInSeconds() {
        return refreshTokenExpiration / 1000;
    }

    /**
     * Get refresh token expiration in milliseconds
     * @return Refresh token expiration in milliseconds
     */
    public long getRefreshTokenExpirationInMillis() {
        return refreshTokenExpiration;
    }

    /**
     * 토큰의 남은 만료 시간(초) 계산
     * @param token JWT token
     * @return 남은 만료 시간(초), 이미 만료된 경우 0
     */
    public long getRemainingExpirationSeconds(String token) {
        try {
            Claims claims = parseToken(token);
            Date expiration = claims.getExpiration();
            long remainingMillis = expiration.getTime() - System.currentTimeMillis();
            return remainingMillis > 0 ? remainingMillis / 1000 : 0;
        } catch (ExpiredJwtException e) {
            return 0;
        }
    }
}
