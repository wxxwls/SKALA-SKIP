package com.skala.skip.benchmark.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;
import java.util.Map;

/**
 * 벤치마킹 분석 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BenchmarkAnalyzeResponse {

    private boolean success;
    private String keyword;
    private Map<String, CompanyResult> results;
    private Summary summary;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CompanyResult {
        private String coverage;
        private String response;
        private List<Integer> sourcePages;
    }

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Summary {
        private int fullCoverage;
        private int partialCoverage;
        private int noCoverage;
    }
}
