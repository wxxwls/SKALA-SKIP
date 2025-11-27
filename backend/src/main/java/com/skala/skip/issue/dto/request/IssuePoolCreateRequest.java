package com.skala.skip.issue.dto.request;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * 이슈풀 생성 요청 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IssuePoolCreateRequest {

    @NotBlank(message = "회사명은 필수입니다")
    private String companyName;

    @NotBlank(message = "산업군은 필수입니다")
    private String industry;

    @NotNull(message = "연도는 필수입니다")
    @Min(value = 2020, message = "연도는 2020 이상이어야 합니다")
    @Max(value = 2030, message = "연도는 2030 이하여야 합니다")
    private Integer year;

    @Builder.Default
    private boolean useStandards = true;

    @Builder.Default
    private boolean useBenchmarks = true;

    @Builder.Default
    private boolean useInternal = true;

    @Builder.Default
    private boolean useNews = true;

    @Builder.Default
    @Min(value = 1, message = "최대 토픽 수는 1 이상이어야 합니다")
    @Max(value = 20, message = "최대 토픽 수는 20 이하여야 합니다")
    private int maxTopics = 20;
}
