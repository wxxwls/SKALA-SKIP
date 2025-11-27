package com.skala.skip.report.service;

import com.skala.skip.report.dto.request.ReportCreateRequest;
import com.skala.skip.report.dto.response.ReportCreateResponse;

public interface ReportCreateService {
    ReportCreateResponse createReport(ReportCreateRequest request);
}
