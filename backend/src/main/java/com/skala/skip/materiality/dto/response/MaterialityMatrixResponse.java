package com.skala.skip.materiality.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * 중대성 매트릭스 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MaterialityMatrixResponse {

    private boolean success;
    private String companyId;
    private int year;
    private List<MaterialityItem> matrix;
    private int totalIssues;
    private int highPriorityCount;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MaterialityItem {
        private String issueId;
        private String issueName;
        private String category;
        private double financialScore;
        private double impactScore;
        private String quadrant;
        private double stakeholderImportance;
        private double businessImportance;
    }
}
