package com.skala.skip.report.controller;

import com.skala.skip.common.dto.ApiResponse;
import com.skala.skip.report.dto.request.ReportGenerateRequest;
import com.skala.skip.report.dto.request.ReportModifyRequest;
import com.skala.skip.report.dto.response.ReportGenerateResponse;
import com.skala.skip.report.dto.response.ReportModifyResponse;
import com.skala.skip.report.service.ReportAiService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 보고서 AI 컨트롤러
 * AI 기반 ESG 보고서 생성/수정 API
 */
@RestController
@RequestMapping("/api/v1/report")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Report AI", description = "AI 기반 ESG 보고서 API")
public class ReportAiController {

    private final ReportAiService reportAiService;

    @PostMapping("/{companyId}/generate")
    @Operation(summary = "ESG 보고서 생성", description = "AI를 활용하여 ESG 보고서를 생성합니다")
    public ResponseEntity<ApiResponse<ReportGenerateResponse>> generateReport(
            @Parameter(description = "회사 ID") @PathVariable String companyId,
            @Valid @RequestBody ReportGenerateRequest request
    ) {
        log.info("POST /api/v1/report/{}/generate - companyName: {}, issueCount: {}",
                companyId, request.getCompanyName(), request.getIssues().size());

        ReportGenerateResponse response = reportAiService.generateReport(companyId, request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/{companyId}/modify")
    @Operation(summary = "보고서 수정", description = "자연어 명령으로 보고서를 수정합니다")
    public ResponseEntity<ApiResponse<ReportModifyResponse>> modifyReport(
            @Parameter(description = "회사 ID") @PathVariable String companyId,
            @Parameter(description = "회사명") @RequestParam String companyName,
            @Valid @RequestBody ReportModifyRequest request
    ) {
        log.info("POST /api/v1/report/{}/modify - instruction: {}", companyId, request.getInstruction());

        ReportModifyResponse response = reportAiService.modifyReport(companyId, companyName, request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
