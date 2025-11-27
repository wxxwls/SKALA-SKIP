package com.skala.skip.ai.config;

import io.netty.channel.ChannelOption;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.ExchangeFilterFunction;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.util.retry.Retry;

import java.time.Duration;

/**
 * AI Service WebClient Configuration
 * FastAPI AI 서비스 연동을 위한 WebClient 설정
 * 타임아웃, 재시도 및 에러 처리 포함
 */
@Configuration
@Slf4j
public class AiServiceConfig {

    @Value("${app.ai-service.base-url:http://localhost:8000}")
    private String aiServiceBaseUrl;

    @Value("${app.ai-service.timeout:120000}")
    private int timeout;

    @Value("${app.ai-service.max-in-memory-size:16777216}")
    private int maxInMemorySize;

    @Value("${app.ai-service.retry.max-attempts:3}")
    private int maxRetryAttempts;

    @Value("${app.ai-service.retry.backoff-ms:2000}")
    private long retryBackoffMs;

    /**
     * AI Service 전용 WebClient Bean
     * 보고서 생성 등 시간이 오래 걸리는 작업을 위해 타임아웃을 길게 설정
     */
    @Bean(name = "aiServiceWebClient")
    public WebClient aiServiceWebClient() {
        HttpClient httpClient = HttpClient.create()
                .responseTimeout(Duration.ofMillis(timeout))
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, timeout);

        return WebClient.builder()
                .baseUrl(aiServiceBaseUrl)
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .codecs(configurer -> configurer
                        .defaultCodecs()
                        .maxInMemorySize(maxInMemorySize))
                .filter(logRequest())
                .filter(logResponse())
                .filter(retryFilter())
                .build();
    }

    /**
     * Retry 설정을 위한 필터
     * 5xx 에러 또는 연결 실패 시 재시도
     */
    private ExchangeFilterFunction retryFilter() {
        return (request, next) -> next.exchange(request)
                .flatMap(response -> {
                    if (response.statusCode().is5xxServerError()) {
                        return Mono.error(new RuntimeException("AI Service error: " + response.statusCode()));
                    }
                    return Mono.just(response);
                })
                .retryWhen(Retry.backoff(maxRetryAttempts, Duration.ofMillis(retryBackoffMs))
                        .filter(throwable -> {
                            log.warn("Retrying AI Service request due to: {}", throwable.getMessage());
                            return true;
                        })
                        .onRetryExhaustedThrow((retryBackoffSpec, retrySignal) -> {
                            log.error("AI Service retry exhausted after {} attempts", maxRetryAttempts);
                            return retrySignal.failure();
                        }));
    }

    /**
     * Request 로깅 필터
     */
    private ExchangeFilterFunction logRequest() {
        return ExchangeFilterFunction.ofRequestProcessor(clientRequest -> {
            log.info("AI Service Request: {} {}", clientRequest.method(), clientRequest.url());
            return Mono.just(clientRequest);
        });
    }

    /**
     * Response 로깅 필터
     */
    private ExchangeFilterFunction logResponse() {
        return ExchangeFilterFunction.ofResponseProcessor(clientResponse -> {
            HttpStatusCode statusCode = clientResponse.statusCode();
            if (statusCode.isError()) {
                log.error("AI Service Response Error: {}", statusCode);
            } else {
                log.info("AI Service Response: {}", statusCode);
            }
            return Mono.just(clientResponse);
        });
    }
}
