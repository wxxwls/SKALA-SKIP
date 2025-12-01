package com.skala.skip.config;

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
 * FastAPI WebClient 설정
 * 타임아웃, 재시도 및 에러 처리 포함
 */
@Configuration
@Slf4j
public class WebClientConfig {

    @Value("${app.fastapi.base-url}")
    private String fastApiBaseUrl;

    @Value("${app.fastapi.timeout:30000}")
    private int timeout;

    @Value("${app.fastapi.retry.max-attempts:3}")
    private int maxRetryAttempts;

    @Value("${app.fastapi.retry.backoff-ms:1000}")
    private long retryBackoffMs;

    @Bean
    public WebClient fastApiWebClient() {
        HttpClient httpClient = HttpClient.create()
                .responseTimeout(Duration.ofMillis(timeout))
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, timeout);

        return WebClient.builder()
                .baseUrl(fastApiBaseUrl)
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
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
                        return Mono.error(new RuntimeException("Server error: " + response.statusCode()));
                    }
                    return Mono.just(response);
                })
                .retryWhen(Retry.backoff(maxRetryAttempts, Duration.ofMillis(retryBackoffMs))
                        .filter(throwable -> {
                            log.warn("Retrying request due to: {}", throwable.getMessage());
                            return true;
                        })
                        .onRetryExhaustedThrow((retryBackoffSpec, retrySignal) -> {
                            log.error("Retry exhausted after {} attempts", maxRetryAttempts);
                            return retrySignal.failure();
                        }));
    }

    /**
     * Request 로깅 필터
     */
    private ExchangeFilterFunction logRequest() {
        return ExchangeFilterFunction.ofRequestProcessor(clientRequest -> {
            log.info("FastAPI Request: {} {}", clientRequest.method(), clientRequest.url());
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
                log.error("FastAPI Response Error: {}", statusCode);
            } else {
                log.info("FastAPI Response: {}", statusCode);
            }
            return Mono.just(clientResponse);
        });
    }
}

