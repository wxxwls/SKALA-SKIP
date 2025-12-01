package com.skala.skip.ai.client;

import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.exception.AiServiceException;
import com.skala.skip.common.exception.ESGErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpStatusCode;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;

import java.net.ConnectException;
import java.util.Map;
import java.util.concurrent.TimeoutException;

/**
 * AI Service Client 베이스 클래스
 * 모든 AI 서비스 클라이언트의 공통 기능을 제공
 */
@Slf4j
@RequiredArgsConstructor
public abstract class AiServiceClient {

    protected final WebClient webClient;

    /**
     * POST 요청 (제네릭 응답)
     */
    protected <T> Mono<AiApiResponse<T>> post(String uri, Object request, ParameterizedTypeReference<AiApiResponse<T>> responseType) {
        return webClient.post()
                .uri(uri)
                .bodyValue(request)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Client error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .onStatus(HttpStatusCode::is5xxServerError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Server error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .bodyToMono(responseType)
                .doOnSubscribe(s -> log.info("AI Service POST {} - request: {}", uri, request))
                .doOnSuccess(r -> log.info("AI Service POST {} - success", uri))
                .doOnError(e -> log.error("AI Service POST {} - error: {}", uri, e.getMessage()))
                .onErrorMap(this::mapException);
    }

    /**
     * POST 요청 (Body 없음)
     */
    protected <T> Mono<AiApiResponse<T>> postWithoutBody(String uri, ParameterizedTypeReference<AiApiResponse<T>> responseType) {
        return webClient.post()
                .uri(uri)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Client error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .onStatus(HttpStatusCode::is5xxServerError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Server error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .bodyToMono(responseType)
                .doOnSubscribe(s -> log.info("AI Service POST {}", uri))
                .doOnSuccess(r -> log.info("AI Service POST {} - success", uri))
                .doOnError(e -> log.error("AI Service POST {} - error: {}", uri, e.getMessage()))
                .onErrorMap(this::mapException);
    }

    /**
     * GET 요청 (제네릭 응답)
     */
    protected <T> Mono<AiApiResponse<T>> get(String uri, ParameterizedTypeReference<AiApiResponse<T>> responseType) {
        return webClient.get()
                .uri(uri)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Client error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .onStatus(HttpStatusCode::is5xxServerError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Server error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .bodyToMono(responseType)
                .doOnSubscribe(s -> log.info("AI Service GET {}", uri))
                .doOnSuccess(r -> log.info("AI Service GET {} - success", uri))
                .doOnError(e -> log.error("AI Service GET {} - error: {}", uri, e.getMessage()))
                .onErrorMap(this::mapException);
    }

    /**
     * GET 요청 (쿼리 파라미터 포함)
     */
    protected <T> Mono<AiApiResponse<T>> getWithParams(String uri, Map<String, Object> params, ParameterizedTypeReference<AiApiResponse<T>> responseType) {
        return webClient.get()
                .uri(uriBuilder -> {
                    uriBuilder.path(uri);
                    params.forEach((key, value) -> {
                        if (value != null) {
                            uriBuilder.queryParam(key, value);
                        }
                    });
                    return uriBuilder.build();
                })
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Client error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .onStatus(HttpStatusCode::is5xxServerError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Server error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .bodyToMono(responseType)
                .doOnSubscribe(s -> log.info("AI Service GET {} - params: {}", uri, params))
                .doOnSuccess(r -> log.info("AI Service GET {} - success", uri))
                .doOnError(e -> log.error("AI Service GET {} - error: {}", uri, e.getMessage()))
                .onErrorMap(this::mapException);
    }

    /**
     * DELETE 요청
     */
    protected <T> Mono<AiApiResponse<T>> delete(String uri, ParameterizedTypeReference<AiApiResponse<T>> responseType) {
        return webClient.delete()
                .uri(uri)
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Client error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .onStatus(HttpStatusCode::is5xxServerError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Server error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .bodyToMono(responseType)
                .doOnSubscribe(s -> log.info("AI Service DELETE {}", uri))
                .doOnSuccess(r -> log.info("AI Service DELETE {} - success", uri))
                .doOnError(e -> log.error("AI Service DELETE {} - error: {}", uri, e.getMessage()))
                .onErrorMap(this::mapException);
    }

    /**
     * PATCH 요청
     */
    protected <T> Mono<AiApiResponse<T>> patch(String uri, Object request, ParameterizedTypeReference<AiApiResponse<T>> responseType) {
        return webClient.patch()
                .uri(uri)
                .bodyValue(request != null ? request : "")
                .retrieve()
                .onStatus(HttpStatusCode::is4xxClientError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Client error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .onStatus(HttpStatusCode::is5xxServerError, response ->
                        response.bodyToMono(String.class)
                                .flatMap(body -> Mono.error(new AiServiceException(
                                        ESGErrorCode.AI_RESPONSE_ERROR,
                                        "Server error: " + response.statusCode(),
                                        body,
                                        response.statusCode().value()
                                )))
                )
                .bodyToMono(responseType)
                .doOnSubscribe(s -> log.info("AI Service PATCH {} - request: {}", uri, request))
                .doOnSuccess(r -> log.info("AI Service PATCH {} - success", uri))
                .doOnError(e -> log.error("AI Service PATCH {} - error: {}", uri, e.getMessage()))
                .onErrorMap(this::mapException);
    }

    /**
     * 예외 매핑
     * WebClient 예외를 AiServiceException으로 변환
     */
    private Throwable mapException(Throwable throwable) {
        if (throwable instanceof AiServiceException) {
            return throwable;
        }

        if (throwable instanceof TimeoutException) {
            return new AiServiceException(
                    ESGErrorCode.AI_TIMEOUT,
                    "AI 서비스 요청 타임아웃",
                    throwable
            );
        }

        if (throwable instanceof WebClientRequestException) {
            Throwable cause = throwable.getCause();
            if (cause instanceof ConnectException) {
                return new AiServiceException(
                        ESGErrorCode.AI_UNAVAILABLE,
                        "AI 서비스 연결 불가: " + cause.getMessage(),
                        throwable
                );
            }
            return new AiServiceException(
                    ESGErrorCode.AI_UNAVAILABLE,
                    "AI 서비스 요청 실패: " + throwable.getMessage(),
                    throwable
            );
        }

        if (throwable instanceof WebClientResponseException responseException) {
            return new AiServiceException(
                    ESGErrorCode.AI_RESPONSE_ERROR,
                    "AI 서비스 응답 오류: " + responseException.getStatusCode(),
                    responseException.getResponseBodyAsString(),
                    responseException.getStatusCode().value()
            );
        }

        return new AiServiceException(
                ESGErrorCode.AI_RESPONSE_ERROR,
                "AI 서비스 호출 중 오류 발생: " + throwable.getMessage(),
                throwable
        );
    }
}
