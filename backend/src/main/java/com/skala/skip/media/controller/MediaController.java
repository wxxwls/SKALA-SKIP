package com.skala.skip.media.controller;

import com.skala.skip.common.dto.ApiResponse;
import com.skala.skip.media.dto.request.AnalyzeNewsRequest;
import com.skala.skip.media.dto.response.AnalyzeNewsResponse;
import com.skala.skip.media.service.MediaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 미디어 분석 컨트롤러
 * 뉴스/미디어 분석 API
 */
@RestController
@RequestMapping("/api/v1/media")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Media", description = "미디어 분석 API")
public class MediaController {

    private final MediaService mediaService;

    @GetMapping
    @Operation(summary = "미디어 데이터 조회", description = "저장된 미디어 분석 데이터를 조회합니다")
    public ResponseEntity<ApiResponse<Object>> getMediaData() {
        log.info("GET /api/v1/media");

        Object response = mediaService.getMediaData();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/analyze")
    @Operation(summary = "뉴스 분석", description = "키워드 기반으로 뉴스를 수집하고 분석합니다")
    public ResponseEntity<ApiResponse<AnalyzeNewsResponse>> analyzeNews(
            @Valid @RequestBody AnalyzeNewsRequest request
    ) {
        log.info("POST /api/v1/media/analyze - keywords: {}", request.getKeywords());

        AnalyzeNewsResponse response = mediaService.analyzeNews(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/issues")
    @Operation(summary = "ESG 이슈 정의 조회", description = "ESG 18개 이슈 정의를 조회합니다")
    public ResponseEntity<ApiResponse<Object>> getEsgIssues() {
        log.info("GET /api/v1/media/issues");

        Object response = mediaService.getEsgIssues();
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
