package com.skala.skip.ai.client;

import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.common.HealthCheckResponse;
import com.skala.skip.ai.dto.response.IssueDisclosuresAiResponse;
import com.skala.skip.ai.dto.response.StandardsDocumentAiResponse;
import com.skala.skip.ai.dto.response.StandardsIssuesAiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.HashMap;
import java.util.Map;

/**
 * ESG Standards AI Service Client
 * FastAPI ESG 표준 문서 관련 API 호출
 */
@Component
@Slf4j
public class StandardsAiClient extends AiServiceClient {

    private static final String BASE_PATH = "/internal/v1/standards";

    public StandardsAiClient(@Qualifier("aiServiceWebClient") WebClient webClient) {
        super(webClient);
    }

    /**
     * 한국 중대성 이슈 18개 목록 조회
     * GET /internal/v1/standards/issues
     */
    public Mono<AiApiResponse<StandardsIssuesAiResponse>> getIssues() {
        log.info("Getting Korean materiality issues list");
        return get(
                BASE_PATH + "/issues",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 이슈별 공시 요건 매핑 조회
     * GET /internal/v1/standards/issues/with-disclosures
     */
    public Mono<AiApiResponse<Object>> getIssuesWithDisclosures() {
        log.info("Getting issues with disclosure requirements");
        return get(
                BASE_PATH + "/issues/with-disclosures",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 특정 이슈 공시 요건 조회
     * GET /internal/v1/standards/issues/{issue_name}/disclosures
     */
    public Mono<AiApiResponse<IssueDisclosuresAiResponse>> getIssueDisclosures(String issueName) {
        log.info("Getting disclosures for issue: {}", issueName);
        return get(
                BASE_PATH + "/issues/" + issueName + "/disclosures",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * AI 기반 이슈 분석
     * GET /internal/v1/standards/issues/{issue_name}/analyze
     */
    public Mono<AiApiResponse<Object>> analyzeIssue(String issueName) {
        log.info("Analyzing issue: {}", issueName);
        return get(
                BASE_PATH + "/issues/" + issueName + "/analyze",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 공시 요건 검색
     * GET /internal/v1/standards/search
     */
    public Mono<AiApiResponse<Object>> searchDisclosures(String query) {
        log.info("Searching disclosures for: {}", query);
        Map<String, Object> params = new HashMap<>();
        params.put("query", query);
        return getWithParams(
                BASE_PATH + "/search",
                params,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 통계 정보 조회
     * GET /internal/v1/standards/statistics
     */
    public Mono<AiApiResponse<Object>> getStatistics() {
        log.info("Getting standards statistics");
        return get(
                BASE_PATH + "/statistics",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * GRI/SASB PDF 인덱싱
     * PATCH /internal/v1/standards/index
     */
    public Mono<AiApiResponse<Object>> indexDocuments() {
        log.info("Indexing GRI/SASB documents");
        return patch(
                BASE_PATH + "/index",
                null,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * ChromaDB 리셋
     * POST /internal/v1/standards/reset
     */
    public Mono<AiApiResponse<Object>> resetChromaDB() {
        log.info("Resetting ChromaDB");
        return postWithoutBody(
                BASE_PATH + "/reset",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 인덱싱 문서 수 조회
     * GET /internal/v1/standards/count
     */
    public Mono<AiApiResponse<Object>> getDocumentCount() {
        log.info("Getting indexed document count");
        return get(
                BASE_PATH + "/count",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 문서 목록 조회
     * GET /internal/v1/standards/documents
     */
    public Mono<AiApiResponse<StandardsDocumentAiResponse>> getDocuments() {
        log.info("Getting standards documents list");
        return get(
                BASE_PATH + "/documents",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 문서 삭제
     * DELETE /internal/v1/standards/documents/{document_id}
     */
    public Mono<AiApiResponse<Object>> deleteDocument(String documentId) {
        log.info("Deleting standards document: {}", documentId);
        return delete(
                BASE_PATH + "/documents/" + documentId,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 문서 임베딩 시작
     * POST /internal/v1/standards/documents/embed
     */
    public Mono<AiApiResponse<Object>> embedDocuments() {
        log.info("Starting document embedding");
        return postWithoutBody(
                BASE_PATH + "/documents/embed",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 헬스체크
     * GET /internal/v1/standards/health
     */
    public Mono<HealthCheckResponse> healthCheck() {
        log.info("Checking standards service health");
        return webClient.get()
                .uri(BASE_PATH + "/health")
                .retrieve()
                .bodyToMono(HealthCheckResponse.class)
                .doOnSuccess(r -> log.info("Standards service health: {}", r.getStatus()))
                .doOnError(e -> log.error("Standards service health check failed: {}", e.getMessage()));
    }
}
