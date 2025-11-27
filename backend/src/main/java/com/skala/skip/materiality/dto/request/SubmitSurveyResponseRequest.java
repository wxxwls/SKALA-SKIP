package com.skala.skip.materiality.dto.request;

import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.Map;

/**
 * 설문 응답 제출 요청 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SubmitSurveyResponseRequest {

    @NotEmpty(message = "응답은 필수입니다")
    private Map<String, Integer> responses;

    private String respondentId;

    private String stakeholderType;
}
