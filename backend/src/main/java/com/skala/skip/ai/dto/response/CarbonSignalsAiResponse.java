package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 탄소 거래 시그널 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CarbonSignalsAiResponse {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("signals")
    private List<CarbonSignal> signals;

    @JsonProperty("count")
    private int count;

    /**
     * 탄소 거래 시그널 정보
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CarbonSignal {

        @JsonProperty("signal")
        private String signal;

        @JsonProperty("confidence")
        private double confidence;

        @JsonProperty("predicted_price")
        private double predictedPrice;

        @JsonProperty("current_price")
        private double currentPrice;

        @JsonProperty("price_change_percent")
        private double priceChangePercent;

        @JsonProperty("recommendation")
        private String recommendation;

        @JsonProperty("analysis_date")
        private String analysisDate;
    }
}
