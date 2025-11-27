package com.skala.skip.auth.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Create user response DTO
 * Ref: authentication_login_standard.md - Section 7.2
 */
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateUserResponse {

    private Long userId;
    private String userName;
    private String email;
    private String userRole;
    private Boolean firstLoginFlag;
    private LocalDateTime createdAt;
}
