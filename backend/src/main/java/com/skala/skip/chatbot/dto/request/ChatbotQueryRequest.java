package com.skala.skip.chatbot.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * ESG 챗봇 질의 요청 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatbotQueryRequest {

    @NotBlank(message = "질의 내용은 필수입니다")
    private String query;

    private Integer year;

    private String sessionId;
}
