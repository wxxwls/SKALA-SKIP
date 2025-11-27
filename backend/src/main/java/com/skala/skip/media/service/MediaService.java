package com.skala.skip.media.service;

import com.skala.skip.media.dto.request.AnalyzeNewsRequest;
import com.skala.skip.media.dto.response.AnalyzeNewsResponse;

/**
 * 미디어 분석 서비스 인터페이스
 */
public interface MediaService {

    /**
     * 저장된 미디어 분석 데이터 조회
     */
    Object getMediaData();

    /**
     * 키워드 기반 뉴스 수집 및 분석
     */
    AnalyzeNewsResponse analyzeNews(AnalyzeNewsRequest request);

    /**
     * ESG 18개 이슈 정의 조회
     */
    Object getEsgIssues();
}
