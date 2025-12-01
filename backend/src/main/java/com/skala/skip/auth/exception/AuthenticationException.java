package com.skala.skip.auth.exception;

import lombok.Getter;

/**
 * Base authentication exception
 * All authentication-related exceptions extend this class
 */
@Getter
public class AuthenticationException extends RuntimeException {

    private final AuthErrorCode errorCode;
    private final String details;

    public AuthenticationException(AuthErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
        this.details = null;
    }

    public AuthenticationException(AuthErrorCode errorCode, String details) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
        this.details = details;
    }

    public AuthenticationException(AuthErrorCode errorCode, String details, Throwable cause) {
        super(errorCode.getMessage(), cause);
        this.errorCode = errorCode;
        this.details = details;
    }
}
