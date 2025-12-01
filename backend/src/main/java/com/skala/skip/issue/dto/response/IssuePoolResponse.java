package com.skala.skip.issue.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * 이슈풀 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IssuePoolResponse {

    private String companyId;
    private int year;
    private List<TopicResponse> topics;
    private int totalCount;
    private List<String> sourcesUsed;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TopicResponse {
        private String topicId;
        private String topicTitle;
        private String category;
        private String description;
        private double financialScore;
        private double impactScore;
        private List<SourceResponse> sources;
        private List<String> keywords;
    }

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SourceResponse {
        private String sourceType;
        private String sourceName;
        private double relevanceScore;
    }
}
