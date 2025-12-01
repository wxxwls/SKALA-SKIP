package com.skala.skip.benchmark.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * 벤치마킹 분석 요청 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BenchmarkAnalyzeRequest {

    @NotBlank(message = "키워드는 필수입니다")
    private String keyword;

    @NotEmpty(message = "회사 정보 목록은 필수입니다")
    private List<CompanyInfo> companies;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CompanyInfo {
        private String name;
        private String path;
    }
}
