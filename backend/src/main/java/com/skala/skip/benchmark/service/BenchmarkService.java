package com.skala.skip.benchmark.service;

import com.skala.skip.benchmark.dto.request.BenchmarkAnalyzeRequest;
import com.skala.skip.benchmark.dto.response.BenchmarkAnalyzeResponse;
import com.skala.skip.benchmark.dto.response.BenchmarkDocumentResponse;

/**
 * 벤치마킹 서비스 인터페이스
 */
public interface BenchmarkService {

    /**
     * 키워드 기반 분석
     */
    BenchmarkAnalyzeResponse analyze(BenchmarkAnalyzeRequest request);

    /**
     * SK 18개 이슈 기반 분석
     */
    Object analyzeIssues(String companyName, String pdfPath);

    /**
     * SK 18개 이슈 목록 조회
     */
    Object getSkIssues();

    /**
     * 캐시된 분석 데이터 조회
     */
    Object getCachedData();

    /**
     * 문서 목록 조회
     */
    BenchmarkDocumentResponse getDocuments();

    /**
     * 문서 삭제
     */
    Object deleteDocument(String documentId);

    /**
     * 캐시 초기화
     */
    Object clearCache();

    /**
     * 전체 재분석
     */
    Object reanalyzeAll();
}
