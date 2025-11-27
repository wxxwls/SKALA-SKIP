package com.skala.skip.benchmark.controller;

import com.skala.skip.benchmark.dto.request.BenchmarkAnalyzeRequest;
import com.skala.skip.benchmark.dto.response.BenchmarkAnalyzeResponse;
import com.skala.skip.benchmark.dto.response.BenchmarkDocumentResponse;
import com.skala.skip.benchmark.service.BenchmarkService;
import com.skala.skip.common.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 벤치마킹 컨트롤러
 * 경쟁사 벤치마킹 분석 API
 */
@RestController
@RequestMapping("/api/v1/benchmark")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Benchmark", description = "벤치마킹 분석 API")
public class BenchmarkController {

    private final BenchmarkService benchmarkService;

    @PostMapping("/analyze")
    @Operation(summary = "키워드 기반 분석", description = "키워드를 기반으로 경쟁사 ESG 보고서를 분석합니다")
    public ResponseEntity<ApiResponse<BenchmarkAnalyzeResponse>> analyze(
            @Valid @RequestBody BenchmarkAnalyzeRequest request
    ) {
        log.info("POST /api/v1/benchmark/analyze - keyword: {}", request.getKeyword());

        BenchmarkAnalyzeResponse response = benchmarkService.analyze(request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/analyze-issues")
    @Operation(summary = "SK 이슈 기반 분석", description = "SK 18개 이슈를 기반으로 분석합니다")
    public ResponseEntity<ApiResponse<Object>> analyzeIssues(
            @Parameter(description = "회사명") @RequestParam String companyName,
            @Parameter(description = "PDF 경로") @RequestParam String pdfPath
    ) {
        log.info("POST /api/v1/benchmark/analyze-issues - companyName: {}", companyName);

        Object response = benchmarkService.analyzeIssues(companyName, pdfPath);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/issues")
    @Operation(summary = "SK 이슈 목록 조회", description = "SK 18개 이슈 목록을 조회합니다")
    public ResponseEntity<ApiResponse<Object>> getSkIssues() {
        log.info("GET /api/v1/benchmark/issues");

        Object response = benchmarkService.getSkIssues();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/data")
    @Operation(summary = "캐시 데이터 조회", description = "캐시된 분석 데이터를 조회합니다")
    public ResponseEntity<ApiResponse<Object>> getCachedData() {
        log.info("GET /api/v1/benchmark/data");

        Object response = benchmarkService.getCachedData();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/documents")
    @Operation(summary = "문서 목록 조회", description = "업로드된 벤치마킹 문서 목록을 조회합니다")
    public ResponseEntity<ApiResponse<BenchmarkDocumentResponse>> getDocuments() {
        log.info("GET /api/v1/benchmark/documents");

        BenchmarkDocumentResponse response = benchmarkService.getDocuments();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @DeleteMapping("/documents/{documentId}")
    @Operation(summary = "문서 삭제", description = "벤치마킹 문서를 삭제합니다")
    public ResponseEntity<ApiResponse<Object>> deleteDocument(
            @Parameter(description = "문서 ID") @PathVariable String documentId
    ) {
        log.info("DELETE /api/v1/benchmark/documents/{}", documentId);

        Object response = benchmarkService.deleteDocument(documentId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/cache/clear")
    @Operation(summary = "캐시 초기화", description = "벤치마킹 캐시를 초기화합니다")
    public ResponseEntity<ApiResponse<Object>> clearCache() {
        log.info("POST /api/v1/benchmark/cache/clear");

        Object response = benchmarkService.clearCache();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/reanalyze-all")
    @Operation(summary = "전체 재분석", description = "모든 벤치마킹 데이터를 재분석합니다")
    public ResponseEntity<ApiResponse<Object>> reanalyzeAll() {
        log.info("POST /api/v1/benchmark/reanalyze-all");

        Object response = benchmarkService.reanalyzeAll();
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
