package com.skala.skip.report.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * 보고서 수정 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportModifyResponse {

    private boolean success;
    private String modifiedReport;
    private String changesSummary;
    private String message;
}
