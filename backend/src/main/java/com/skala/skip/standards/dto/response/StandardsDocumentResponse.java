package com.skala.skip.standards.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * ESG 표준 문서 목록 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StandardsDocumentResponse {

    private List<DocumentInfo> documents;
    private int totalCount;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DocumentInfo {
        private String id;
        private String name;
        private String type;
        private long size;
        private String uploadedAt;
        private String status;
    }
}
