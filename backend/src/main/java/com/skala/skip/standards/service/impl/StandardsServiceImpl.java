package com.skala.skip.standards.service.impl;

import com.skala.skip.ai.client.StandardsAiClient;
import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.response.IssueDisclosuresAiResponse;
import com.skala.skip.ai.dto.response.StandardsDocumentAiResponse;
import com.skala.skip.ai.dto.response.StandardsIssuesAiResponse;
import com.skala.skip.ai.exception.AiServiceException;
import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import com.skala.skip.standards.dto.response.IssueDisclosuresResponse;
import com.skala.skip.standards.dto.response.StandardsDocumentResponse;
import com.skala.skip.standards.dto.response.StandardsIssuesResponse;
import com.skala.skip.standards.service.StandardsService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.stream.Collectors;

/**
 * ESG 표준 서비스 구현
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class StandardsServiceImpl implements StandardsService {

    private final StandardsAiClient standardsAiClient;

    @Override
    public StandardsIssuesResponse getIssues() {
        log.info("한국 중대성 이슈 18개 목록 조회");

        try {
            AiApiResponse<StandardsIssuesAiResponse> response = standardsAiClient.getIssues().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_002, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.STD_AI_002, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            StandardsIssuesResponse result = mapToIssuesResponse(response.getData());
            log.info("이슈 목록 조회 완료 - totalCount: {}", result.getTotalCount());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_002, "이슈 목록 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public Object getIssuesWithDisclosures() {
        log.info("이슈별 공시 요건 매핑 조회");

        try {
            AiApiResponse<Object> response = standardsAiClient.getIssuesWithDisclosures().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_002, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_002, "이슈별 공시 요건 매핑 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public IssueDisclosuresResponse getIssueDisclosures(String issueName) {
        log.info("특정 이슈 공시 요건 조회 - issueName: {}", issueName);

        try {
            AiApiResponse<IssueDisclosuresAiResponse> response = standardsAiClient.getIssueDisclosures(issueName).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_002, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.STD_AI_002, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            IssueDisclosuresResponse result = mapToDisclosuresResponse(response.getData());
            log.info("이슈 공시 요건 조회 완료 - issueName: {}, totalCount: {}",
                    result.getIssueName(), result.getTotalCount());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_002, "이슈 공시 요건 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public Object analyzeIssue(String issueName) {
        log.info("AI 기반 이슈 분석 - issueName: {}", issueName);

        try {
            AiApiResponse<Object> response = standardsAiClient.analyzeIssue(issueName).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_001, response.getError().getMessage());
            }

            log.info("이슈 분석 완료 - issueName: {}", issueName);
            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_001, "이슈 분석 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public Object searchDisclosures(String query) {
        log.info("공시 요건 검색 - query: {}", query);

        try {
            AiApiResponse<Object> response = standardsAiClient.searchDisclosures(query).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_002, response.getError().getMessage());
            }

            log.info("공시 요건 검색 완료 - query: {}", query);
            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_002, "공시 요건 검색 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public Object getStatistics() {
        log.info("통계 정보 조회");

        try {
            AiApiResponse<Object> response = standardsAiClient.getStatistics().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_002, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_002, "통계 정보 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public Object indexDocuments() {
        log.info("GRI/SASB PDF 인덱싱 시작");

        try {
            AiApiResponse<Object> response = standardsAiClient.indexDocuments().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_001, response.getError().getMessage());
            }

            log.info("문서 인덱싱 완료");
            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_001, "문서 인덱싱 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public Object resetChromaDB() {
        log.info("ChromaDB 리셋");

        try {
            AiApiResponse<Object> response = standardsAiClient.resetChromaDB().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_001, response.getError().getMessage());
            }

            log.info("ChromaDB 리셋 완료");
            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_001, "ChromaDB 리셋 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public Object getDocumentCount() {
        log.info("인덱싱 문서 수 조회");

        try {
            AiApiResponse<Object> response = standardsAiClient.getDocumentCount().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_002, response.getError().getMessage());
            }

            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_002, "문서 수 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    public StandardsDocumentResponse getDocuments() {
        log.info("문서 목록 조회");

        try {
            AiApiResponse<StandardsDocumentAiResponse> response = standardsAiClient.getDocuments().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_002, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.STD_AI_002, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            StandardsDocumentResponse result = mapToDocumentResponse(response.getData());
            log.info("문서 목록 조회 완료 - totalCount: {}", result.getTotalCount());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_002, "문서 목록 조회 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public Object deleteDocument(String documentId) {
        log.info("문서 삭제 - documentId: {}", documentId);

        try {
            AiApiResponse<Object> response = standardsAiClient.deleteDocument(documentId).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_001, response.getError().getMessage());
            }

            log.info("문서 삭제 완료 - documentId: {}", documentId);
            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_001, "문서 삭제 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public Object embedDocuments() {
        log.info("문서 임베딩 시작");

        try {
            AiApiResponse<Object> response = standardsAiClient.embedDocuments().block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.STD_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.STD_AI_001, response.getError().getMessage());
            }

            log.info("문서 임베딩 완료");
            return response.getData() != null ? response.getData() : Collections.emptyMap();

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("표준 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.STD_AI_001, "문서 임베딩 중 오류 발생: " + e.getMessage(), e);
        }
    }

    private StandardsIssuesResponse mapToIssuesResponse(StandardsIssuesAiResponse data) {
        return StandardsIssuesResponse.builder()
                .totalCount(data.getTotalCount())
                .issues(data.getIssues() != null ? data.getIssues().stream()
                        .map(i -> StandardsIssuesResponse.StandardIssue.builder()
                                .id(i.getId())
                                .name(i.getName())
                                .category(i.getCategory())
                                .description(i.getDescription())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }

    private IssueDisclosuresResponse mapToDisclosuresResponse(IssueDisclosuresAiResponse data) {
        return IssueDisclosuresResponse.builder()
                .issueName(data.getIssueName())
                .totalCount(data.getTotalCount())
                .disclosures(data.getDisclosures() != null ? data.getDisclosures().stream()
                        .map(d -> IssueDisclosuresResponse.DisclosureRequirement.builder()
                                .standard(d.getStandard())
                                .code(d.getCode())
                                .title(d.getTitle())
                                .description(d.getDescription())
                                .metrics(d.getMetrics())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }

    private StandardsDocumentResponse mapToDocumentResponse(StandardsDocumentAiResponse data) {
        return StandardsDocumentResponse.builder()
                .totalCount(data.getTotalCount())
                .documents(data.getDocuments() != null ? data.getDocuments().stream()
                        .map(d -> StandardsDocumentResponse.DocumentInfo.builder()
                                .id(d.getId())
                                .name(d.getName())
                                .type(d.getType())
                                .size(d.getSize())
                                .uploadedAt(d.getUploadedAt())
                                .status(d.getStatus())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }
}
