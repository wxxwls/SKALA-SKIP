package com.skala.skip.auth.exception;

/**
 * Exception thrown when account is locked
 */
public class AccountLockedException extends AuthenticationException {

    public AccountLockedException() {
        super(AuthErrorCode.AUTH_002);
    }

    public AccountLockedException(String details) {
        super(AuthErrorCode.AUTH_002, details);
    }
}
