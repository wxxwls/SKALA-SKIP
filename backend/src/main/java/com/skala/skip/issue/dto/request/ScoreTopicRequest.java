package com.skala.skip.issue.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * 토픽 점수화 요청 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ScoreTopicRequest {

    @NotBlank(message = "회사명은 필수입니다")
    private String companyName;

    @NotBlank(message = "산업군은 필수입니다")
    private String industry;

    @NotNull(message = "연도는 필수입니다")
    private Integer year;

    @NotBlank(message = "토픽 제목은 필수입니다")
    private String topicTitle;

    private String topicDescription;
}
