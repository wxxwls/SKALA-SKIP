package com.skala.skip.chatbot.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * ESG 챗봇 질의 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatbotQueryResponse {

    private boolean success;
    private String answer;
    private List<DocumentSource> sources;
    private List<String> usedCollections;
    private double confidence;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DocumentSource {
        private String documentId;
        private String documentTitle;
        private Integer page;
        private double relevanceScore;
    }
}
