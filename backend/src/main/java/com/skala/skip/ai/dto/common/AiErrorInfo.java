package com.skala.skip.ai.dto.common;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * FastAPI AI 서비스 에러 정보
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiErrorInfo {

    @JsonProperty("code")
    private String code;

    @JsonProperty("message")
    private String message;
}
