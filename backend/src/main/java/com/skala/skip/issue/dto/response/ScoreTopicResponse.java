package com.skala.skip.issue.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * 토픽 점수화 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScoreTopicResponse {

    private String topicTitle;
    private double financialScore;
    private double impactScore;
    private String financialRationale;
    private String impactRationale;
    private List<IssuePoolResponse.SourceResponse> sources;
}
