package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * ESG 보고서 생성 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportGenerateAiResponse {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("report_html")
    private String reportHtml;

    @JsonProperty("sections")
    private List<ReportSection> sections;

    @JsonProperty("metadata")
    private ReportMetadata metadata;

    @JsonProperty("error")
    private String error;

    /**
     * 보고서 섹션
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ReportSection {

        @JsonProperty("section_id")
        private String sectionId;

        @JsonProperty("title")
        private String title;

        @JsonProperty("content")
        private String content;

        @JsonProperty("issue_id")
        private String issueId;
    }

    /**
     * 보고서 메타데이터
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ReportMetadata {

        @JsonProperty("total_issues")
        private int totalIssues;

        @JsonProperty("sections_generated")
        private int sectionsGenerated;

        @JsonProperty("processing_time_ms")
        private long processingTimeMs;

        @JsonProperty("model_used")
        private String modelUsed;
    }
}
