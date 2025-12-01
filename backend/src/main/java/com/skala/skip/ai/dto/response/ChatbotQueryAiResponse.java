package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * ESG 챗봇 질의 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatbotQueryAiResponse {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("answer")
    private String answer;

    @JsonProperty("sources")
    private List<DocumentSource> sources;

    @JsonProperty("used_collections")
    private List<String> usedCollections;

    @JsonProperty("confidence")
    private double confidence;

    /**
     * 문서 출처 정보
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DocumentSource {

        @JsonProperty("document_id")
        private String documentId;

        @JsonProperty("document_title")
        private String documentTitle;

        @JsonProperty("page")
        private Integer page;

        @JsonProperty("relevance_score")
        private double relevanceScore;
    }
}
