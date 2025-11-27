package com.skala.skip.report.controller;

import com.skala.skip.auth.security.JwtAuthenticationFilter;
import com.skala.skip.auth.util.JwtTokenProvider;
import com.skala.skip.config.TestSecurityConfig;
import com.skala.skip.report.dto.response.ReportExportResponse;
import com.skala.skip.report.service.ReportExportService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.FilterType;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(
        controllers = ReportExportController.class,
        excludeFilters = @ComponentScan.Filter(
                type = FilterType.ASSIGNABLE_TYPE,
                classes = {JwtAuthenticationFilter.class}
        )
)
@Import(TestSecurityConfig.class)
class ReportExportControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ReportExportService reportExportService;

    @MockBean
    private JwtTokenProvider jwtTokenProvider;

    @Test
    @DisplayName("GET /api/v1/reports/{reportId}/export - 보고서 다운로드 성공")
    void exportReport_Success() throws Exception {
        // given
        Long reportId = 1L;
        String fileName = "2024_지속가능경영보고서.pdf";
        String contentType = "application/pdf";
        byte[] fileContent = "테스트용 PDF 파일 내용".getBytes();

        ReportExportResponse response = ReportExportResponse.builder()
                .fileName(fileName)
                .contentType(contentType)
                .fileContent(fileContent)
                .build();

        when(reportExportService.exportReport(anyLong()))
                .thenReturn(response);

        // when & then
        mockMvc.perform(get("/api/v1/reports/{reportId}/export", reportId))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_PDF))
                .andExpect(header().exists(HttpHeaders.CONTENT_DISPOSITION))
                .andExpect(header().string(HttpHeaders.CONTENT_DISPOSITION,
                        org.hamcrest.Matchers.containsString("attachment")));
    }
}
