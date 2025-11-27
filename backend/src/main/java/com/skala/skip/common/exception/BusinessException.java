package com.skala.skip.common.exception;

import lombok.Getter;

@Getter
public class BusinessException extends RuntimeException {
    private final ESGErrorCode errorCode;
    private final String details;

    public BusinessException(ESGErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
        this.details = null;
    }

    public BusinessException(ESGErrorCode errorCode, String details) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
        this.details = details;
    }

    public BusinessException(ESGErrorCode errorCode, String details, Throwable cause) {
        super(errorCode.getMessage(), cause);
        this.errorCode = errorCode;
        this.details = details;
    }
}

