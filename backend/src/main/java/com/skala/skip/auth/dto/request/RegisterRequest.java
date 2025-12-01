package com.skala.skip.auth.dto.request;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * 회원가입 요청 DTO
 */
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class RegisterRequest {

    @NotBlank(message = "User name is required")
    private String userName;

    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    private String email;

    @NotBlank(message = "Password is required")
    private String password;

    @NotBlank(message = "User role is required")
    @Pattern(
            regexp = "^(ROLE_USER|ROLE_ESG_PM|ROLE_EXECUTIVE|ROLE_ADMIN)$",
            message = "Invalid role. Must be one of: ROLE_USER, ROLE_ESG_PM, ROLE_EXECUTIVE, ROLE_ADMIN"
    )
    private String userRole;
}
