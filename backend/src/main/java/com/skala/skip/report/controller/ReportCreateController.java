package com.skala.skip.report.controller;

import com.skala.skip.common.dto.ApiResponse;
import com.skala.skip.report.dto.request.ReportCreateRequest;
import com.skala.skip.report.dto.response.ReportCreateResponse;
import com.skala.skip.report.service.ReportCreateService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/reports")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Report Create", description = "보고서 생성 API")
public class ReportCreateController {

    private final ReportCreateService reportCreateService;

    @PostMapping
    @Operation(summary = "보고서 생성", description = "새로운 ESG 보고서를 생성합니다")
    public ResponseEntity<ApiResponse<ReportCreateResponse>> createReport(
            @Valid @RequestBody ReportCreateRequest request
    ) {
        log.info("POST /api/v1/reports - companyId: {}, year: {}, title: {}",
                request.getCompanyId(), request.getYear(), request.getTitle());

        ReportCreateResponse response = reportCreateService.createReport(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}


