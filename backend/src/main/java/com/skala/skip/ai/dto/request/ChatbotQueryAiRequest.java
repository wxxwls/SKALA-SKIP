package com.skala.skip.ai.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * ESG 챗봇 질의 AI 요청 DTO
 * POST /internal/v1/chatbot/query
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatbotQueryAiRequest {

    @NotBlank
    @JsonProperty("query")
    private String query;

    @JsonProperty("company_id")
    private String companyId;

    @JsonProperty("year")
    private Integer year;

    @JsonProperty("session_id")
    private String sessionId;
}
