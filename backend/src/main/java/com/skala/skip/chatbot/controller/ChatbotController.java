package com.skala.skip.chatbot.controller;

import com.skala.skip.chatbot.dto.request.ChatbotQueryRequest;
import com.skala.skip.chatbot.dto.response.ChatbotQueryResponse;
import com.skala.skip.chatbot.service.ChatbotService;
import com.skala.skip.common.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * ESG 챗봇 컨트롤러
 * RAG 기반 ESG 질의응답 API
 */
@RestController
@RequestMapping("/api/v1/chatbot")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Chatbot", description = "ESG 챗봇 API")
public class ChatbotController {

    private final ChatbotService chatbotService;

    @PostMapping("/{companyId}/query")
    @Operation(summary = "ESG 질의응답", description = "RAG 기반으로 ESG 관련 질문에 답변합니다")
    public ResponseEntity<ApiResponse<ChatbotQueryResponse>> query(
            @Parameter(description = "회사 ID") @PathVariable String companyId,
            @Valid @RequestBody ChatbotQueryRequest request
    ) {
        log.info("POST /api/v1/chatbot/{}/query - query: {}", companyId, request.getQuery());

        ChatbotQueryResponse response = chatbotService.query(companyId, request);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
