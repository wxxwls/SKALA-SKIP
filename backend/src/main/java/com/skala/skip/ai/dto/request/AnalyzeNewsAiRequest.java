package com.skala.skip.ai.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 뉴스 분석 AI 요청 DTO
 * POST /internal/v1/media/analyze
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AnalyzeNewsAiRequest {

    @NotEmpty
    @JsonProperty("keywords")
    private List<String> keywords;

    @Builder.Default
    @JsonProperty("max_pages")
    private int maxPages = 3;
}
