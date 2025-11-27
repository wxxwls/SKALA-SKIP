package com.skala.skip.report.service.impl;

import com.skala.skip.report.dto.request.ReportCreateRequest;
import com.skala.skip.report.dto.response.ReportCreateResponse;
import com.skala.skip.report.service.ReportCreateService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.concurrent.atomic.AtomicLong;

@Service
@Transactional(readOnly = true)
@Slf4j
public class ReportCreateServiceImpl implements ReportCreateService {

    private static final AtomicLong REPORT_ID_SEQUENCE = new AtomicLong(1L);

    @Override
    @Transactional
    public ReportCreateResponse createReport(ReportCreateRequest request) {
        log.info("보고서 생성 서비스 호출 - companyId: {}, year: {}, title: {}",
                request.getCompanyId(), request.getYear(), request.getTitle());

        return ReportCreateResponse.builder()
                .id(REPORT_ID_SEQUENCE.getAndIncrement())
                .companyId(request.getCompanyId())
                .year(request.getYear())
                .title(request.getTitle())
                .status("DRAFT")
                .templateId(request.getTemplateId())
                .colorThemeId(request.getColorThemeId())
                .build();
    }
}

