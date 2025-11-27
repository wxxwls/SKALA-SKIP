package com.skala.skip.report.service;

import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import com.skala.skip.report.client.ReportAgentClient;
import com.skala.skip.report.dto.request.ReportDraftRequest;
import com.skala.skip.report.dto.response.ReportDraftResponse;
import com.skala.skip.report.exception.ReportAgentException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import com.skala.skip.report.service.impl.ReportAgentServiceImpl;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import reactor.core.publisher.Mono;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ReportAgentServiceTest {

    @Mock
    private ReportAgentClient reportAgentClient;

    private ReportAgentService reportAgentService;

    @BeforeEach
    void setUp() {
        reportAgentService = new ReportAgentServiceImpl(reportAgentClient);
    }

    @Test
    @DisplayName("보고서 초안 생성 성공 - 정상 응답 반환")
    void generateDraft_Success() {
        // given
        Long reportId = 1L;
        String sectionCode = "E_CLIMATE";

        ReportDraftRequest request = ReportDraftRequest.builder()
                .maxTokens(1500)
                .tone("formal")
                .language("ko")
                .build();

        ReportDraftResponse expectedResponse = ReportDraftResponse.builder()
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
                .thenReturn(Mono.just(expectedResponse));

        // when
        ReportDraftResponse response = reportAgentService.generateDraft(reportId, sectionCode, request);

        // then
        assertThat(response.getSectionCode()).isEqualTo(sectionCode);
        assertThat(response.getDraftText()).contains("기후변화 리스크");
        assertThat(response.getReferences()).hasSize(1);
        assertThat(response.getReferences().get(0).getSourceType()).isEqualTo("ISSUE");
        assertThat(response.getReferences().get(0).getSourceId()).isEqualTo(1L);
        assertThat(response.getReferences().get(0).getTitle()).isEqualTo("기후변화 리스크 관리 강화");
    }

    @Test
    @DisplayName("보고서 초안 생성 실패 - FastAPI로부터 빈 응답 반환")
    void generateDraft_Failure_EmptyResponse() {
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
        assertThatThrownBy(() -> reportAgentService.generateDraft(reportId, sectionCode, request))
                .isInstanceOf(BusinessException.class)
                .satisfies(throwable -> {
                    BusinessException businessException = (BusinessException) throwable;
                    assertThat(businessException.getErrorCode()).isEqualTo(ESGErrorCode.RPT_AI_001);
                    assertThat(businessException.getDetails()).isEqualTo("FastAPI로부터 응답을 받지 못했습니다.");
                });
    }

    @Test
    @DisplayName("보고서 초안 생성 실패 - ReportAgentException 발생")
    void generateDraft_Failure_ReportAgentException() {
        // given
        Long reportId = 1L;
        String sectionCode = "E_CLIMATE";

        ReportDraftRequest request = ReportDraftRequest.builder()
                .maxTokens(1500)
                .tone("formal")
                .language("ko")
                .build();

        ReportAgentException reportAgentException = new ReportAgentException(
                ESGErrorCode.RPT_CLIENT_001,
                "FastAPI 서버 오류: 500 Internal Server Error"
        );

        when(reportAgentClient.generateDraftReport(anyLong(), anyString(), any(ReportDraftRequest.class)))
                .thenReturn(Mono.error(reportAgentException));

        // when & then
        assertThatThrownBy(() -> reportAgentService.generateDraft(reportId, sectionCode, request))
                .isInstanceOf(ReportAgentException.class)
                .satisfies(throwable -> {
                    ReportAgentException exception = (ReportAgentException) throwable;
                    assertThat(exception.getErrorCode()).isEqualTo(ESGErrorCode.RPT_CLIENT_001);
                    assertThat(exception.getResponseBody()).isEqualTo("FastAPI 서버 오류: 500 Internal Server Error");
                });
    }

    @Test
    @DisplayName("보고서 초안 생성 실패 - 일반 Exception 발생 시 BusinessException으로 변환")
    void generateDraft_Failure_GenericException() {
        // given
        Long reportId = 1L;
        String sectionCode = "E_CLIMATE";

        ReportDraftRequest request = ReportDraftRequest.builder()
                .maxTokens(1500)
                .tone("formal")
                .language("ko")
                .build();

        RuntimeException runtimeException = new RuntimeException("네트워크 연결 실패");

        when(reportAgentClient.generateDraftReport(anyLong(), anyString(), any(ReportDraftRequest.class)))
                .thenReturn(Mono.error(runtimeException));

        // when & then
        assertThatThrownBy(() -> reportAgentService.generateDraft(reportId, sectionCode, request))
                .isInstanceOf(BusinessException.class)
                .satisfies(throwable -> {
                    BusinessException businessException = (BusinessException) throwable;
                    assertThat(businessException.getErrorCode()).isEqualTo(ESGErrorCode.RPT_AI_001);
                    assertThat(businessException.getDetails()).contains("보고서 초안 생성 중 오류 발생");
                    assertThat(businessException.getDetails()).contains("네트워크 연결 실패");
                    assertThat(businessException.getCause()).isEqualTo(runtimeException);
                });
    }
}
