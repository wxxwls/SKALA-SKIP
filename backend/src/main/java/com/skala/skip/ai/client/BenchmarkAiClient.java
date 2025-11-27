package com.skala.skip.ai.client;

import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.common.HealthCheckResponse;
import com.skala.skip.ai.dto.request.BenchmarkAnalyzeAiRequest;
import com.skala.skip.ai.dto.response.BenchmarkAnalyzeAiResponse;
import com.skala.skip.ai.dto.response.BenchmarkDocumentAiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

/**
 * Benchmark AI Service Client
 * FastAPI 벤치마킹 분석 관련 API 호출
 */
@Component
@Slf4j
public class BenchmarkAiClient extends AiServiceClient {

    private static final String BASE_PATH = "/internal/v1/benchmarks";

    public BenchmarkAiClient(@Qualifier("aiServiceWebClient") WebClient webClient) {
        super(webClient);
    }

    /**
     * 키워드 기반 분석
     * POST /internal/v1/benchmarks/analyze
     */
    public Mono<AiApiResponse<BenchmarkAnalyzeAiResponse>> analyze(BenchmarkAnalyzeAiRequest request) {
        log.info("Analyzing benchmark for keyword: {}", request.getKeyword());
        return post(
                BASE_PATH + "/analyze",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * SK 18개 이슈 기반 분석
     * POST /internal/v1/benchmarks/analyze-issues
     */
    public Mono<AiApiResponse<Object>> analyzeIssues(String companyName, String pdfPath) {
        log.info("Analyzing issues for company: {}", companyName);
        return postWithoutBody(
                BASE_PATH + "/analyze-issues?company_name=" + companyName + "&pdf_path=" + pdfPath,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * SK 18개 이슈 목록 조회
     * GET /internal/v1/benchmarks/issues
     */
    public Mono<AiApiResponse<Object>> getSkIssues() {
        log.info("Getting SK issues list");
        return get(
                BASE_PATH + "/issues",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 캐시된 분석 데이터 조회
     * GET /internal/v1/benchmarks/data
     */
    public Mono<AiApiResponse<Object>> getCachedData() {
        log.info("Getting cached benchmark data");
        return get(
                BASE_PATH + "/data",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 문서 목록 조회
     * GET /internal/v1/benchmarks/documents
     */
    public Mono<AiApiResponse<BenchmarkDocumentAiResponse>> getDocuments() {
        log.info("Getting benchmark documents list");
        return get(
                BASE_PATH + "/documents",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 문서 삭제
     * DELETE /internal/v1/benchmarks/documents/{document_id}
     */
    public Mono<AiApiResponse<Object>> deleteDocument(String documentId) {
        log.info("Deleting benchmark document: {}", documentId);
        return delete(
                BASE_PATH + "/documents/" + documentId,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * PDF 삭제
     * DELETE /internal/v1/benchmarks/pdfs/{filename}
     */
    public Mono<AiApiResponse<Object>> deletePdf(String filename) {
        log.info("Deleting benchmark PDF: {}", filename);
        return delete(
                BASE_PATH + "/pdfs/" + filename,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 캐시 초기화
     * POST /internal/v1/benchmarks/cache/clear
     */
    public Mono<AiApiResponse<Object>> clearCache() {
        log.info("Clearing benchmark cache");
        return postWithoutBody(
                BASE_PATH + "/cache/clear",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 전체 캐시 삭제
     * POST /internal/v1/benchmarks/cache/clear-all
     */
    public Mono<AiApiResponse<Object>> clearAllCache() {
        log.info("Clearing all benchmark cache");
        return postWithoutBody(
                BASE_PATH + "/cache/clear-all",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 전체 재분석
     * POST /internal/v1/benchmarks/reanalyze-all
     */
    public Mono<AiApiResponse<Object>> reanalyzeAll() {
        log.info("Reanalyzing all benchmarks");
        return postWithoutBody(
                BASE_PATH + "/reanalyze-all",
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 헬스체크
     * GET /internal/v1/benchmarks/health
     */
    public Mono<HealthCheckResponse> healthCheck() {
        log.info("Checking benchmark service health");
        return webClient.get()
                .uri(BASE_PATH + "/health")
                .retrieve()
                .bodyToMono(HealthCheckResponse.class)
                .doOnSuccess(r -> log.info("Benchmark service health: {}", r.getStatus()))
                .doOnError(e -> log.error("Benchmark service health check failed: {}", e.getMessage()));
    }
}
