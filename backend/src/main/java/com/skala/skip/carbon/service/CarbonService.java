package com.skala.skip.carbon.service;

import com.skala.skip.carbon.dto.response.CarbonSignalsResponse;

/**
 * 탄소 거래 서비스 인터페이스
 */
public interface CarbonService {

    /**
     * 탄소 거래 시그널 조회 (BUY/SELL/HOLD)
     */
    CarbonSignalsResponse getSignals();
}
