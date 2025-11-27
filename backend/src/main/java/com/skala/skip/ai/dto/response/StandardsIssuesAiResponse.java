package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * ESG 표준 이슈 목록 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StandardsIssuesAiResponse {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("issues")
    private List<StandardIssue> issues;

    @JsonProperty("total_count")
    private int totalCount;

    /**
     * 표준 이슈 정보
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class StandardIssue {

        @JsonProperty("id")
        private String id;

        @JsonProperty("name")
        private String name;

        @JsonProperty("category")
        private String category;

        @JsonProperty("description")
        private String description;
    }
}
