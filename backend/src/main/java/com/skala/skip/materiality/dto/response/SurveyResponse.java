package com.skala.skip.materiality.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

/**
 * 설문 생성 응답 DTO
 */
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SurveyResponse {

    private boolean success;
    private String surveyId;
    private List<SurveyQuestion> questions;
    private int totalQuestions;

    @Getter
    @Setter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SurveyQuestion {
        private String id;
        private String issueId;
        private String issueName;
        private String questionText;
        private String questionType;
    }
}
