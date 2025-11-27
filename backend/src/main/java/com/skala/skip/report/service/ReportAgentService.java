package com.skala.skip.report.service;

import com.skala.skip.report.dto.request.ReportDraftRequest;
import com.skala.skip.report.dto.response.ReportDraftResponse;

public interface ReportAgentService {
    ReportDraftResponse generateDraft(Long reportId, String sectionCode, ReportDraftRequest request);
}
