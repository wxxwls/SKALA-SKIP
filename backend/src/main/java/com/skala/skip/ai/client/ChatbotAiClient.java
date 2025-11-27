package com.skala.skip.ai.client;

import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.common.HealthCheckResponse;
import com.skala.skip.ai.dto.request.ChatbotQueryAiRequest;
import com.skala.skip.ai.dto.response.ChatbotQueryAiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

/**
 * ESG Chatbot AI Service Client
 * FastAPI RAG Q&A 관련 API 호출
 */
@Component
@Slf4j
public class ChatbotAiClient extends AiServiceClient {

    private static final String BASE_PATH = "/internal/v1/chatbot";

    public ChatbotAiClient(@Qualifier("aiServiceWebClient") WebClient webClient) {
        super(webClient);
    }

    /**
     * ESG 질의응답
     * POST /internal/v1/chatbot/query
     */
    public Mono<AiApiResponse<ChatbotQueryAiResponse>> query(ChatbotQueryAiRequest request) {
        log.info("Chatbot query: {}", request.getQuery());
        return post(
                BASE_PATH + "/query",
                request,
                new ParameterizedTypeReference<>() {}
        );
    }

    /**
     * 헬스체크
     * GET /internal/v1/chatbot/health
     */
    public Mono<HealthCheckResponse> healthCheck() {
        log.info("Checking chatbot service health");
        return webClient.get()
                .uri(BASE_PATH + "/health")
                .retrieve()
                .bodyToMono(HealthCheckResponse.class)
                .doOnSuccess(r -> log.info("Chatbot service health: {}", r.getStatus()))
                .doOnError(e -> log.error("Chatbot service health check failed: {}", e.getMessage()));
    }
}
