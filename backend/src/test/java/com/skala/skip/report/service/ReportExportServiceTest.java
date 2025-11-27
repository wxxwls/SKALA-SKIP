package com.skala.skip.report.service;

import com.skala.skip.report.dto.response.ReportExportResponse;
import com.skala.skip.report.service.impl.ReportExportServiceImpl;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class ReportExportServiceTest {

    private final ReportExportService reportExportService = new ReportExportServiceImpl();

    @Test
    @DisplayName("보고서 다운로드 성공 - 정상 응답 반환")
    void exportReport_Success() {
        // given
        Long reportId = 1L;

        // when
        ReportExportResponse response = reportExportService.exportReport(reportId);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getFileName()).isNotNull();
        assertThat(response.getContentType()).isNotNull();
        assertThat(response.getFileContent()).isNotNull();
    }
}
