package com.skala.skip.materiality.controller;

import com.skala.skip.common.dto.ApiResponse;
import com.skala.skip.common.dto.MetaResponse;
import com.skala.skip.materiality.dto.request.CreateSurveyRequest;
import com.skala.skip.materiality.dto.request.SubmitSurveyResponseRequest;
import com.skala.skip.materiality.dto.response.MaterialityMatrixResponse;
import com.skala.skip.materiality.dto.response.SurveyResponse;
import com.skala.skip.materiality.service.MaterialityService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

/**
 * 중대성 평가 컨트롤러
 * 이해관계자 설문 및 중대성 매트릭스 API
 */
@RestController
@RequestMapping("/api/v1/materiality")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Materiality", description = "중대성 평가 API")
public class MaterialityController {

    private final MaterialityService materialityService;

    @PostMapping("/{companyId}/surveys")
    @Operation(summary = "이해관계자 설문 생성", description = "이해관계자 설문을 생성합니다")
    public ResponseEntity<ApiResponse<SurveyResponse>> createSurvey(
            @Parameter(description = "회사 ID") @PathVariable String companyId,
            @Valid @RequestBody CreateSurveyRequest request
    ) {
        log.info("POST /api/v1/materiality/{}/surveys - year: {}, stakeholderType: {}",
                companyId, request.getYear(), request.getStakeholderType());

        SurveyResponse response = materialityService.createSurvey(companyId, request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/surveys/{surveyId}/responses")
    @Operation(summary = "설문 응답 제출", description = "설문 응답을 제출합니다")
    public ResponseEntity<ApiResponse<Object>> submitSurveyResponse(
            @Parameter(description = "설문 ID") @PathVariable String surveyId,
            @Valid @RequestBody SubmitSurveyResponseRequest request
    ) {
        log.info("POST /api/v1/materiality/surveys/{}/responses", surveyId);

        Object response = materialityService.submitSurveyResponse(surveyId, request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/{companyId}/matrix")
    @Operation(summary = "중대성 매트릭스 조회", description = "중대성 매트릭스를 조회합니다")
    public ResponseEntity<ApiResponse<MaterialityMatrixResponse>> getMaterialityMatrix(
            @Parameter(description = "회사 ID") @PathVariable String companyId,
            @Parameter(description = "연도") @RequestParam int year
    ) {
        log.info("GET /api/v1/materiality/{}/matrix - year: {}", companyId, year);

        MaterialityMatrixResponse response = materialityService.getMaterialityMatrix(companyId, year);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
