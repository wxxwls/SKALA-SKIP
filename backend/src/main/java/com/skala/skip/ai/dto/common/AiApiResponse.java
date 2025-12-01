package com.skala.skip.ai.dto.common;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * FastAPI AI 서비스 공통 응답 래퍼
 * 모든 AI 서비스 응답은 이 형식을 따름
 *
 * @param <T> 응답 데이터 타입
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiApiResponse<T> {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("data")
    private T data;

    @JsonProperty("error")
    private AiErrorInfo error;

    /**
     * 에러 여부 확인
     */
    public boolean hasError() {
        return !success || error != null;
    }

    /**
     * 데이터 존재 여부 확인
     */
    public boolean hasData() {
        return success && data != null;
    }
}
