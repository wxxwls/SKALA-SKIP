package com.skala.skip.report.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.skala.skip.report.dto.request.ReportCreateRequest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class ReportCreateIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("통합 테스트 - 보고서 생성 성공 (Controller → Service)")
    @WithMockUser(username = "test@example.com", roles = "USER")
    void createReport_Integration_Success() throws Exception {
        // given
        ReportCreateRequest request = ReportCreateRequest.builder()
                .companyId(101L)
                .year(2024)
                .issuePoolId(555L)
                .title("2024 SKT 지속가능경영보고서")
                .templateId(1L)
                .colorThemeId(1L)
                .build();

        // when & then
        mockMvc.perform(post("/api/v1/reports")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.id").exists())
                .andExpect(jsonPath("$.data.companyId").value(101))
                .andExpect(jsonPath("$.data.year").value(2024))
                .andExpect(jsonPath("$.data.title").value(containsString("SKT 지속가능경영보고서")))
                .andExpect(jsonPath("$.data.status").value("DRAFT"))
                .andExpect(jsonPath("$.data.templateId").value(1))
                .andExpect(jsonPath("$.data.colorThemeId").value(1));
    }
}
