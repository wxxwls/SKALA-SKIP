package com.skala.skip.ai.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 이해관계자 설문 생성 AI 요청 DTO
 * POST /internal/v1/surveys
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateSurveyAiRequest {

    @NotBlank
    @JsonProperty("company_id")
    private String companyId;

    @NotNull
    @JsonProperty("year")
    private int year;

    @NotEmpty
    @JsonProperty("issues")
    private List<String> issues;

    @NotBlank
    @JsonProperty("stakeholder_type")
    private String stakeholderType;
}
