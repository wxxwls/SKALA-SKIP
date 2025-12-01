package com.skala.skip.media.service.impl;

import com.skala.skip.ai.client.MediaAiClient;
import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.request.AnalyzeNewsAiRequest;
import com.skala.skip.ai.dto.response.AnalyzeNewsAiResponse;
import com.skala.skip.ai.exception.AiServiceException;
import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import com.skala.skip.media.dto.request.AnalyzeNewsRequest;
import com.skala.skip.media.dto.response.AnalyzeNewsResponse;
import com.skala.skip.media.service.MediaService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.stream.Collectors;

/**
 * 미디어 분석 서비스 구현
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class MediaServiceImpl implements MediaService {

    private final MediaAiClient mediaAiClient;

    @Override
    public Object getMediaData() {
        log.info("저장된 미디어 분석 데이터 조회");

        try {
            AiApiResponse<Object> response = mediaAiClient.getMediaData().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.MED_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.MED_AI_002, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("미디어 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.MED_AI_002, "미디어 데이터 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public AnalyzeNewsResponse analyzeNews(AnalyzeNewsRequest request) {
        log.info("뉴스 분석 요청 - keywords: {}, maxPages: {}", request.getKeywords(), request.getMaxPages());

        AnalyzeNewsAiRequest aiRequest = AnalyzeNewsAiRequest.builder()
                .keywords(request.getKeywords())
                .maxPages(request.getMaxPages())
                .build();

        try {
            AiApiResponse<AnalyzeNewsAiResponse> response = mediaAiClient.analyzeNews(aiRequest).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.MED_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.MED_AI_001, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.MED_AI_001, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            AnalyzeNewsResponse result = mapToResponse(response.getData());
            log.info("뉴스 분석 완료 - totalCollected: {}, uniqueArticles: {}",
                    result.getTotalCollected(), result.getUniqueArticles());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("미디어 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.MED_AI_001, "뉴스 분석 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public Object getEsgIssues() {
        log.info("ESG 18개 이슈 정의 조회");

        try {
            AiApiResponse<Object> response = mediaAiClient.getEsgIssues().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.MED_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.MED_AI_002, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("미디어 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.MED_AI_002, "ESG 이슈 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    private AnalyzeNewsResponse mapToResponse(AnalyzeNewsAiResponse data) {
        return AnalyzeNewsResponse.builder()
                .totalCollected(data.getTotalCollected())
                .uniqueArticles(data.getUniqueArticles())
                .articles(data.getArticles() != null ? data.getArticles().stream()
                        .map(a -> AnalyzeNewsResponse.NewsArticle.builder()
                                .title(a.getTitle())
                                .cleanTitle(a.getCleanTitle())
                                .description(a.getDescription())
                                .link(a.getLink())
                                .pubDate(a.getPubDate())
                                .esgIssues(a.getEsgIssues())
                                .esgCategories(a.getEsgCategories())
                                .sentiment(a.getSentiment())
                                .sentimentScore(a.getSentimentScore())
                                .positiveCount(a.getPositiveCount())
                                .negativeCount(a.getNegativeCount())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .statistics(mapStatistics(data.getStatistics()))
                .build();
    }

    private AnalyzeNewsResponse.Statistics mapStatistics(AnalyzeNewsAiResponse.Statistics stats) {
        if (stats == null) return null;

        return AnalyzeNewsResponse.Statistics.builder()
                .categoryStatistics(stats.getCategoryStatistics())
                .issueStatistics(stats.getIssueStatistics() != null ? stats.getIssueStatistics().stream()
                        .map(i -> AnalyzeNewsResponse.IssueStatistic.builder()
                                .issue(i.getIssue())
                                .count(i.getCount())
                                .percentage(i.getPercentage())
                                .esgCategory(i.getEsgCategory())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .sentimentStatistics(stats.getSentimentStatistics() != null ?
                        AnalyzeNewsResponse.SentimentStatistics.builder()
                                .positive(stats.getSentimentStatistics().getPositive())
                                .negative(stats.getSentimentStatistics().getNegative())
                                .neutral(stats.getSentimentStatistics().getNeutral())
                                .avgScore(stats.getSentimentStatistics().getAvgScore())
                                .build() : null)
                .build();
    }
}
