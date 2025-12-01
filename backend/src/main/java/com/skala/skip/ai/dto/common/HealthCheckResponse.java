package com.skala.skip.ai.dto.common;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * AI 서비스 헬스체크 응답
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class HealthCheckResponse {

    @JsonProperty("status")
    private String status;

    @JsonProperty("service")
    private String service;

    @JsonProperty("timestamp")
    private String timestamp;

    /**
     * 서비스 정상 여부 확인
     */
    public boolean isHealthy() {
        return "ok".equalsIgnoreCase(status) || "healthy".equalsIgnoreCase(status);
    }
}
