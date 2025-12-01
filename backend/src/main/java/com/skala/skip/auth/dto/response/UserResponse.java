package com.skala.skip.auth.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * User information response DTO
 * Used for /api/v1/auth/me endpoint
 */
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserResponse {

    private Long userId;
    private String userName;
    private String email;
    private String userRole;
    private Boolean firstLoginFlag;
    private Boolean accountLocked;
    private LocalDateTime passwordUpdatedAt;
    private LocalDateTime createdAt;
}
