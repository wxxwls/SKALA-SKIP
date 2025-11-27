package com.skala.skip.report.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.skala.skip.auth.security.JwtAuthenticationFilter;
import com.skala.skip.auth.util.JwtTokenProvider;
import com.skala.skip.config.TestSecurityConfig;
import com.skala.skip.report.dto.request.ReportDraftRequest;
import com.skala.skip.report.dto.response.ReportDraftResponse;
import com.skala.skip.report.service.ReportAgentService;
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

import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(
        controllers = ReportAgentController.class,
        excludeFilters = @ComponentScan.Filter(
                type = FilterType.ASSIGNABLE_TYPE,
                classes = {JwtAuthenticationFilter.class}
        )
)
@Import(TestSecurityConfig.class)
class ReportAgentControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private ReportAgentService reportAgentService;

    @MockBean
    private JwtTokenProvider jwtTokenProvider;

    @Test
    @DisplayName("POST /api/v1/reports/{reportId}/sections/{sectionCode}/ai-draft - 보고서 초안 생성 성공")
    void generateDraft_Success() throws Exception {
        // given
        Long reportId = 1L;
        String sectionCode = "E_CLIMATE";

        ReportDraftRequest request = ReportDraftRequest.builder()
                .maxTokens(1500)
                .tone("formal")
                .language("ko")
                .build();

        ReportDraftResponse response = ReportDraftResponse.builder()
                .sectionCode(sectionCode)
                .draftText("우리 회사는 기후변화 리스크에 대응하기 위해...")
                .references(List.of(
                        ReportDraftResponse.Reference.builder()
                                .sourceType("ISSUE")
                                .sourceId(1L)
                                .title("기후변화 리스크 관리 강화")
                                .build()
                ))
                .build();

        when(reportAgentService.generateDraft(anyLong(), anyString(), any(ReportDraftRequest.class)))
                .thenReturn(response);

        // when & then
        mockMvc.perform(post("/api/v1/reports/{reportId}/sections/{sectionCode}/ai-draft", reportId, sectionCode)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.sectionCode").value(sectionCode))
                .andExpect(jsonPath("$.data.draftText").value("우리 회사는 기후변화 리스크에 대응하기 위해..."))
                .andExpect(jsonPath("$.data.references[0].sourceType").value("ISSUE"))
                .andExpect(jsonPath("$.data.references[0].sourceId").value(1))
                .andExpect(jsonPath("$.data.references[0].title").value("기후변화 리스크 관리 강화"));
    }
}
