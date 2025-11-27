package com.skala.skip.standards.controller;

import com.skala.skip.common.dto.ApiResponse;
import com.skala.skip.standards.dto.response.IssueDisclosuresResponse;
import com.skala.skip.standards.dto.response.StandardsDocumentResponse;
import com.skala.skip.standards.dto.response.StandardsIssuesResponse;
import com.skala.skip.standards.service.StandardsService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * ESG 표준 컨트롤러
 * ESG 표준 문서 및 공시 요건 관련 API
 */
@RestController
@RequestMapping("/api/v1/standards")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Standards", description = "ESG 표준 문서 API")
public class StandardsController {

    private final StandardsService standardsService;

    @GetMapping("/issues")
    @Operation(summary = "이슈 목록 조회", description = "한국 중대성 이슈 18개 목록을 조회합니다")
    public ResponseEntity<ApiResponse<StandardsIssuesResponse>> getIssues() {
        log.info("GET /api/v1/standards/issues");

        StandardsIssuesResponse response = standardsService.getIssues();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/issues/with-disclosures")
    @Operation(summary = "이슈별 공시 요건 매핑 조회", description = "모든 이슈에 대한 공시 요건 매핑을 조회합니다")
    public ResponseEntity<ApiResponse<Object>> getIssuesWithDisclosures() {
        log.info("GET /api/v1/standards/issues/with-disclosures");

        Object response = standardsService.getIssuesWithDisclosures();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/issues/{issueName}/disclosures")
    @Operation(summary = "특정 이슈 공시 요건 조회", description = "특정 이슈에 대한 공시 요건을 조회합니다")
    public ResponseEntity<ApiResponse<IssueDisclosuresResponse>> getIssueDisclosures(
            @Parameter(description = "이슈명") @PathVariable String issueName
    ) {
        log.info("GET /api/v1/standards/issues/{}/disclosures", issueName);

        IssueDisclosuresResponse response = standardsService.getIssueDisclosures(issueName);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/issues/{issueName}/analyze")
    @Operation(summary = "이슈 분석", description = "AI 기반으로 특정 이슈를 분석합니다")
    public ResponseEntity<ApiResponse<Object>> analyzeIssue(
            @Parameter(description = "이슈명") @PathVariable String issueName
    ) {
        log.info("GET /api/v1/standards/issues/{}/analyze", issueName);

        Object response = standardsService.analyzeIssue(issueName);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/search")
    @Operation(summary = "공시 요건 검색", description = "키워드로 공시 요건을 검색합니다")
    public ResponseEntity<ApiResponse<Object>> searchDisclosures(
            @Parameter(description = "검색어") @RequestParam String query
    ) {
        log.info("GET /api/v1/standards/search - query: {}", query);

        Object response = standardsService.searchDisclosures(query);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/statistics")
    @Operation(summary = "통계 정보 조회", description = "표준 문서 통계 정보를 조회합니다")
    public ResponseEntity<ApiResponse<Object>> getStatistics() {
        log.info("GET /api/v1/standards/statistics");

        Object response = standardsService.getStatistics();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PatchMapping("/index")
    @Operation(summary = "문서 인덱싱", description = "GRI/SASB PDF 문서를 인덱싱합니다")
    public ResponseEntity<ApiResponse<Object>> indexDocuments() {
        log.info("PATCH /api/v1/standards/index");

        Object response = standardsService.indexDocuments();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/reset")
    @Operation(summary = "ChromaDB 리셋", description = "ChromaDB를 리셋합니다")
    public ResponseEntity<ApiResponse<Object>> resetChromaDB() {
        log.info("POST /api/v1/standards/reset");

        Object response = standardsService.resetChromaDB();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/count")
    @Operation(summary = "문서 수 조회", description = "인덱싱된 문서 수를 조회합니다")
    public ResponseEntity<ApiResponse<Object>> getDocumentCount() {
        log.info("GET /api/v1/standards/count");

        Object response = standardsService.getDocumentCount();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @GetMapping("/documents")
    @Operation(summary = "문서 목록 조회", description = "표준 문서 목록을 조회합니다")
    public ResponseEntity<ApiResponse<StandardsDocumentResponse>> getDocuments() {
        log.info("GET /api/v1/standards/documents");

        StandardsDocumentResponse response = standardsService.getDocuments();
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @DeleteMapping("/documents/{documentId}")
    @Operation(summary = "문서 삭제", description = "특정 문서를 삭제합니다")
    public ResponseEntity<ApiResponse<Object>> deleteDocument(
            @Parameter(description = "문서 ID") @PathVariable String documentId
    ) {
        log.info("DELETE /api/v1/standards/documents/{}", documentId);

        Object response = standardsService.deleteDocument(documentId);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/documents/embed")
    @Operation(summary = "문서 임베딩", description = "문서 임베딩을 시작합니다")
    public ResponseEntity<ApiResponse<Object>> embedDocuments() {
        log.info("POST /api/v1/standards/documents/embed");

        Object response = standardsService.embedDocuments();
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
