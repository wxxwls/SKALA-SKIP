package com.skala.skip.materiality.service;

import com.skala.skip.materiality.dto.request.CreateSurveyRequest;
import com.skala.skip.materiality.dto.request.SubmitSurveyResponseRequest;
import com.skala.skip.materiality.dto.response.MaterialityMatrixResponse;
import com.skala.skip.materiality.dto.response.SurveyResponse;

/**
 * 중대성 평가 서비스 인터페이스
 */
public interface MaterialityService {

    /**
     * 이해관계자 설문 생성
     */
    SurveyResponse createSurvey(String companyId, CreateSurveyRequest request);

    /**
     * 설문 응답 제출
     */
    Object submitSurveyResponse(String surveyId, SubmitSurveyResponseRequest request);

    /**
     * 중대성 매트릭스 조회
     */
    MaterialityMatrixResponse getMaterialityMatrix(String companyId, int year);
}
