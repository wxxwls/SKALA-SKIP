package com.skala.skip.auth.exception;

import lombok.Getter;

/**
 * Exception thrown when login credentials are invalid
 * Ref: authentication_login_standard.md - Section 5.2
 */
@Getter
public class InvalidCredentialsException extends AuthenticationException {

    private final Integer remainingAttempts;

    public InvalidCredentialsException() {
        super(AuthErrorCode.AUTH_001);
        this.remainingAttempts = null;
    }

    public InvalidCredentialsException(String details) {
        super(AuthErrorCode.AUTH_001, details);
        this.remainingAttempts = null;
    }

    public InvalidCredentialsException(String details, int remainingAttempts) {
        super(AuthErrorCode.AUTH_001, details);
        this.remainingAttempts = remainingAttempts;
    }
}
