package com.skala.skip.standards.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * 이슈별 공시 요건 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IssueDisclosuresResponse {

    private String issueName;
    private List<DisclosureRequirement> disclosures;
    private int totalCount;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DisclosureRequirement {
        private String standard;
        private String code;
        private String title;
        private String description;
        private List<String> metrics;
    }
}
