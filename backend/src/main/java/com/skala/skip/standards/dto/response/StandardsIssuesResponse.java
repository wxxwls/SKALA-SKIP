package com.skala.skip.standards.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * ESG 표준 이슈 목록 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StandardsIssuesResponse {

    private List<StandardIssue> issues;
    private int totalCount;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class StandardIssue {
        private String id;
        private String name;
        private String category;
        private String description;
    }
}
