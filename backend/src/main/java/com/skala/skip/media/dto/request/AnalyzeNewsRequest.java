package com.skala.skip.media.dto.request;

import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * 뉴스 분석 요청 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AnalyzeNewsRequest {

    @NotEmpty(message = "키워드 목록은 필수입니다")
    private List<String> keywords;

    @Builder.Default
    private int maxPages = 3;
}
