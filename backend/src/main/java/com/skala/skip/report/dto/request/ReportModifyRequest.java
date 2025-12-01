package com.skala.skip.report.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * 보고서 수정 요청 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportModifyRequest {

    @NotBlank(message = "현재 보고서 내용은 필수입니다")
    private String currentReport;

    @NotBlank(message = "수정 지시사항은 필수입니다")
    private String instruction;
}
