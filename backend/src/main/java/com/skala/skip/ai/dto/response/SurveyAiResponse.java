package com.skala.skip.ai.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 이해관계자 설문 생성 AI 응답 DTO
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SurveyAiResponse {

    @JsonProperty("success")
    private boolean success;

    @JsonProperty("survey_id")
    private String surveyId;

    @JsonProperty("questions")
    private List<SurveyQuestion> questions;

    @JsonProperty("total_questions")
    private int totalQuestions;

    /**
     * 설문 질문 아이템
     */
    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SurveyQuestion {

        @JsonProperty("id")
        private String id;

        @JsonProperty("issue_id")
        private String issueId;

        @JsonProperty("issue_name")
        private String issueName;

        @JsonProperty("question_text")
        private String questionText;

        @JsonProperty("question_type")
        private String questionType;
    }
}
