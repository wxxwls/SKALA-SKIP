package com.skala.skip.benchmark.service.impl;

import com.skala.skip.ai.client.BenchmarkAiClient;
import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.request.BenchmarkAnalyzeAiRequest;
import com.skala.skip.ai.dto.response.BenchmarkAnalyzeAiResponse;
import com.skala.skip.ai.dto.response.BenchmarkDocumentAiResponse;
import com.skala.skip.ai.exception.AiServiceException;
import com.skala.skip.benchmark.dto.request.BenchmarkAnalyzeRequest;
import com.skala.skip.benchmark.dto.response.BenchmarkAnalyzeResponse;
import com.skala.skip.benchmark.dto.response.BenchmarkDocumentResponse;
import com.skala.skip.benchmark.service.BenchmarkService;
import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 벤치마킹 서비스 구현
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class BenchmarkServiceImpl implements BenchmarkService {

    private final BenchmarkAiClient benchmarkAiClient;

    @Override
    public BenchmarkAnalyzeResponse analyze(BenchmarkAnalyzeRequest request) {
        log.info("벤치마킹 분석 요청 - keyword: {}, companyCount: {}",
                request.getKeyword(), request.getCompanies().size());

        BenchmarkAnalyzeAiRequest aiRequest = BenchmarkAnalyzeAiRequest.builder()
                .keyword(request.getKeyword())
                .companies(request.getCompanies().stream()
                        .map(c -> BenchmarkAnalyzeAiRequest.CompanyInfo.builder()
                                .name(c.getName())
                                .path(c.getPath())
                                .build())
                        .collect(Collectors.toList()))
                .build();

        try {
            AiApiResponse<BenchmarkAnalyzeAiResponse> response = benchmarkAiClient.analyze(aiRequest).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.BMK_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                throw new AiServiceException(ESGErrorCode.BMK_AI_001, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.BMK_AI_001, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            BenchmarkAnalyzeResponse result = mapToAnalyzeResponse(response.getData());
            log.info("벤치마킹 분석 완료 - keyword: {}", request.getKeyword());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("벤치마킹 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.BMK_AI_001, "벤치마킹 처리 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public Object analyzeIssues(String companyName, String pdfPath) {
        log.info("SK 이슈 기반 분석 - companyName: {}", companyName);

        try {
            AiApiResponse<Object> response = benchmarkAiClient.analyzeIssues(companyName, pdfPath).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.BMK_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                throw new AiServiceException(ESGErrorCode.BMK_AI_001, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("SK 이슈 분석 오류", e);
            throw new BusinessException(ESGErrorCode.BMK_AI_001, "SK 이슈 분석 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public Object getSkIssues() {
        log.info("SK 18개 이슈 목록 조회");

        try {
            AiApiResponse<Object> response = benchmarkAiClient.getSkIssues().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.BMK_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                throw new AiServiceException(ESGErrorCode.BMK_AI_001, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("SK 이슈 목록 조회 오류", e);
            throw new BusinessException(ESGErrorCode.BMK_AI_001, "SK 이슈 목록 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public Object getCachedData() {
        log.info("캐시된 분석 데이터 조회");

        try {
            AiApiResponse<Object> response = benchmarkAiClient.getCachedData().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.BMK_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                throw new AiServiceException(ESGErrorCode.BMK_AI_001, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("캐시 데이터 조회 오류", e);
            throw new BusinessException(ESGErrorCode.BMK_AI_001, "캐시 데이터 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public BenchmarkDocumentResponse getDocuments() {
        log.info("벤치마킹 문서 목록 조회");

        try {
            AiApiResponse<BenchmarkDocumentAiResponse> response = benchmarkAiClient.getDocuments().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.BMK_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                throw new AiServiceException(ESGErrorCode.BMK_AI_001, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.BMK_AI_001, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            return mapToDocumentResponse(response.getData());

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("문서 목록 조회 오류", e);
            throw new BusinessException(ESGErrorCode.BMK_AI_001, "문서 목록 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public Object deleteDocument(String documentId) {
        log.info("벤치마킹 문서 삭제 - documentId: {}", documentId);

        try {
            AiApiResponse<Object> response = benchmarkAiClient.deleteDocument(documentId).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.BMK_AI_003, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                throw new AiServiceException(ESGErrorCode.BMK_AI_003, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : "SUCCESS";

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("문서 삭제 오류", e);
            throw new BusinessException(ESGErrorCode.BMK_AI_003, "문서 삭제 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public Object clearCache() {
        log.info("벤치마킹 캐시 초기화");

        try {
            AiApiResponse<Object> response = benchmarkAiClient.clearCache().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.BMK_AI_004, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                throw new AiServiceException(ESGErrorCode.BMK_AI_004, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : "SUCCESS";

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("캐시 초기화 오류", e);
            throw new BusinessException(ESGErrorCode.BMK_AI_004, "캐시 초기화 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public Object reanalyzeAll() {
        log.info("전체 재분석 시작");

        try {
            AiApiResponse<Object> response = benchmarkAiClient.reanalyzeAll().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.BMK_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                throw new AiServiceException(ESGErrorCode.BMK_AI_001, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : "SUCCESS";

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("전체 재분석 오류", e);
            throw new BusinessException(ESGErrorCode.BMK_AI_001, "전체 재분석 중 오류 발생: " + e.getMessage(), e);
        }
    }

    private BenchmarkAnalyzeResponse mapToAnalyzeResponse(BenchmarkAnalyzeAiResponse data) {
        Map<String, BenchmarkAnalyzeResponse.CompanyResult> results = null;
        if (data.getResults() != null) {
            results = data.getResults().entrySet().stream()
                    .collect(Collectors.toMap(
                            Map.Entry::getKey,
                            e -> BenchmarkAnalyzeResponse.CompanyResult.builder()
                                    .coverage(e.getValue().getCoverage())
                                    .response(e.getValue().getResponse())
                                    .sourcePages(e.getValue().getSourcePages())
                                    .build()
                    ));
        }

        return BenchmarkAnalyzeResponse.builder()
                .success(data.isSuccess())
                .keyword(data.getKeyword())
                .results(results)
                .summary(data.getSummary() != null ? BenchmarkAnalyzeResponse.Summary.builder()
                        .fullCoverage(data.getSummary().getFullCoverage())
                        .partialCoverage(data.getSummary().getPartialCoverage())
                        .noCoverage(data.getSummary().getNoCoverage())
                        .build() : null)
                .build();
    }

    private BenchmarkDocumentResponse mapToDocumentResponse(BenchmarkDocumentAiResponse data) {
        return BenchmarkDocumentResponse.builder()
                .success(data.isSuccess())
                .totalCount(data.getTotalCount())
                .documents(data.getDocuments() != null ? data.getDocuments().stream()
                        .map(d -> BenchmarkDocumentResponse.DocumentInfo.builder()
                                .id(d.getId())
                                .name(d.getName())
                                .size(d.getSize())
                                .uploadedAt(d.getUploadedAt())
                                .status(d.getStatus())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }
}
