package com.skala.skip.ai.client;

import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.common.HealthCheckResponse;
import com.skala.skip.ai.dto.request.IssuePoolGenerateAiRequest;
import com.skala.skip.ai.dto.request.ScoreTopicAiRequest;
import com.skala.skip.ai.dto.response.IssuePoolAiResponse;
import com.skala.skip.ai.dto.response.ScoreTopicAiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

/**
 * Issue Pool AI Service Client
 * FastAPI 이슈풀 관련 API 호출
 */
@Component
@Slf4j
public class IssuePoolAiClient extends AiServiceClient {

    private static final String BASE_PATH = "/internal/v1/issue-pools";

    public IssuePoolAiClient(@Qualifier("aiServiceWebClient") WebClient webClient) {
        super(webClient);
    }

    /**
     * ESG 이슈풀 생성 요청
     * POST /internal/v1/issue-pools/generate
     */
    public Mono<AiApiResponse<IssuePoolAiResponse>> generateIssuePool(IssuePoolGenerateAiRequest request) {
        log.info("Generating issue pool for company: {}", request.getCompanyContext().getCompanyId());
        return post(
                BASE_PATH + "/generate",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 단일 토픽 이중중대성 점수화 요청
     * POST /internal/v1/issue-pools/score-topic
     */
    public Mono<AiApiResponse<ScoreTopicAiResponse>> scoreTopic(ScoreTopicAiRequest request) {
        log.info("Scoring topic: {} for company: {}", request.getTopicTitle(), request.getCompanyContext().getCompanyId());
        return post(
                BASE_PATH + "/score-topic",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 표준 문서 업로드 (GRI, SASB 등)
     * PATCH /internal/v1/issue-pools/s_upload
     */
    public Mono<AiApiResponse<Object>> uploadStandardDocument(Object request) {
        log.info("Uploading standard document");
        return patch(
                BASE_PATH + "/s_upload",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 벤치마킹 문서 업로드
     * PATCH /internal/v1/issue-pools/b_upload
     */
    public Mono<AiApiResponse<Object>> uploadBenchmarkDocument(Object request) {
        log.info("Uploading benchmark document");
        return patch(
                BASE_PATH + "/b_upload",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 헬스체크
     * GET /internal/v1/issue-pools/health
     */
    public Mono<HealthCheckResponse> healthCheck() {
        log.info("Checking issue pool service health");
        return webClient.get()
                .uri(BASE_PATH + "/health")
                .retrieve()
                .bodyToMono(HealthCheckResponse.class)
                .doOnSuccess(r -> log.info("Issue pool service health: {}", r.getStatus()))
                .doOnError(e -> log.error("Issue pool service health check failed: {}", e.getMessage()));
    }
}
