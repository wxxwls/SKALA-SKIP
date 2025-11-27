package com.skala.skip.ai.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 벤치마킹 분석 AI 요청 DTO
 * POST /internal/v1/benchmarks/analyze
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BenchmarkAnalyzeAiRequest {

    @NotBlank
    @JsonProperty("keyword")
    private String keyword;

    @NotEmpty
    @JsonProperty("companies")
    private List<CompanyInfo> companies;

    /**
     * 분석 대상 회사 정보
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CompanyInfo {

        @JsonProperty("name")
        private String name;

        @JsonProperty("path")
        private String path;
    }
}
