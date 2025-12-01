package com.skala.skip.chatbot.service;

import com.skala.skip.chatbot.dto.request.ChatbotQueryRequest;
import com.skala.skip.chatbot.dto.response.ChatbotQueryResponse;

/**
 * ESG 챗봇 서비스 인터페이스
 */
public interface ChatbotService {

    /**
     * ESG 질의응답
     */
    ChatbotQueryResponse query(String companyId, ChatbotQueryRequest request);
}
