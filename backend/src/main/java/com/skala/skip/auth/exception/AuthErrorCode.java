package com.skala.skip.auth.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

/**
 * Authentication error codes
 * Ref: authentication_login_standard.md - Section 9
 */
@Getter
@RequiredArgsConstructor
public enum AuthErrorCode {

    // Authentication errors
    AUTH_001("AUTH-001", "Invalid credentials"),
    AUTH_002("AUTH-002", "Account is locked"),
    AUTH_003("AUTH-003", "Missing authentication token"),
    AUTH_004("AUTH-004", "Invalid or expired token"),
    AUTH_005("AUTH-005", "Access denied - insufficient permissions"),

    // Password errors
    AUTH_006("AUTH-006", "Current password is incorrect"),
    AUTH_007("AUTH-007", "New password does not meet requirements"),
    AUTH_008("AUTH-008", "Password change required on first login"),

    // User not found
    AUTH_009("AUTH-009", "User not found"),

    // Token errors
    AUTH_010("AUTH-010", "Invalid or expired refresh token"),

    // Logout errors
    AUTH_011("AUTH-011", "Token has been revoked"),
    AUTH_012("AUTH-012", "Logout failed");

    private final String code;
    private final String message;
}
