package com.skala.skip.issue.service;

import com.skala.skip.issue.dto.request.IssuePoolCreateRequest;
import com.skala.skip.issue.dto.request.ScoreTopicRequest;
import com.skala.skip.issue.dto.response.IssuePoolResponse;
import com.skala.skip.issue.dto.response.ScoreTopicResponse;

/**
 * 이슈풀 서비스 인터페이스
 */
public interface IssuePoolService {

    /**
     * ESG 이슈풀 생성
     */
    IssuePoolResponse generateIssuePool(String companyId, IssuePoolCreateRequest request);

    /**
     * 단일 토픽 이중중대성 점수화
     */
    ScoreTopicResponse scoreTopic(String companyId, ScoreTopicRequest request);
}
