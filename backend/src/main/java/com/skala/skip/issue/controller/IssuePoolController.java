package com.skala.skip.issue.controller;

import com.skala.skip.common.dto.ApiResponse;
import com.skala.skip.issue.dto.request.IssuePoolCreateRequest;
import com.skala.skip.issue.dto.request.ScoreTopicRequest;
import com.skala.skip.issue.dto.response.IssuePoolResponse;
import com.skala.skip.issue.dto.response.ScoreTopicResponse;
import com.skala.skip.issue.service.IssuePoolService;
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

/**
 * 이슈풀 컨트롤러
 * ESG 이슈풀 생성 및 토픽 점수화 API
 */
@RestController
@RequestMapping("/api/v1/issue-pool")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Issue Pool", description = "ESG 이슈풀 API")
public class IssuePoolController {

    private final IssuePoolService issuePoolService;

    @PostMapping("/{companyId}/generate")
    @Operation(summary = "ESG 이슈풀 생성", description = "AI를 활용하여 ESG 이슈풀을 생성합니다 (최대 20개 토픽)")
    public ResponseEntity<ApiResponse<IssuePoolResponse>> generateIssuePool(
            @Parameter(description = "회사 ID") @PathVariable String companyId,
            @Valid @RequestBody IssuePoolCreateRequest request
    ) {
        log.info("POST /api/v1/issue-pool/{}/generate - companyName: {}, year: {}",
                companyId, request.getCompanyName(), request.getYear());

        IssuePoolResponse response = issuePoolService.generateIssuePool(companyId, request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @PostMapping("/{companyId}/score-topic")
    @Operation(summary = "토픽 점수화", description = "단일 토픽의 이중중대성(재무적/영향) 점수를 산출합니다")
    public ResponseEntity<ApiResponse<ScoreTopicResponse>> scoreTopic(
            @Parameter(description = "회사 ID") @PathVariable String companyId,
            @Valid @RequestBody ScoreTopicRequest request
    ) {
        log.info("POST /api/v1/issue-pool/{}/score-topic - topicTitle: {}",
                companyId, request.getTopicTitle());

        ScoreTopicResponse response = issuePoolService.scoreTopic(companyId, request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
