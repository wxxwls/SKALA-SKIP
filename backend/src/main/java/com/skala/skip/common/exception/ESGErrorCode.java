package com.skala.skip.common.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum ESGErrorCode {
    // ===== 이슈풀 (ISS) =====
    ISS_AI_001("ESG-ISS-AI-001", "이슈풀 생성 실패"),
    ISS_AI_002("ESG-ISS-AI-002", "토픽 점수화 실패"),
    ISS_LIMIT_001("ESG-ISS-LIMIT-001", "이슈풀 토픽 수 제한 초과 (최대 20개)"),
    ISS_VAL_001("ESG-ISS-VAL-001", "이슈풀 검증 실패"),

    // ===== 중대성 평가 (MAT) =====
    MAT_AI_001("ESG-MAT-AI-001", "중대성 평가 실패"),
    MAT_LIMIT_001("ESG-MAT-LIMIT-001", "토픽 수 제한 초과"),
    MAT_VAL_001("ESG-MAT-VAL-001", "중대성 평가 검증 실패"),

    // ===== 이해관계자 설문 (SVY) =====
    SVY_AI_001("ESG-SVY-AI-001", "설문 생성 실패"),
    SVY_VAL_001("ESG-SVY-VAL-001", "정확히 5개의 이슈를 선택해야 합니다"),
    SVY_VAL_002("ESG-SVY-VAL-002", "점수는 1-3 범위여야 합니다"),

    // ===== 보고서 작성 (RPT) =====
    RPT_AI_001("ESG-RPT-AI-001", "AI 초안 생성 실패"),
    RPT_AI_002("ESG-RPT-AI-002", "보고서 수정 실패"),
    RPT_VAL_001("ESG-RPT-VAL-001", "보고서 포맷 검증 실패"),
    RPT_CLIENT_001("ESG-RPT-CLIENT-001", "FastAPI 클라이언트 호출 실패"),
    RPT_CLIENT_002("ESG-RPT-CLIENT-002", "FastAPI 응답 파싱 실패"),
    RPT_EXPORT_001("ESG-RPT-EXPORT-001", "보고서 다운로드 실패"),
    RPT_EXPORT_002("ESG-RPT-EXPORT-002", "보고서 파일 응답이 비어 있습니다"),
    RPT_CREATE_001("ESG-RPT-CREATE-001", "보고서 생성 요청 실패"),
    RPT_CREATE_002("ESG-RPT-CREATE-002", "보고서 생성 응답이 비어 있습니다"),

    // ===== ESG 챗봇 (CHAT) =====
    CHAT_AI_001("ESG-CHAT-AI-001", "챗봇 질의 실패"),
    CHAT_VAL_001("ESG-CHAT-VAL-001", "질의 검증 실패"),

    // ===== 벤치마킹 (BMK) =====
    BMK_AI_001("ESG-BMK-AI-001", "벤치마킹 분석 실패"),
    BMK_AI_002("ESG-BMK-AI-002", "벤치마킹 파일 미발견"),
    BMK_AI_003("ESG-BMK-AI-003", "벤치마킹 파일 삭제 실패"),
    BMK_AI_004("ESG-BMK-AI-004", "캐시 초기화 실패"),

    // ===== 미디어/뉴스 분석 (MED) =====
    MED_AI_001("ESG-MED-AI-001", "미디어 분석 실패"),
    MED_AI_002("ESG-MED-AI-002", "미디어 데이터 조회 실패"),

    // ===== 뉴스 인텔리전스 (NWS) =====
    NWS_AI_001("ESG-NWS-AI-001", "뉴스 수집 실패"),
    NWS_VAL_001("ESG-NWS-VAL-001", "뉴스 검색 조건 검증 실패"),

    // ===== ESG 표준 문서 (STD) =====
    STD_AI_001("ESG-STD-AI-001", "표준 문서 분석 실패"),
    STD_AI_002("ESG-STD-AI-002", "문서 인덱싱 실패"),

    // ===== 탄소 크레딧 (CRB) =====
    CRB_AI_001("ESG-CRB-AI-001", "탄소 거래 시그널 조회 실패"),
    CRB_AI_002("ESG-CRB-AI-002", "탄소 데이터 조회 실패"),

    // ===== 내부 데이터/Data Hub (INT) =====
    INT_AI_001("ESG-INT-AI-001", "내부 데이터 분석 실패"),
    INT_VAL_001("ESG-INT-VAL-001", "내부 데이터 검증 실패"),
    INT_VAL_002("ESG-INT-VAL-002", "Data Hub 연결 실패"),

    // ===== AI 서비스 공통 에러 =====
    AI_TIMEOUT("ESG-AI-TIMEOUT", "AI 서비스 타임아웃"),
    AI_UNAVAILABLE("ESG-AI-UNAVAILABLE", "AI 서비스 연결 불가"),
    AI_RESPONSE_ERROR("ESG-AI-RESPONSE-001", "AI 서비스 응답 오류"),
    AI_PARSE_ERROR("ESG-AI-PARSE-001", "AI 서비스 응답 파싱 실패"),

    // ===== 공통 시스템 에러 =====
    INTERNAL_SERVER_ERROR("ESG-SYS-001", "내부 서버 오류가 발생했습니다.");

    private final String code;
    private final String message;
}

