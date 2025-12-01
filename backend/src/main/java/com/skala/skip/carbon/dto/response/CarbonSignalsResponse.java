package com.skala.skip.carbon.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * 탄소 거래 시그널 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CarbonSignalsResponse {

    private List<CarbonSignal> signals;
    private int count;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CarbonSignal {
        private String signal;
        private double confidence;
        private double predictedPrice;
        private double currentPrice;
        private double priceChangePercent;
        private String recommendation;
        private String analysisDate;
    }
}
