package com.skala.skip.ai.client;

import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.common.HealthCheckResponse;
import com.skala.skip.ai.dto.request.ReportGenerateAiRequest;
import com.skala.skip.ai.dto.request.ReportModifyAiRequest;
import com.skala.skip.ai.dto.response.ReportGenerateAiResponse;
import com.skala.skip.ai.dto.response.ReportModifyAiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

/**
 * Report AI Service Client
 * FastAPI 보고서 생성 관련 API 호출
 */
@Component
@Slf4j
public class ReportAiClient extends AiServiceClient {

    private static final String BASE_PATH = "/internal/v1/reports";

    public ReportAiClient(@Qualifier("aiServiceWebClient") WebClient webClient) {
        super(webClient);
    }

    /**
     * ESG 보고서 생성
     * POST /internal/v1/reports/generate
     */
    public Mono<AiApiResponse<ReportGenerateAiResponse>> generateReport(ReportGenerateAiRequest request) {
        log.info("Generating report for company: {}", request.getCompanyContext().getCompanyName());
        return post(
                BASE_PATH + "/generate",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 보고서 수정 (자연어 명령)
     * POST /internal/v1/reports/modify
     */
    public Mono<AiApiResponse<ReportModifyAiResponse>> modifyReport(ReportModifyAiRequest request) {
        log.info("Modifying report for company: {} with instruction: {}",
                request.getCompanyName(), request.getInstruction());
        return post(
                BASE_PATH + "/modify",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 헬스체크
     * GET /internal/v1/reports/health
     */
    public Mono<HealthCheckResponse> healthCheck() {
        log.info("Checking report service health");
        return webClient.get()
                .uri(BASE_PATH + "/health")
                .retrieve()
                .bodyToMono(HealthCheckResponse.class)
                .doOnSuccess(r -> log.info("Report service health: {}", r.getStatus()))
                .doOnError(e -> log.error("Report service health check failed: {}", e.getMessage()));
    }
}
