package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * ESG 표준 문서 목록 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StandardsDocumentAiResponse {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("documents")
    private List<DocumentInfo> documents;

    @JsonProperty("total_count")
    private int totalCount;

    /**
     * 문서 정보
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DocumentInfo {

        @JsonProperty("id")
        private String id;

        @JsonProperty("name")
        private String name;

        @JsonProperty("type")
        private String type;

        @JsonProperty("size")
        private long size;

        @JsonProperty("uploadedAt")
        private String uploadedAt;

        @JsonProperty("status")
        private String status;
    }
}
