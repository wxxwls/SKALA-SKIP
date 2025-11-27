package com.skala.skip.report.client;

import com.skala.skip.common.exception.ESGErrorCode;
import com.skala.skip.report.dto.request.ReportDraftRequest;
import com.skala.skip.report.dto.response.ReportDraftResponse;
import com.skala.skip.report.exception.ReportAgentException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Component
@RequiredArgsConstructor
@Slf4j
public class ReportAgentClient {

    private final WebClient fastApiWebClient;

    public Mono<ReportDraftResponse> generateDraftReport(Long reportId, String sectionCode, ReportDraftRequest request) {
        log.info("FastAPI 호출 시작 - reportId: {}, sectionCode: {}, maxTokens: {}, tone: {}, language: {}", 
                reportId, sectionCode, request.getMaxTokens(), request.getTone(), request.getLanguage());

        return fastApiWebClient
                .post()
                .uri("/internal/v1/reports/{reportId}/sections/{sectionCode}/ai-draft", reportId, sectionCode)
                .bodyValue(request)
                .retrieve()
                .onStatus(
                        status -> status.is4xxClientError() || status.is5xxServerError(),
                        response -> response
                                .bodyToMono(String.class)
                                .flatMap(body -> {
                                    HttpStatus httpStatus = HttpStatus.valueOf(response.statusCode().value());
                                    log.error("FastAPI 호출 실패 - reportId: {}, sectionCode: {}, status: {}, body: {}", 
                                            reportId, sectionCode, httpStatus, body);
                                    return Mono.error(new ReportAgentException(
                                            ESGErrorCode.RPT_CLIENT_001, 
                                            body
                                    ));
                                })
                )
                .bodyToMono(ReportDraftResponse.class)
                .doOnSuccess(response -> {
                    int contentLength = response.getDraftText() != null
                            ? response.getDraftText().length()
                            : 0;
                    int referencesCount = response.getReferences() != null
                            ? response.getReferences().size()
                            : 0;
                    log.info("FastAPI 호출 성공 - reportId: {}, sectionCode: {}, draftText length: {}, references count: {}",
                            reportId, sectionCode, contentLength, referencesCount);
                })
                .doOnError(error -> {
                    if (!(error instanceof ReportAgentException)) {
                        log.error("FastAPI 호출 중 예외 발생 - reportId: {}, sectionCode: {}", reportId, sectionCode, error);
                    }
                });
    }
}

