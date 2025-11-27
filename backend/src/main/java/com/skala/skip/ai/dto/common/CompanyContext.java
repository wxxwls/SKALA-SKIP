package com.skala.skip.ai.dto.common;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * 회사 컨텍스트 정보
 * AI 서비스 요청 시 회사 정보를 전달하는 공통 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CompanyContext {

    @JsonProperty("company_id")
    private String companyId;

    @JsonProperty("company_name")
    private String companyName;

    @JsonProperty("industry")
    private String industry;

    @JsonProperty("year")
    private int year;
}
