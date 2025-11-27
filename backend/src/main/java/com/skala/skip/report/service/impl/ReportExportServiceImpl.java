package com.skala.skip.report.service.impl;

import com.skala.skip.report.dto.response.ReportExportResponse;
import com.skala.skip.report.service.ReportExportService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class ReportExportServiceImpl implements ReportExportService {

    @Override
    public ReportExportResponse exportReport(Long reportId) {
        log.info("보고서 다운로드 요청 수신 - reportId: {}", reportId);

        // TODO: Spring Boot에서 직접 보고서 파일 생성/다운로드 처리
        // - DB에서 보고서 데이터 조회
        // - 파일 생성 (PDF, Excel 등) - Apache POI 사용
        // - S3에서 파일 조회 또는 직접 생성
        // - ReportExportResponse 반환

        // 임시 구현: 실제 로직은 추후 구현 필요
        // 빈 PDF 파일 대신 최소한의 더미 데이터 반환
        byte[] dummyContent = "PDF 파일 내용 (실제 구현 필요)".getBytes();

        return ReportExportResponse.builder()
                .fileName(String.format("report-%d.pdf", reportId))
                .contentType("application/pdf")
                .fileContent(dummyContent)
                .build();
    }
}

