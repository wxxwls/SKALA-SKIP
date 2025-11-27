package com.skala.skip.report.service;

import com.skala.skip.report.dto.request.ReportCreateRequest;
import com.skala.skip.report.dto.response.ReportCreateResponse;
import com.skala.skip.report.service.impl.ReportCreateServiceImpl;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class ReportCreateServiceTest {

    private final ReportCreateService reportCreateService = new ReportCreateServiceImpl();

    @Test
    @DisplayName("보고서 생성 성공 - 정상 응답 반환")
    void createReport_Success() {
        // given
        ReportCreateRequest request = ReportCreateRequest.builder()
                .companyId(101L)
                .year(2024)
                .issuePoolId(555L)
                .title("2024 SKT 지속가능경영보고서")
                .templateId(1L)
                .colorThemeId(1L)
                .build();

        // when
        ReportCreateResponse response = reportCreateService.createReport(request);

        // then
        assertThat(response.getId()).isNotNull();
        assertThat(response.getCompanyId()).isEqualTo(101L);
        assertThat(response.getYear()).isEqualTo(2024);
        assertThat(response.getTitle()).isEqualTo("2024 SKT 지속가능경영보고서");
        assertThat(response.getStatus()).isEqualTo("DRAFT");
        assertThat(response.getTemplateId()).isEqualTo(1L);
        assertThat(response.getColorThemeId()).isEqualTo(1L);
    }
}
