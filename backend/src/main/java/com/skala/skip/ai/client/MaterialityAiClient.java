package com.skala.skip.ai.client;

import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.common.HealthCheckResponse;
import com.skala.skip.ai.dto.request.CreateSurveyAiRequest;
import com.skala.skip.ai.dto.request.SubmitSurveyResponseAiRequest;
import com.skala.skip.ai.dto.response.MaterialityMatrixAiResponse;
import com.skala.skip.ai.dto.response.SurveyAiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.HashMap;
import java.util.Map;

/**
 * Materiality Assessment AI Service Client
 * FastAPI 중대성 평가 관련 API 호출
 */
@Component
@Slf4j
public class MaterialityAiClient extends AiServiceClient {

    private static final String SURVEY_BASE_PATH = "/internal/v1/surveys";
    private static final String MATERIALITY_BASE_PATH = "/internal/v1/materiality";

    public MaterialityAiClient(@Qualifier("aiServiceWebClient") WebClient webClient) {
        super(webClient);
    }

    /**
     * 이해관계자 설문 생성
     * POST /internal/v1/surveys
     */
    public Mono<AiApiResponse<SurveyAiResponse>> createSurvey(CreateSurveyAiRequest request) {
        log.info("Creating survey for company: {}", request.getCompanyId());
        return post(
                SURVEY_BASE_PATH,
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 설문 응답 제출
     * POST /internal/v1/surveys/{survey_id}/responses
     */
    public Mono<AiApiResponse<Object>> submitSurveyResponse(String surveyId, SubmitSurveyResponseAiRequest request) {
        log.info("Submitting survey response for survey: {}", surveyId);
        return post(
                SURVEY_BASE_PATH + "/" + surveyId + "/responses",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 중대성 매트릭스 조회
     * GET /internal/v1/materiality/matrix
     */
    public Mono<AiApiResponse<MaterialityMatrixAiResponse>> getMaterialityMatrix(String companyId, int year) {
        log.info("Getting materiality matrix for company: {}, year: {}", companyId, year);
        Map<String, Object> params = new HashMap<>();
        params.put("company_id", companyId);
        params.put("year", year);
        return getWithParams(
                MATERIALITY_BASE_PATH + "/matrix",
                params,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 헬스체크
     * GET /internal/v1/materiality/health
     */
    public Mono<HealthCheckResponse> healthCheck() {
        log.info("Checking materiality service health");
        return webClient.get()
                .uri(MATERIALITY_BASE_PATH + "/health")
                .retrieve()
                .bodyToMono(HealthCheckResponse.class)
                .doOnSuccess(r -> log.info("Materiality service health: {}", r.getStatus()))
                .doOnError(e -> log.error("Materiality service health check failed: {}", e.getMessage()));
    }
}
