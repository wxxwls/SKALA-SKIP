package com.skala.skip.ai.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.skala.skip.ai.dto.common.CompanyContext;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * ESG 보고서 생성 AI 요청 DTO
 * POST /internal/v1/reports/generate
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportGenerateAiRequest {

    @NotNull
    @JsonProperty("company_context")
    private CompanyContext companyContext;

    @NotEmpty
    @JsonProperty("issues")
    private List<IssueItem> issues;

    @JsonProperty("previous_report")
    private String previousReport;

    /**
     * 보고서에 포함할 이슈 아이템
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class IssueItem {

        @JsonProperty("issue_id")
        private String issueId;

        @JsonProperty("issue_name")
        private String issueName;

        @JsonProperty("category")
        private String category;

        @JsonProperty("financial_score")
        private double financialScore;

        @JsonProperty("impact_score")
        private double impactScore;

        @JsonProperty("description")
        private String description;

        @JsonProperty("kpis")
        private List<KpiItem> kpis;
    }

    /**
     * KPI 아이템
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class KpiItem {

        @JsonProperty("name")
        private String name;

        @JsonProperty("value")
        private String value;

        @JsonProperty("unit")
        private String unit;

        @JsonProperty("year")
        private int year;

        @JsonProperty("target")
        private String target;
    }
}
