package com.skala.skip.carbon.service.impl;

import com.skala.skip.ai.client.CarbonAiClient;
import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.response.CarbonSignalsAiResponse;
import com.skala.skip.ai.exception.AiServiceException;
import com.skala.skip.carbon.dto.response.CarbonSignalsResponse;
import com.skala.skip.carbon.service.CarbonService;
import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.stream.Collectors;

/**
 * 탄소 거래 서비스 구현
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class CarbonServiceImpl implements CarbonService {

    private final CarbonAiClient carbonAiClient;

    @Override
    public CarbonSignalsResponse getSignals() {
        log.info("탄소 거래 시그널 조회");

        try {
            AiApiResponse<CarbonSignalsAiResponse> response = carbonAiClient.getSignals().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.CRB_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                throw new AiServiceException(ESGErrorCode.CRB_AI_002, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.CRB_AI_002, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            CarbonSignalsResponse result = mapToResponse(response.getData());
            log.info("탄소 거래 시그널 조회 완료 - count: {}", result.getCount());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("탄소 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.CRB_AI_001, "탄소 거래 처리 중 오류 발생: " + e.getMessage(), e);
        }
    }

    private CarbonSignalsResponse mapToResponse(CarbonSignalsAiResponse data) {
        return CarbonSignalsResponse.builder()
                .count(data.getCount())
                .signals(data.getSignals() != null ? data.getSignals().stream()
                        .map(s -> CarbonSignalsResponse.CarbonSignal.builder()
                                .signal(s.getSignal())
                                .confidence(s.getConfidence())
                                .predictedPrice(s.getPredictedPrice())
                                .currentPrice(s.getCurrentPrice())
                                .priceChangePercent(s.getPriceChangePercent())
                                .recommendation(s.getRecommendation())
                                .analysisDate(s.getAnalysisDate())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }
}
