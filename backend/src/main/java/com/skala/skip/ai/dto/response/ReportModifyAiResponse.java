package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * 보고서 수정 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportModifyAiResponse {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("modified_report")
    private String modifiedReport;

    @JsonProperty("changes_summary")
    private String changesSummary;

    @JsonProperty("message")
    private String message;
}
