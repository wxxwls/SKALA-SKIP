package com.skala.skip.report.service.impl;

import com.skala.skip.ai.client.ReportAiClient;
import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.common.CompanyContext;
import com.skala.skip.ai.dto.request.ReportGenerateAiRequest;
import com.skala.skip.ai.dto.request.ReportModifyAiRequest;
import com.skala.skip.ai.dto.response.ReportGenerateAiResponse;
import com.skala.skip.ai.dto.response.ReportModifyAiResponse;
import com.skala.skip.ai.exception.AiServiceException;
import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import com.skala.skip.report.dto.request.ReportGenerateRequest;
import com.skala.skip.report.dto.request.ReportModifyRequest;
import com.skala.skip.report.dto.response.ReportGenerateResponse;
import com.skala.skip.report.dto.response.ReportModifyResponse;
import com.skala.skip.report.service.ReportAiService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.stream.Collectors;

/**
 * 보고서 AI 서비스 구현
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class ReportAiServiceImpl implements ReportAiService {

    private final ReportAiClient reportAiClient;

    @Override
    @Transactional
    public ReportGenerateResponse generateReport(String companyId, ReportGenerateRequest request) {
        log.info("보고서 생성 요청 - companyId: {}, companyName: {}, issueCount: {}",
                companyId, request.getCompanyName(), request.getIssues().size());

        CompanyContext companyContext = CompanyContext.builder()
                .companyId(companyId)
                .companyName(request.getCompanyName())
                .industry(request.getIndustry())
                .year(request.getYear())
                .build();

        ReportGenerateAiRequest aiRequest = ReportGenerateAiRequest.builder()
                .companyContext(companyContext)
                .issues(request.getIssues().stream()
                        .map(this::mapToAiIssueItem)
                        .collect(Collectors.toList()))
                .previousReport(request.getPreviousReport())
                .build();

        try {
            AiApiResponse<ReportGenerateAiResponse> response = reportAiClient.generateReport(aiRequest).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.RPT_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.RPT_AI_001, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.RPT_AI_001, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            ReportGenerateResponse result = mapToReportGenerateResponse(response.getData());
            log.info("보고서 생성 완료 - companyId: {}, sectionsGenerated: {}",
                    companyId, result.getMetadata() != null ? result.getMetadata().getSectionsGenerated() : 0);
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("보고서 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.RPT_AI_001, "보고서 생성 중 오류 발생: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public ReportModifyResponse modifyReport(String companyId, String companyName, ReportModifyRequest request) {
        log.info("보고서 수정 요청 - companyId: {}, instruction: {}", companyId, request.getInstruction());

        ReportModifyAiRequest aiRequest = ReportModifyAiRequest.builder()
                .companyName(companyName)
                .currentReport(request.getCurrentReport())
                .instruction(request.getInstruction())
                .build();

        try {
            AiApiResponse<ReportModifyAiResponse> response = reportAiClient.modifyReport(aiRequest).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.RPT_AI_002, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                log.error("AI 서비스 에러 응답 - code: {}, message: {}",
                        response.getError().getCode(), response.getError().getMessage());
                throw new AiServiceException(ESGErrorCode.RPT_AI_002, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.RPT_AI_002, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            ReportModifyResponse result = mapToReportModifyResponse(response.getData());
            log.info("보고서 수정 완료 - companyId: {}, changesSummary: {}", companyId, result.getChangesSummary());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("보고서 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.RPT_AI_002, "보고서 수정 중 오류 발생: " + e.getMessage(), e);
        }
    }

    private ReportGenerateAiRequest.IssueItem mapToAiIssueItem(ReportGenerateRequest.IssueItem item) {
        return ReportGenerateAiRequest.IssueItem.builder()
                .issueId(item.getIssueId())
                .issueName(item.getIssueName())
                .category(item.getCategory())
                .financialScore(item.getFinancialScore())
                .impactScore(item.getImpactScore())
                .description(item.getDescription())
                .kpis(item.getKpis() != null ? item.getKpis().stream()
                        .map(kpi -> ReportGenerateAiRequest.KpiItem.builder()
                                .name(kpi.getName())
                                .value(kpi.getValue())
                                .unit(kpi.getUnit())
                                .year(kpi.getYear())
                                .target(kpi.getTarget())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }

    private ReportGenerateResponse mapToReportGenerateResponse(ReportGenerateAiResponse data) {
        return ReportGenerateResponse.builder()
                .success(data.isSuccess())
                .reportHtml(data.getReportHtml())
                .error(data.getError())
                .sections(data.getSections() != null ? data.getSections().stream()
                        .map(s -> ReportGenerateResponse.ReportSection.builder()
                                .sectionId(s.getSectionId())
                                .title(s.getTitle())
                                .content(s.getContent())
                                .issueId(s.getIssueId())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .metadata(data.getMetadata() != null ? ReportGenerateResponse.ReportMetadata.builder()
                        .totalIssues(data.getMetadata().getTotalIssues())
                        .sectionsGenerated(data.getMetadata().getSectionsGenerated())
                        .processingTimeMs(data.getMetadata().getProcessingTimeMs())
                        .modelUsed(data.getMetadata().getModelUsed())
                        .build() : null)
                .build();
    }

    private ReportModifyResponse mapToReportModifyResponse(ReportModifyAiResponse data) {
        return ReportModifyResponse.builder()
                .success(data.isSuccess())
                .modifiedReport(data.getModifiedReport())
                .changesSummary(data.getChangesSummary())
                .message(data.getMessage())
                .build();
    }
}
