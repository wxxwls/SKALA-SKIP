package com.skala.skip.materiality.service.impl;

import com.skala.skip.ai.client.MaterialityAiClient;
import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.request.CreateSurveyAiRequest;
import com.skala.skip.ai.dto.request.SubmitSurveyResponseAiRequest;
import com.skala.skip.ai.dto.response.MaterialityMatrixAiResponse;
import com.skala.skip.ai.dto.response.SurveyAiResponse;
import com.skala.skip.ai.exception.AiServiceException;
import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import com.skala.skip.materiality.dto.request.CreateSurveyRequest;
import com.skala.skip.materiality.dto.request.SubmitSurveyResponseRequest;
import com.skala.skip.materiality.dto.response.MaterialityMatrixResponse;
import com.skala.skip.materiality.dto.response.SurveyResponse;
import com.skala.skip.materiality.service.MaterialityService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.stream.Collectors;

/**
 * 중대성 평가 서비스 구현
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class MaterialityServiceImpl implements MaterialityService {

    private final MaterialityAiClient materialityAiClient;

    @Override
    @Transactional
    public SurveyResponse createSurvey(String companyId, CreateSurveyRequest request) {
        log.info("설문 생성 요청 - companyId: {}, year: {}, stakeholderType: {}",
                companyId, request.getYear(), request.getStakeholderType());

        CreateSurveyAiRequest aiRequest = CreateSurveyAiRequest.builder()
                .companyId(companyId)
                .year(request.getYear())
                .issues(request.getIssues())
                .stakeholderType(request.getStakeholderType())
                .build();

        try {
            AiApiResponse<SurveyAiResponse> response = materialityAiClient.createSurvey(aiRequest).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.SVY_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.SVY_AI_001, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.SVY_AI_001, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            SurveyResponse result = mapToSurveyResponse(response.getData());
            log.info("설문 생성 완료 - surveyId: {}, questionCount: {}", result.getSurveyId(), result.getTotalQuestions());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("중대성 평가 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.SVY_AI_001, "설문 생성 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public Object submitSurveyResponse(String surveyId, SubmitSurveyResponseRequest request) {
        log.info("설문 응답 제출 - surveyId: {}", surveyId);

        SubmitSurveyResponseAiRequest aiRequest = SubmitSurveyResponseAiRequest.builder()
                .responses(request.getResponses())
                .respondentId(request.getRespondentId())
                .stakeholderType(request.getStakeholderType())
                .build();

        try {
            AiApiResponse<Object> response = materialityAiClient.submitSurveyResponse(surveyId, aiRequest).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.SVY_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.SVY_AI_001, response.getError().getMessage());
            }

            Object result = response.getData() != null ? response.getData() : "SUCCESS";
            log.info("설문 응답 제출 완료 - surveyId: {}", surveyId);
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("중대성 평가 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.SVY_AI_001, "설문 응답 제출 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public MaterialityMatrixResponse getMaterialityMatrix(String companyId, int year) {
        log.info("중대성 매트릭스 조회 - companyId: {}, year: {}", companyId, year);

        try {
            AiApiResponse<MaterialityMatrixAiResponse> response = materialityAiClient.getMaterialityMatrix(companyId, year).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.MAT_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.MAT_AI_001, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.MAT_AI_001, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            MaterialityMatrixResponse result = mapToMaterialityMatrixResponse(response.getData());
            log.info("중대성 매트릭스 조회 완료 - companyId: {}, totalIssues: {}", companyId, result.getTotalIssues());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("중대성 평가 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.MAT_AI_001, "중대성 매트릭스 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    private SurveyResponse mapToSurveyResponse(SurveyAiResponse data) {
        return SurveyResponse.builder()
                .success(data.isSuccess())
                .surveyId(data.getSurveyId())
                .totalQuestions(data.getTotalQuestions())
                .questions(data.getQuestions() != null ? data.getQuestions().stream()
                        .map(q -> SurveyResponse.SurveyQuestion.builder()
                                .id(q.getId())
                                .issueId(q.getIssueId())
                                .issueName(q.getIssueName())
                                .questionText(q.getQuestionText())
                                .questionType(q.getQuestionType())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }

    private MaterialityMatrixResponse mapToMaterialityMatrixResponse(MaterialityMatrixAiResponse data) {
        return MaterialityMatrixResponse.builder()
                .success(data.isSuccess())
                .companyId(data.getCompanyId())
                .year(data.getYear())
                .totalIssues(data.getTotalIssues())
                .highPriorityCount(data.getHighPriorityCount())
                .matrix(data.getMatrix() != null ? data.getMatrix().stream()
                        .map(m -> MaterialityMatrixResponse.MaterialityItem.builder()
                                .issueId(m.getIssueId())
                                .issueName(m.getIssueName())
                                .category(m.getCategory())
                                .financialScore(m.getFinancialScore())
                                .impactScore(m.getImpactScore())
                                .quadrant(m.getQuadrant())
                                .stakeholderImportance(m.getStakeholderImportance())
                                .businessImportance(m.getBusinessImportance())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }
}
