package com.skala.skip.auth.dto.response;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Builder;
import lombok.Getter;

/**
 * Token 응답 DTO
 * Access Token 재발급 시 사용
 */
@Getter
@Builder
@Schema(description = "토큰 응답")
public class TokenResponse {

    @Schema(description = "JWT Access Token", example = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    private String accessToken;

    @Schema(description = "JWT Refresh Token (최초 로그인 시에만 포함)", example = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    private String refreshToken;

    @Schema(description = "토큰 타입", example = "Bearer")
    private String tokenType;

    @Schema(description = "Access Token 만료 시간(초)", example = "3600")
    private Long expiresIn;
}
