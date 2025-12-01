package com.skala.skip.ai.exception;

import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import lombok.Getter;

/**
 * AI 서비스 호출 관련 예외
 * FastAPI AI 서비스 연동 시 발생하는 예외를 처리
 */
@Getter
public class AiServiceException extends BusinessException {

    private final String responseBody;
    private final Integer httpStatus;

    public AiServiceException(ESGErrorCode errorCode) {
        super(errorCode);
        this.responseBody = null;
        this.httpStatus = null;
    }

    public AiServiceException(ESGErrorCode errorCode, String details) {
        super(errorCode, details);
        this.responseBody = null;
        this.httpStatus = null;
    }

    public AiServiceException(ESGErrorCode errorCode, String details, String responseBody) {
        super(errorCode, details);
        this.responseBody = responseBody;
        this.httpStatus = null;
    }

    public AiServiceException(ESGErrorCode errorCode, String details, String responseBody, Integer httpStatus) {
        super(errorCode, details);
        this.responseBody = responseBody;
        this.httpStatus = httpStatus;
    }

    public AiServiceException(ESGErrorCode errorCode, String details, Throwable cause) {
        super(errorCode, details, cause);
        this.responseBody = null;
        this.httpStatus = null;
    }
}
