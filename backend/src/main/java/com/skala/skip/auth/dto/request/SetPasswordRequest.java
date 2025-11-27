package com.skala.skip.auth.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * Set password request DTO (for first login)
 * 최초 로그인 시 비밀번호 설정용 - 현재 비밀번호 불필요
 */
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class SetPasswordRequest {

    @NotBlank(message = "New password is required")
    @Pattern(
            regexp = "^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,}$",
            message = "Password must be at least 8 characters with letters, numbers, and special characters"
    )
    private String newPassword;
}
