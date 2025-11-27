package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 단일 토픽 이중중대성 점수화 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScoreTopicAiResponse {

    @JsonProperty("topic_title")
    private String topicTitle;

    @JsonProperty("financial_score")
    private double financialScore;

    @JsonProperty("impact_score")
    private double impactScore;

    @JsonProperty("financial_rationale")
    private String financialRationale;

    @JsonProperty("impact_rationale")
    private String impactRationale;

    @JsonProperty("sources")
    private List<IssuePoolAiResponse.SourceAttribution> sources;
}
