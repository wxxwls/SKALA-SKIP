package com.skala.skip.issue.service.impl;

import com.skala.skip.ai.client.IssuePoolAiClient;
import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.common.CompanyContext;
import com.skala.skip.ai.dto.request.IssuePoolGenerateAiRequest;
import com.skala.skip.ai.dto.request.ScoreTopicAiRequest;
import com.skala.skip.ai.dto.response.IssuePoolAiResponse;
import com.skala.skip.ai.dto.response.ScoreTopicAiResponse;
import com.skala.skip.ai.exception.AiServiceException;
import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import com.skala.skip.issue.dto.request.IssuePoolCreateRequest;
import com.skala.skip.issue.dto.request.ScoreTopicRequest;
import com.skala.skip.issue.dto.response.IssuePoolResponse;
import com.skala.skip.issue.dto.response.ScoreTopicResponse;
import com.skala.skip.issue.service.IssuePoolService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.stream.Collectors;

/**
 * 이슈풀 서비스 구현
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class IssuePoolServiceImpl implements IssuePoolService {

    private final IssuePoolAiClient issuePoolAiClient;

    @Override
    @Transactional
    public IssuePoolResponse generateIssuePool(String companyId, IssuePoolCreateRequest request) {
        log.info("이슈풀 생성 요청 - companyId: {}, companyName: {}, year: {}",
                companyId, request.getCompanyName(), request.getYear());

        CompanyContext companyContext = CompanyContext.builder()
                .companyId(companyId)
                .companyName(request.getCompanyName())
                .industry(request.getIndustry())
                .year(request.getYear())
                .build();

        IssuePoolGenerateAiRequest aiRequest = IssuePoolGenerateAiRequest.builder()
                .companyContext(companyContext)
                .useStandards(request.isUseStandards())
                .useBenchmarks(request.isUseBenchmarks())
                .useInternal(request.isUseInternal())
                .useNews(request.isUseNews())
                .maxTopics(request.getMaxTopics())
                .build();

        try {
            AiApiResponse<IssuePoolAiResponse> response = issuePoolAiClient.generateIssuePool(aiRequest).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.ISS_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.ISS_AI_001, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.ISS_AI_001, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            IssuePoolResponse result = mapToIssuePoolResponse(response.getData());
            log.info("이슈풀 생성 완료 - companyId: {}, topicCount: {}", companyId, result.getTotalCount());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("이슈풀 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.ISS_AI_001, "이슈풀 처리 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public ScoreTopicResponse scoreTopic(String companyId, ScoreTopicRequest request) {
        log.info("토픽 점수화 요청 - companyId: {}, topicTitle: {}", companyId, request.getTopicTitle());

        CompanyContext companyContext = CompanyContext.builder()
                .companyId(companyId)
                .companyName(request.getCompanyName())
                .industry(request.getIndustry())
                .year(request.getYear())
                .build();

        ScoreTopicAiRequest aiRequest = ScoreTopicAiRequest.builder()
                .companyContext(companyContext)
                .topicTitle(request.getTopicTitle())
                .topicDescription(request.getTopicDescription())
                .build();

        try {
            AiApiResponse<ScoreTopicAiResponse> response = issuePoolAiClient.scoreTopic(aiRequest).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.ISS_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.ISS_AI_002, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.ISS_AI_002, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            ScoreTopicResponse result = mapToScoreTopicResponse(response.getData());
            log.info("토픽 점수화 완료 - topicTitle: {}, financialScore: {}, impactScore: {}",
                    result.getTopicTitle(), result.getFinancialScore(), result.getImpactScore());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("토픽 점수화 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.ISS_AI_002, "토픽 점수화 중 오류 발생: " + e.getMessage(), e);
        }
    }

    private IssuePoolResponse mapToIssuePoolResponse(IssuePoolAiResponse data) {
        return IssuePoolResponse.builder()
                .companyId(data.getCompanyId())
                .year(data.getYear())
                .totalCount(data.getTotalCount())
                .sourcesUsed(data.getSourcesUsed())
                .topics(data.getTopics() != null ? data.getTopics().stream()
                        .map(this::mapToTopicResponse)
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }

    private IssuePoolResponse.TopicResponse mapToTopicResponse(IssuePoolAiResponse.TopicItem topic) {
        return IssuePoolResponse.TopicResponse.builder()
                .topicId(topic.getTopicId())
                .topicTitle(topic.getTopicTitle())
                .category(topic.getCategory())
                .description(topic.getDescription())
                .financialScore(topic.getFinancialScore())
                .impactScore(topic.getImpactScore())
                .keywords(topic.getKeywords())
                .sources(topic.getSources() != null ? topic.getSources().stream()
                        .map(this::mapToSourceResponse)
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }

    private IssuePoolResponse.SourceResponse mapToSourceResponse(IssuePoolAiResponse.SourceAttribution source) {
        return IssuePoolResponse.SourceResponse.builder()
                .sourceType(source.getSourceType())
                .sourceName(source.getSourceName())
                .relevanceScore(source.getRelevanceScore())
                .build();
    }

    private ScoreTopicResponse mapToScoreTopicResponse(ScoreTopicAiResponse data) {
        return ScoreTopicResponse.builder()
                .topicTitle(data.getTopicTitle())
                .financialScore(data.getFinancialScore())
                .impactScore(data.getImpactScore())
                .financialRationale(data.getFinancialRationale())
                .impactRationale(data.getImpactRationale())
                .sources(data.getSources() != null ? data.getSources().stream()
                        .map(this::mapToSourceResponse)
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }
}
