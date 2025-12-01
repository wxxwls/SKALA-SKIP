package com.skala.skip.ai.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * 설문 응답 제출 AI 요청 DTO
 * POST /internal/v1/surveys/{survey_id}/responses
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SubmitSurveyResponseAiRequest {

    @NotEmpty
    @JsonProperty("responses")
    private Map<String, Integer> responses;

    @JsonProperty("respondent_id")
    private String respondentId;

    @JsonProperty("stakeholder_type")
    private String stakeholderType;
}
