package com.skala.skip.ai.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.skala.skip.ai.dto.common.CompanyContext;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * ESG 이슈풀 생성 AI 요청 DTO
 * POST /internal/v1/issue-pools/generate
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IssuePoolGenerateAiRequest {

    @NotNull
    @JsonProperty("company_context")
    private CompanyContext companyContext;

    @Builder.Default
    @JsonProperty("use_standards")
    private boolean useStandards = true;

    @Builder.Default
    @JsonProperty("use_benchmarks")
    private boolean useBenchmarks = true;

    @Builder.Default
    @JsonProperty("use_internal")
    private boolean useInternal = true;

    @Builder.Default
    @JsonProperty("use_news")
    private boolean useNews = true;

    @Min(1)
    @Max(50)
    @Builder.Default
    @JsonProperty("max_topics")
    private int maxTopics = 20;
}
