package com.skala.skip.standards.service;

import com.skala.skip.standards.dto.response.IssueDisclosuresResponse;
import com.skala.skip.standards.dto.response.StandardsDocumentResponse;
import com.skala.skip.standards.dto.response.StandardsIssuesResponse;

/**
 * ESG 표준 서비스 인터페이스
 */
public interface StandardsService {

    /**
     * 한국 중대성 이슈 18개 목록 조회
     */
    StandardsIssuesResponse getIssues();

    /**
     * 이슈별 공시 요건 매핑 조회
     */
    Object getIssuesWithDisclosures();

    /**
     * 특정 이슈 공시 요건 조회
     */
    IssueDisclosuresResponse getIssueDisclosures(String issueName);

    /**
     * AI 기반 이슈 분석
     */
    Object analyzeIssue(String issueName);

    /**
     * 공시 요건 검색
     */
    Object searchDisclosures(String query);

    /**
     * 통계 정보 조회
     */
    Object getStatistics();

    /**
     * GRI/SASB PDF 인덱싱
     */
    Object indexDocuments();

    /**
     * ChromaDB 리셋
     */
    Object resetChromaDB();

    /**
     * 인덱싱 문서 수 조회
     */
    Object getDocumentCount();

    /**
     * 문서 목록 조회
     */
    StandardsDocumentResponse getDocuments();

    /**
     * 문서 삭제
     */
    Object deleteDocument(String documentId);

    /**
     * 문서 임베딩 시작
     */
    Object embedDocuments();
}
