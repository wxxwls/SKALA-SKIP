package com.skala.skip.report.controller;

import com.skala.skip.report.dto.response.ReportExportResponse;
import com.skala.skip.report.service.ReportExportService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.nio.charset.StandardCharsets;

@RestController
@RequestMapping("/api/v1/reports")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Report Export", description = "보고서 내보내기 API")
public class ReportExportController {

    private final ReportExportService reportExportService;

    @GetMapping("/{reportId}/export")
    @Operation(summary = "보고서 내보내기", description = "보고서를 PDF 파일로 내보냅니다")
    public ResponseEntity<byte[]> exportReport(
            @Parameter(description = "보고서 ID") @PathVariable Long reportId
    ) {
        log.info("GET /api/v1/reports/{}/export", reportId);

        ReportExportResponse response = reportExportService.exportReport(reportId);
        return toResponseEntity(response);
    }

    private ResponseEntity<byte[]> toResponseEntity(ReportExportResponse response) {
        MediaType mediaType = MediaType.APPLICATION_OCTET_STREAM;
        if (response.getContentType() != null) {
            try {
                mediaType = MediaType.parseMediaType(response.getContentType());
            } catch (IllegalArgumentException ignored) {
                log.warn("알 수 없는 Content-Type, 기본값 사용: {}", response.getContentType());
            }
        }

        ContentDisposition disposition = ContentDisposition.attachment()
                .filename(response.getFileName(), StandardCharsets.UTF_8)
                .build();

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, disposition.toString())
                .contentType(mediaType)
                .body(response.getFileContent());
    }
}


