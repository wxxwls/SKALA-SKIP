package com.skala.skip.report.service.impl;

import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import com.skala.skip.report.client.ReportAgentClient;
import com.skala.skip.report.dto.request.ReportDraftRequest;
import com.skala.skip.report.dto.response.ReportDraftResponse;
import com.skala.skip.report.exception.ReportAgentException;
import com.skala.skip.report.service.ReportAgentService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class ReportAgentServiceImpl implements ReportAgentService {

    private final ReportAgentClient reportAgentClient;

    @Override
    @Transactional
    public ReportDraftResponse generateDraft(Long reportId, String sectionCode, ReportDraftRequest request) {
        log.info("보고서 초안 생성 요청 - reportId: {}, sectionCode: {}, maxTokens: {}, tone: {}, language: {}",
                reportId,
                sectionCode,
                request.getMaxTokens(),
                request.getTone(),
                request.getLanguage());

        try {
            ReportDraftResponse response = reportAgentClient
                    .generateDraftReport(reportId, sectionCode, request)
                    .block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.RPT_AI_001, "FastAPI로부터 응답을 받지 못했습니다.");
            }

            int contentLength = response.getDraftText() != null ? response.getDraftText().length() : 0;
            int referencesCount = response.getReferences() != null ? response.getReferences().size() : 0;
            log.info("보고서 초안 생성 완료 - reportId: {}, sectionCode: {}, draft length: {}, references count: {}",
                    reportId, sectionCode, contentLength, referencesCount);

            return response;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("보고서 초안 생성 실패 - reportId: {}, sectionCode: {}", reportId, sectionCode, e);
            throw new BusinessException(
                    ESGErrorCode.RPT_AI_001,
                    String.format("보고서 초안 생성 중 오류 발생: %s", e.getMessage()),
                    e
            );
        }
    }
}

