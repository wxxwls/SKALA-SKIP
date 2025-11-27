package com.skala.skip.media.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;
import java.util.Map;

/**
 * 뉴스 분석 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AnalyzeNewsResponse {

    private int totalCollected;
    private int uniqueArticles;
    private List<NewsArticle> articles;
    private Statistics statistics;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class NewsArticle {
        private String title;
        private String cleanTitle;
        private String description;
        private String link;
        private String pubDate;
        private List<String> esgIssues;
        private List<String> esgCategories;
        private String sentiment;
        private double sentimentScore;
        private int positiveCount;
        private int negativeCount;
    }

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Statistics {
        private List<IssueStatistic> issueStatistics;
        private SentimentStatistics sentimentStatistics;
        private Map<String, Integer> categoryStatistics;
    }

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class IssueStatistic {
        private String issue;
        private int count;
        private double percentage;
        private String esgCategory;
    }

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SentimentStatistics {
        private int positive;
        private int negative;
        private int neutral;
        private double avgScore;
    }
}
