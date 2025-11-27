package com.skala.skip.report.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportCreateRequest {

    @NotNull(message = "companyId는 필수입니다.")
    private Long companyId;

    @NotNull(message = "year는 필수입니다.")
    private Integer year;

    @NotNull(message = "issuePoolId는 필수입니다.")
    private Long issuePoolId;

    @NotBlank(message = "title은 필수입니다.")
    private String title;

    @NotNull(message = "templateId는 필수입니다.")
    private Long templateId;

    @NotNull(message = "colorThemeId는 필수입니다.")
    private Long colorThemeId;
}

