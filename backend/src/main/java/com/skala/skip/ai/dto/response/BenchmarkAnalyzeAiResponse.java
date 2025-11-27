package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * 벤치마킹 분석 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BenchmarkAnalyzeAiResponse {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("keyword")
    private String keyword;

    @JsonProperty("results")
    private Map<String, CompanyResult> results;

    @JsonProperty("summary")
    private Summary summary;

    /**
     * 회사별 분석 결과
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CompanyResult {

        @JsonProperty("coverage")
        private String coverage;

        @JsonProperty("response")
        private String response;

        @JsonProperty("source_pages")
        private List<Integer> sourcePages;
    }

    /**
     * 분석 요약 정보
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Summary {

        @JsonProperty("full_coverage")
        private int fullCoverage;

        @JsonProperty("partial_coverage")
        private int partialCoverage;

        @JsonProperty("no_coverage")
        private int noCoverage;
    }
}
