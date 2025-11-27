package com.skala.skip.report.service;

import com.skala.skip.report.dto.response.ReportExportResponse;

public interface ReportExportService {
    ReportExportResponse exportReport(Long reportId);
}
