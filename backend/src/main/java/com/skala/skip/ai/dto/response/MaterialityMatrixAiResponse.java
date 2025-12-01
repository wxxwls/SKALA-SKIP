package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 중대성 매트릭스 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MaterialityMatrixAiResponse {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("company_id")
    private String companyId;

    @JsonProperty("year")
    private int year;

    @JsonProperty("matrix")
    private List<MaterialityItem> matrix;

    @JsonProperty("total_issues")
    private int totalIssues;

    @JsonProperty("high_priority_count")
    private int highPriorityCount;

    /**
     * 중대성 매트릭스 아이템
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MaterialityItem {

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

        @JsonProperty("quadrant")
        private String quadrant;

        @JsonProperty("stakeholder_importance")
        private double stakeholderImportance;

        @JsonProperty("business_importance")
        private double businessImportance;
    }
}
