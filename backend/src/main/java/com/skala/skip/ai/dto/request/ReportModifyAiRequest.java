package com.skala.skip.ai.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * 보고서 수정 AI 요청 DTO (자연어 명령)
 * POST /internal/v1/reports/modify
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportModifyAiRequest {

    @NotBlank
    @JsonProperty("company_name")
    private String companyName;

    @NotBlank
    @JsonProperty("current_report")
    private String currentReport;

    @NotBlank
    @JsonProperty("instruction")
    private String instruction;
}
