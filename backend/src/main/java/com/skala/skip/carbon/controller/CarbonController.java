package com.skala.skip.carbon.controller;

import com.skala.skip.carbon.dto.response.CarbonSignalsResponse;
import com.skala.skip.carbon.service.CarbonService;
import com.skala.skip.common.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 탄소 거래 컨트롤러
 * 탄소 거래 시그널 API
 */
@RestController
@RequestMapping("/api/v1/carbon")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Carbon", description = "탄소 거래 시그널 API")
public class CarbonController {

    private final CarbonService carbonService;

    @GetMapping("/signals")
    @Operation(summary = "거래 시그널 조회", description = "탄소 거래 시그널(BUY/SELL/HOLD)을 조회합니다")
    public ResponseEntity<ApiResponse<CarbonSignalsResponse>> getSignals() {
        log.info("GET /api/v1/carbon/signals");

        CarbonSignalsResponse response = carbonService.getSignals();
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
