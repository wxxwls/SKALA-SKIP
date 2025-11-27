package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * ESG 이슈풀 생성 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IssuePoolAiResponse {

    @JsonProperty("company_id")
    private String companyId;

    @JsonProperty("year")
    private int year;

    @JsonProperty("topics")
    private List<TopicItem> topics;

    @JsonProperty("total_count")
    private int totalCount;

    @JsonProperty("sources_used")
    private List<String> sourcesUsed;

    /**
     * 이슈풀 토픽 아이템
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TopicItem {

        @JsonProperty("topic_id")
        private String topicId;

        @JsonProperty("topic_title")
        private String topicTitle;

        @JsonProperty("category")
        private String category;

        @JsonProperty("description")
        private String description;

        @JsonProperty("financial_score")
        private double financialScore;

        @JsonProperty("impact_score")
        private double impactScore;

        @JsonProperty("sources")
        private List<SourceAttribution> sources;

        @JsonProperty("keywords")
        private List<String> keywords;
    }

    /**
     * 출처 정보
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SourceAttribution {

        @JsonProperty("source_type")
        private String sourceType;

        @JsonProperty("source_name")
        private String sourceName;

        @JsonProperty("relevance_score")
        private double relevanceScore;
    }
}
