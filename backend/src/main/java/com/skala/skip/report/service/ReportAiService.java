package com.skala.skip.report.service;

import com.skala.skip.report.dto.request.ReportGenerateRequest;
import com.skala.skip.report.dto.request.ReportModifyRequest;
import com.skala.skip.report.dto.response.ReportGenerateResponse;
import com.skala.skip.report.dto.response.ReportModifyResponse;

/**
 * 보고서 AI 서비스 인터페이스
 */
public interface ReportAiService {

    /**
     * ESG 보고서 생성
     */
    ReportGenerateResponse generateReport(String companyId, ReportGenerateRequest request);

    /**
     * 보고서 수정 (자연어 명령)
     */
    ReportModifyResponse modifyReport(String companyId, String companyName, ReportModifyRequest request);
}
