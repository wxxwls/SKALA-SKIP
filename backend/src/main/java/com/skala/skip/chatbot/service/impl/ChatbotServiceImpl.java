package com.skala.skip.chatbot.service.impl;

import com.skala.skip.ai.client.ChatbotAiClient;
import com.skala.skip.ai.dto.common.AiApiResponse;
import com.skala.skip.ai.dto.request.ChatbotQueryAiRequest;
import com.skala.skip.ai.dto.response.ChatbotQueryAiResponse;
import com.skala.skip.ai.exception.AiServiceException;
import com.skala.skip.chatbot.dto.request.ChatbotQueryRequest;
import com.skala.skip.chatbot.dto.response.ChatbotQueryResponse;
import com.skala.skip.chatbot.service.ChatbotService;
import com.skala.skip.common.exception.BusinessException;
import com.skala.skip.common.exception.ESGErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.stream.Collectors;

/**
 * ESG 챗봇 서비스 구현
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class ChatbotServiceImpl implements ChatbotService {

    private final ChatbotAiClient chatbotAiClient;

    @Override
    public ChatbotQueryResponse query(String companyId, ChatbotQueryRequest request) {
        log.info("챗봇 질의 - companyId: {}, query: {}", companyId, request.getQuery());

        ChatbotQueryAiRequest aiRequest = ChatbotQueryAiRequest.builder()
                .query(request.getQuery())
                .companyId(companyId)
                .year(request.getYear())
                .sessionId(request.getSessionId())
                .build();

        try {
            AiApiResponse<ChatbotQueryAiResponse> response = chatbotAiClient.query(aiRequest).block();

            if (response == null) {
                throw new BusinessException(ESGErrorCode.CHAT_AI_001, "AI 서비스로부터 응답을 받지 못했습니다.");
            }

            if (response.hasError()) {
                throw new AiServiceException(ESGErrorCode.CHAT_AI_001, response.getError().getMessage());
            }

            if (!response.hasData()) {
                throw new BusinessException(ESGErrorCode.CHAT_AI_001, "AI 서비스로부터 데이터를 받지 못했습니다.");
            }

            ChatbotQueryResponse result = mapToResponse(response.getData());
            log.info("챗봇 응답 완료 - confidence: {}", result.getConfidence());
            return result;

        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            log.error("챗봇 서비스 오류", e);
            throw new BusinessException(ESGErrorCode.CHAT_AI_001, "챗봇 처리 중 오류 발생: " + e.getMessage(), e);
        }
    }

    private ChatbotQueryResponse mapToResponse(ChatbotQueryAiResponse data) {
        return ChatbotQueryResponse.builder()
                .success(data.isSuccess())
                .answer(data.getAnswer())
                .usedCollections(data.getUsedCollections())
                .confidence(data.getConfidence())
                .sources(data.getSources() != null ? data.getSources().stream()
                        .map(s -> ChatbotQueryResponse.DocumentSource.builder()
                                .documentId(s.getDocumentId())
                                .documentTitle(s.getDocumentTitle())
                                .page(s.getPage())
                                .relevanceScore(s.getRelevanceScore())
                                .build())
                        .collect(Collectors.toList()) : Collections.emptyList())
                .build();
    }
}
