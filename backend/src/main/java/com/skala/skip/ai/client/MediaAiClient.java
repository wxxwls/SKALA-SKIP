package com.skala.skip.ai.client;

import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.common.HealthCheckResponse;
import com.skala.skip.ai.dto.request.AnalyzeNewsAiRequest;
import com.skala.skip.ai.dto.response.AnalyzeNewsAiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

/**
 * Media Analysis AI Service Client
 * FastAPI 뉴스/미디어 분석 관련 API 호출
 */
@Component
@Slf4j
public class MediaAiClient extends AiServiceClient {

    private static final String BASE_PATH = "/internal/v1/media";

    public MediaAiClient(@Qualifier("aiServiceWebClient") WebClient webClient) {
        super(webClient);
    }

    /**
     * 저장된 미디어 분석 데이터 조회
     * GET /internal/v1/media
     */
    public Mono<AiApiResponse<Object>> getMediaData() {
        log.info("Getting stored media analysis data");
        return get(
                BASE_PATH,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 키워드 기반 뉴스 수집 및 분석
     * POST /internal/v1/media/analyze
     */
    public Mono<AiApiResponse<AnalyzeNewsAiResponse>> analyzeNews(AnalyzeNewsAiRequest request) {
        log.info("Analyzing news for keywords: {}", request.getKeywords());
        return post(
                BASE_PATH + "/analyze",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 사전 수집 기사 분석
     * POST /internal/v1/media/analyze-articles
     */
    public Mono<AiApiResponse<Object>> analyzeArticles(Object request) {
        log.info("Analyzing pre-collected articles");
        return post(
                BASE_PATH + "/analyze-articles",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * ESG 18개 이슈 정의 조회
     * GET /internal/v1/media/issues
     */
    public Mono<AiApiResponse<Object>> getEsgIssues() {
        log.info("Getting ESG 18 issues definition");
        return get(
                BASE_PATH + "/issues",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 헬스체크
     * GET /internal/v1/media/health
     */
    public Mono<HealthCheckResponse> healthCheck() {
        log.info("Checking media service health");
        return webClient.get()
                .uri(BASE_PATH + "/health")
                .retrieve()
                .bodyToMono(HealthCheckResponse.class)
                .doOnSuccess(r -> log.info("Media service health: {}", r.getStatus()))
                .doOnError(e -> log.error("Media service health check failed: {}", e.getMessage()));
    }
}
