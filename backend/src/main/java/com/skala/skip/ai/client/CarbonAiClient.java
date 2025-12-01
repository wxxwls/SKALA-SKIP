package com.skala.skip.ai.client;

import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.common.HealthCheckResponse;
import com.skala.skip.ai.dto.response.CarbonSignalsAiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

/**
 * Carbon Trading AI Service Client
 * FastAPI 탄소 거래 시그널 관련 API 호출
 */
@Component
@Slf4j
public class CarbonAiClient extends AiServiceClient {

    private static final String BASE_PATH = "/internal/v1/carbon";

    public CarbonAiClient(@Qualifier("aiServiceWebClient") WebClient webClient) {
        super(webClient);
    }

    /**
     * 탄소 거래 시그널 조회 (BUY/SELL/HOLD)
     * GET /internal/v1/carbon/signals
     */
    public Mono<AiApiResponse<CarbonSignalsAiResponse>> getSignals() {
        log.info("Getting carbon trading signals");
        return get(
                BASE_PATH + "/signals",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 헬스체크
     * GET /internal/v1/carbon/health
     */
    public Mono<HealthCheckResponse> healthCheck() {
        log.info("Checking carbon service health");
        return webClient.get()
                .uri(BASE_PATH + "/health")
                .retrieve()
                .bodyToMono(HealthCheckResponse.class)
                .doOnSuccess(r -> log.info("Carbon service health: {}", r.getStatus()))
                .doOnError(e -> log.error("Carbon service health check failed: {}", e.getMessage()));
    }
}
