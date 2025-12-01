package com.skala.skip.report.controller;

import com.skala.skip.common.dto.ApiResponse;
import com.skala.skip.report.dto.request.ReportDraftRequest;
import com.skala.skip.report.dto.response.ReportDraftResponse;
import com.skala.skip.report.service.ReportAgentService;
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
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/reports")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Report Agent", description = "보고서 AI 초안 생성 API")
public class ReportAgentController {

    private final ReportAgentService reportAgentService;

    @PostMapping("/{reportId}/sections/{sectionCode}/ai-draft")
    @Operation(summary = "보고서 초안 생성", description = "AI를 활용하여 보고서 섹션의 초안을 생성합니다")
    public ResponseEntity<ApiResponse<ReportDraftResponse>> generateDraft(
            @Parameter(description = "보고서 ID") @PathVariable Long reportId,
            @Parameter(description = "섹션 코드") @PathVariable String sectionCode,
            @Valid @RequestBody ReportDraftRequest request
    ) {
        log.info("POST /api/v1/reports/{}/sections/{}/ai-draft - maxTokens: {}, tone: {}, language: {}",
                reportId, sectionCode, request.getMaxTokens(), request.getTone(), request.getLanguage());

        ReportDraftResponse response = reportAgentService.generateDraft(reportId, sectionCode, request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}

