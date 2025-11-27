package com.skala.skip.report.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportCreateResponse {

    private Long id;
    private Long companyId;
    private Integer year;
    private String title;
    private String status;
    private Long templateId;
    private Long colorThemeId;
}

