package com.skala.skip.report.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportDraftResponse {
    private String sectionCode;
    private String draftText;
    private List<Reference> references;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Reference {
        private String sourceType;
        private Long sourceId;
        private String title;
    }
}

