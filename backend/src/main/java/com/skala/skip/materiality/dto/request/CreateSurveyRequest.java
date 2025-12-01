package com.skala.skip.materiality.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * 이해관계자 설문 생성 요청 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateSurveyRequest {

    @NotNull(message = "연도는 필수입니다")
    private Integer year;

    @NotEmpty(message = "이슈 목록은 필수입니다")
    private List<String> issues;

    @NotBlank(message = "이해관계자 유형은 필수입니다")
    private String stakeholderType;
}
