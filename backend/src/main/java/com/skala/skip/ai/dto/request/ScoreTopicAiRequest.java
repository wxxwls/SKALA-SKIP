package com.skala.skip.ai.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.skala.skip.ai.dto.common.CompanyContext;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * 단일 토픽 이중중대성 점수화 AI 요청 DTO
 * POST /internal/v1/issue-pools/score-topic
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScoreTopicAiRequest {

    @NotNull
    @JsonProperty("company_context")
    private CompanyContext companyContext;

    @NotBlank
    @JsonProperty("topic_title")
    private String topicTitle;

    @JsonProperty("topic_description")
    private String topicDescription;
}
