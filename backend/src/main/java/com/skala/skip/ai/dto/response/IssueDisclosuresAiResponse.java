package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 이슈별 공시 요건 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IssueDisclosuresAiResponse {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("issue_name")
    private String issueName;

    @JsonProperty("disclosures")
    private List<DisclosureRequirement> disclosures;

    @JsonProperty("total_count")
    private int totalCount;

    /**
     * 공시 요건 정보
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DisclosureRequirement {

        @JsonProperty("standard")
        private String standard;

        @JsonProperty("code")
        private String code;

        @JsonProperty("title")
        private String title;

        @JsonProperty("description")
        private String description;

        @JsonProperty("metrics")
        private List<String> metrics;
    }
}
