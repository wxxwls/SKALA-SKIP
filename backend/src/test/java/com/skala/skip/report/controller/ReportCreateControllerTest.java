package com.skala.skip.report.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.skala.skip.auth.security.JwtAuthenticationFilter;
import com.skala.skip.auth.util.JwtTokenProvider;
import com.skala.skip.config.TestSecurityConfig;
import com.skala.skip.report.dto.request.ReportCreateRequest;
import com.skala.skip.report.dto.response.ReportCreateResponse;
import com.skala.skip.report.service.ReportCreateService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.FilterType;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(
        controllers = ReportCreateController.class,
        excludeFilters = @ComponentScan.Filter(
                type = FilterType.ASSIGNABLE_TYPE,
                classes = {JwtAuthenticationFilter.class}
        )
)
@Import(TestSecurityConfig.class)
class ReportCreateControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private ReportCreateService reportCreateService;

    @MockBean
    private JwtTokenProvider jwtTokenProvider;

    @Test
    @DisplayName("POST /api/v1/reports - 보고서 생성 성공")
    void createReport_Success() throws Exception {
        // given
        ReportCreateRequest request = ReportCreateRequest.builder()
                .companyId(101L)
                .year(2024)
                .issuePoolId(555L)
                .title("2024 SKT 지속가능경영보고서")
                .templateId(1L)
                .colorThemeId(1L)
                .build();

        ReportCreateResponse response = ReportCreateResponse.builder()
                .id(7001L)
                .companyId(101L)
                .year(2024)
                .title("2024 SKT 지속가능경영보고서")
                .status("DRAFT")
                .templateId(1L)
                .colorThemeId(1L)
                .build();

        when(reportCreateService.createReport(any(ReportCreateRequest.class)))
                .thenReturn(response);

        // when & then
        mockMvc.perform(post("/api/v1/reports")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").value(7001))
                .andExpect(jsonPath("$.data.companyId").value(101))
                .andExpect(jsonPath("$.data.year").value(2024))
                .andExpect(jsonPath("$.data.title").value("2024 SKT 지속가능경영보고서"))
                .andExpect(jsonPath("$.data.status").value("DRAFT"))
                .andExpect(jsonPath("$.data.templateId").value(1))
                .andExpect(jsonPath("$.data.colorThemeId").value(1));
    }
}
