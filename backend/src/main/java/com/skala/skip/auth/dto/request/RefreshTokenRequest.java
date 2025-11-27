package com.skala.skip.auth.dto.request;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * Access Token 재발급 요청 DTO
 */
@Getter
@NoArgsConstructor
@Schema(description = "Access Token 재발급 요청")
public class RefreshTokenRequest {

    @NotBlank(message = "Refresh Token은 필수입니다")
    @Schema(description = "JWT Refresh Token", example = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    private String refreshToken;
}
