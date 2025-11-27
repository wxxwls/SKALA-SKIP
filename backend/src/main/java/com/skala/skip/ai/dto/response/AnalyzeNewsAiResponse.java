package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * 뉴스 분석 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AnalyzeNewsAiResponse {

    @JsonProperty("total_collected")
    private int totalCollected;

    @JsonProperty("unique_articles")
    private int uniqueArticles;

    @JsonProperty("articles")
    private List<NewsArticle> articles;

    @JsonProperty("statistics")
    private Statistics statistics;

    /**
     * 뉴스 기사 정보
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class NewsArticle {

        @JsonProperty("title")
        private String title;

        @JsonProperty("clean_title")
        private String cleanTitle;

        @JsonProperty("description")
        private String description;

        @JsonProperty("link")
        private String link;

        @JsonProperty("pubDate")
        private String pubDate;

        @JsonProperty("esg_issues")
        private List<String> esgIssues;

        @JsonProperty("esg_categories")
        private List<String> esgCategories;

        @JsonProperty("sentiment")
        private String sentiment;

        @JsonProperty("sentiment_score")
        private double sentimentScore;

        @JsonProperty("positive_count")
        private int positiveCount;

        @JsonProperty("negative_count")
        private int negativeCount;
    }

    /**
     * 분석 통계 정보
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Statistics {

        @JsonProperty("issue_statistics")
        private List<IssueStatistic> issueStatistics;

        @JsonProperty("sentiment_statistics")
        private SentimentStatistics sentimentStatistics;

        @JsonProperty("category_statistics")
        private Map<String, Integer> categoryStatistics;
    }

    /**
     * 이슈별 통계
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class IssueStatistic {

        @JsonProperty("issue")
        private String issue;

        @JsonProperty("count")
        private int count;

        @JsonProperty("percentage")
        private double percentage;

        @JsonProperty("esg_category")
        private String esgCategory;
    }

    /**
     * 감성 분석 통계
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SentimentStatistics {

        @JsonProperty("긍정")
        private int positive;

        @JsonProperty("부정")
        private int negative;

        @JsonProperty("중립")
        private int neutral;

        @JsonProperty("avg_score")
        private double avgScore;
    }
}
