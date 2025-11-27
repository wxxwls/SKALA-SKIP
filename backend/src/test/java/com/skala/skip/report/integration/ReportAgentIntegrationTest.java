package com.skala.skip.report.integration;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.skala.skip.report.client.ReportAgentClient;
import com.skala.skip.report.dto.request.ReportDraftRequest;
import com.skala.skip.report.dto.response.ReportDraftResponse;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;
import reactor.core.publisher.Mono;

import java.util.List;

import static org.hamcrest.Matchers.containsString;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class ReportAgentIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private ReportAgentClient reportAgentClient;

    @Test
    @DisplayName("통합 테스트 - 보고서 초안 생성 성공 (Controller → Service → Client)")
    @WithMockUser(username = "test@example.com", roles = "USER")
    void generateDraft_Integration_Success() throws Exception {
        // given
        Long reportId = 1L;
        String sectionCode = "E_CLIMATE";

        ReportDraftRequest request = ReportDraftRequest.builder()
                .maxTokens(1500)
                .tone("formal")
                .language("ko")
                .build();

        ReportDraftResponse mockResponse = ReportDraftResponse.builder()
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

        when(reportAgentClient.generateDraftReport(anyLong(), anyString(), any(ReportDraftRequest.class)))
                .thenReturn(Mono.just(mockResponse));

        // when & then
        mockMvc.perform(post("/api/v1/reports/{reportId}/sections/{sectionCode}/ai-draft", reportId, sectionCode)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.sectionCode").value(sectionCode))
                .andExpect(jsonPath("$.data.draftText").value(containsString("기후변화 리스크")))
                .andExpect(jsonPath("$.data.references[0].sourceType").value("ISSUE"))
                .andExpect(jsonPath("$.data.references[0].sourceId").value(1))
                .andExpect(jsonPath("$.data.references[0].title").value("기후변화 리스크 관리 강화"));
    }

    @Test
    @DisplayName("통합 테스트 - 보고서 초안 생성 실패 (FastAPI 빈 응답)")
    @WithMockUser(username = "test@example.com", roles = "USER")
    void generateDraft_Integration_Failure_EmptyResponse() throws Exception {
        // given
        Long reportId = 1L;
        String sectionCode = "E_CLIMATE";

        ReportDraftRequest request = ReportDraftRequest.builder()
                .maxTokens(1500)
                .tone("formal")
                .language("ko")
                .build();

        when(reportAgentClient.generateDraftReport(anyLong(), anyString(), any(ReportDraftRequest.class)))
                .thenReturn(Mono.empty());

        // when & then
        mockMvc.perform(post("/api/v1/reports/{reportId}/sections/{sectionCode}/ai-draft", reportId, sectionCode)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.success").value(false))
                .andExpect(jsonPath("$.error.code").exists())
                .andExpect(jsonPath("$.error.message").exists());
    }
}
