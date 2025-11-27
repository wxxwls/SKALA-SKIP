package com.skala.skip.benchmark.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * 벤치마킹 문서 목록 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BenchmarkDocumentResponse {

    private boolean success;
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
        private long size;
        private String uploadedAt;
        private String status;
    }
}
