package com.skala.skip.report.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * ESG 보고서 생성 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportGenerateResponse {

    private boolean success;
    private String reportHtml;
    private List<ReportSection> sections;
    private ReportMetadata metadata;
    private String error;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ReportSection {
        private String sectionId;
        private String title;
        private String content;
        private String issueId;
    }

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ReportMetadata {
        private int totalIssues;
        private int sectionsGenerated;
        private long processingTimeMs;
        private String modelUsed;
    }
}
