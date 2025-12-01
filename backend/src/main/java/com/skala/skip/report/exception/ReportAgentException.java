package com.skala.skip.report.exception;

import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import lombok.Getter;

@Getter
public class ReportAgentException extends BusinessException {
    private final String responseBody;

    public ReportAgentException(ESGErrorCode errorCode, String responseBody) {
        super(errorCode, responseBody);
        this.responseBody = responseBody;
    }

    public ReportAgentException(ESGErrorCode errorCode, String responseBody, Throwable cause) {
        super(errorCode, responseBody, cause);
        this.responseBody = responseBody;
    }
}

