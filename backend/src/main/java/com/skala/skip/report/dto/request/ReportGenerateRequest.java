package com.skala.skip.report.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * ESG 보고서 생성 요청 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportGenerateRequest {

    @NotBlank(message = "회사명은 필수입니다")
    private String companyName;

    @NotBlank(message = "산업군은 필수입니다")
    private String industry;

    @NotNull(message = "연도는 필수입니다")
    private Integer year;

    @NotEmpty(message = "이슈 목록은 필수입니다")
    private List<IssueItem> issues;

    private String previousReport;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class IssueItem {
        private String issueId;
        private String issueName;
        private String category;
        private double financialScore;
        private double impactScore;
        private String description;
        private List<KpiItem> kpis;
    }

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class KpiItem {
        private String name;
        private String value;
        private String unit;
        private int year;
        private String target;
    }
}
