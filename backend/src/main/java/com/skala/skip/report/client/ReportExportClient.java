package com.skala.skip.report.client;

import com.skala.skip.common.exception.ESGErrorCode;
import com.skala.skip.report.dto.response.ReportExportResponse;
import com.skala.skip.report.exception.ReportExportException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.reactive.function.client.ClientResponse;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Optional;

@Component
@RequiredArgsConstructor
@Slf4j
public class ReportExportClient {

    private static final String EXPORT_URI = "/internal/v1/reports/{reportId}/export";
    private static final String DEFAULT_CONTENT_TYPE = "application/octet-stream";

    private final WebClient fastApiWebClient;

    public Mono<ReportExportResponse> downloadReport(Long reportId) {
        log.info("FastAPI 보고서 다운로드 호출 시작 - reportId: {}", reportId);

        return fastApiWebClient
                .get()
                .uri(EXPORT_URI, reportId)
                .exchangeToMono(response -> handleResponse(reportId, response))
                .doOnSuccess(response ->
                        log.info("FastAPI 보고서 다운로드 성공 - reportId: {}, bytes: {}",
                                reportId,
                                response.getFileContent() != null ? response.getFileContent().length : 0))
                .doOnError(error -> {
                    if (!(error instanceof ReportExportException)) {
                        log.error("FastAPI 보고서 다운로드 중 예기치 못한 오류 - reportId: {}", reportId, error);
                    }
                });
    }

    private Mono<ReportExportResponse> handleResponse(Long reportId, ClientResponse response) {
        if (response.statusCode().isError()) {
            return response.bodyToMono(String.class)
                    .defaultIfEmpty("FastAPI 응답 본문이 비어 있습니다.")
                    .flatMap(body -> {
                        log.error("FastAPI 보고서 다운로드 실패 - reportId: {}, status: {}, body: {}",
                                reportId, response.statusCode(), body);
                        return Mono.error(new ReportExportException(ESGErrorCode.RPT_CLIENT_001, body));
                    });
        }

        HttpHeaders headers = response.headers().asHttpHeaders();
        String contentType = Optional.ofNullable(headers.getContentType())
                .map(MediaType::toString)
                .orElse(DEFAULT_CONTENT_TYPE);
        String fileName = resolveFileName(headers, reportId);

        return response.bodyToMono(byte[].class)
                .switchIfEmpty(Mono.error(new ReportExportException(
                        ESGErrorCode.RPT_EXPORT_002,
                        "FastAPI 보고서 응답이 비어 있습니다.")))
                .map(body -> ReportExportResponse.builder()
                        .fileContent(body)
                        .contentType(contentType)
                        .fileName(fileName)
                        .build());
    }

    private String resolveFileName(HttpHeaders headers, Long reportId) {
        return Optional.ofNullable(headers.getFirst(HttpHeaders.CONTENT_DISPOSITION))
                .map(this::extractFileName)
                .filter(StringUtils::hasText)
                .orElse(String.format("report-%d.pdf", reportId));
    }

    private String extractFileName(String contentDisposition) {
        try {
            ContentDisposition disposition = ContentDisposition.parse(contentDisposition);
            return disposition.getFilename();
        } catch (IllegalArgumentException ex) {
            log.warn("Content-Disposition 파싱 실패: {}", contentDisposition, ex);
            return null;
        }
    }
}


