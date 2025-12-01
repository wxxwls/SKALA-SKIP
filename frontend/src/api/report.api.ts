/**
 * Report API Module
 *
 * ESG 보고서 생성 및 관리 API
 */

import apiClient from './axios.config';

const BASE_URL = '/api/v1/report';

/**
 * 이슈 데이터 타입
 */
export interface IssueData {
  id: string;
  name: string;
  category: 'environment' | 'social' | 'governance';
  surveyImpactScore: number;
  surveyFinancialScore: number;
  mediaImpactScore: number;
  mediaFinancialScore: number;
}

/**
 * 중대성 평가 저장 요청 타입
 */
export interface MaterialityAssessmentSaveRequest {
  companyId: string;
  reportYear: number;
  issues: IssueData[];
  top5PriorityIssueIds: string[];
}

/**
 * 보고서 생성 상태 타입
 */
export interface ReportGenerationStatus {
  requested: boolean;
  reportId: string | null;
  status: 'PENDING' | 'GENERATING' | 'COMPLETED' | 'FAILED';
  message: string;
}

/**
 * 중대성 평가 저장 응답 타입
 */
export interface MaterialityAssessmentSaveResponse {
  assessmentId: string;
  companyId: string;
  reportYear: number;
  savedIssueCount: number;
  top5PriorityIssueIds: string[];
  savedAt: string;
  reportStatus: ReportGenerationStatus;
}

/**
 * 이슈 섹션 응답 타입
 */
export interface IssueSectionResponse {
  issueId: string;
  issueName: string;
  category: string;
  sectionHtml: string;
  hasKpiData: boolean;
  missingKpis: string[];
}

/**
 * 보고서 메타데이터 타입
 */
export interface ReportMetadata {
  issueCount: number;
  priorityIssueIds: string[];
  kpiDataAvailable: boolean;
  aiModel: string;
  processingTimeMs: number;
}

/**
 * ESG 보고서 응답 타입
 */
export interface ESGReportResponse {
  reportId: string;
  companyId: string;
  reportYear: number;
  reportHtml: string;
  sections: IssueSectionResponse[];
  metadata: ReportMetadata;
  generatedAt: string;
}

/**
 * API 응답 래퍼 타입
 */
export interface ApiResponseWrapper<T> {
  success: boolean;
  data: T | null;
  error: {
    code: string;
    message: string;
    details?: string;
  } | null;
  timestamp: string;
}

/**
 * Report API
 */
/**
 * AI Service 직접 호출을 위한 타입
 *
 * NOTE: 보고서 생성 시 영향 중대성 상위 5개 + 재무 중대성 상위 5개 = 총 10개 이슈 처리
 */
export interface AIReportGenerationRequest {
  company_context: {
    company_id: string;
    company_name: string;
    industry: string;
    year: number;
  };
  issues: Array<{
    id: string;
    name: string;
    category: 'E' | 'S' | 'G' | 'Cross';
    impact_score: number;
    financial_score: number;
    is_priority: boolean;
  }>;
  // 영향 중대성 상위 5개 이슈 ID
  impact_priority_issue_ids: string[];
  // 재무 중대성 상위 5개 이슈 ID
  financial_priority_issue_ids: string[];
  // 기존 호환성 (deprecated)
  priority_issue_ids?: string[];
  kpi_data_by_issue?: Record<string, Array<{
    kpi_name: string;
    kpi_value: string | null;
    unit: string | null;
    year: number;
    is_null: boolean;
  }>>;
  language?: 'ko' | 'en';
}

export interface AIReportGenerationResponse {
  success: boolean;
  report_html: string | null;
  report_markdown: string | null;
  sections: Array<{
    issue_id: string;
    issue_name: string;
    category: string;
    materiality_type: 'impact' | 'financial';  // 영향 중대성 / 재무 중대성 구분
    priority_rank: number;  // 우선순위 (1-5)
    section_html: string;
    has_kpi_data: boolean;
    missing_kpis: string[];
  }>;
  error: {
    code: string;
    message: string;
    details?: string;
  } | null;
  metadata: {
    processing_time_ms: number;
    ai_model: string;
    tokens_used: number | null;
    sources_used: string[];
  } | null;
}

export interface AIReportModifyRequest {
  instruction: string;
  current_report: string;
  company_name?: string;
}

export interface AIReportModifyResponse {
  success: boolean;
  modified_report: string | null;
  modified_html: string | null;
  message: string;
  error: {
    code: string;
    message: string;
    details?: string;
  } | null;
}

// AI Service Base URL (환경 변수 사용)
const AI_SERVICE_URL = import.meta.env.VITE_AI_SERVICE_URL || 'http://localhost:8000';

export const reportApi = {
  /**
   * 중대성 평가 저장 및 AI 보고서 생성
   *
   * @param companyId 기업 ID
   * @param request 중대성 평가 데이터
   * @returns 저장 응답 (보고서 생성 상태 포함)
   */
  async saveAndGenerateReport(
    companyId: string,
    request: MaterialityAssessmentSaveRequest
  ): Promise<MaterialityAssessmentSaveResponse> {
    const { data } = await apiClient.post<ApiResponseWrapper<MaterialityAssessmentSaveResponse>>(
      `${BASE_URL}/${companyId}/generate`,
      request
    );

    if (!data.success || !data.data) {
      throw new Error(data.error?.message || '보고서 생성에 실패했습니다');
    }

    return data.data;
  },

  /**
   * ESG 보고서 조회
   *
   * @param companyId 기업 ID
   * @param year 보고서 연도
   * @returns ESG 보고서
   */
  async getReport(companyId: string, year: number): Promise<ESGReportResponse> {
    const { data } = await apiClient.get<ApiResponseWrapper<ESGReportResponse>>(
      `${BASE_URL}/${companyId}`,
      { params: { year } }
    );

    if (!data.success || !data.data) {
      throw new Error(data.error?.message || '보고서를 찾을 수 없습니다');
    }

    return data.data;
  },

  /**
   * ESG 보고서 재생성
   *
   * @param companyId 기업 ID
   * @param year 보고서 연도
   * @returns 재생성된 ESG 보고서
   */
  async regenerateReport(companyId: string, year: number): Promise<ESGReportResponse> {
    const { data } = await apiClient.post<ApiResponseWrapper<ESGReportResponse>>(
      `${BASE_URL}/${companyId}/regenerate`,
      null,
      { params: { year } }
    );

    if (!data.success || !data.data) {
      throw new Error(data.error?.message || '보고서 재생성에 실패했습니다');
    }

    return data.data;
  },

  /**
   * AI Service 직접 호출 - 보고서 생성
   */
  async generateReportDirect(request: AIReportGenerationRequest): Promise<AIReportGenerationResponse> {
    const response = await fetch(`${AI_SERVICE_URL}/internal/v1/reports/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`AI Service error: ${response.status}`);
    }

    return response.json();
  },

  /**
   * AI Service 직접 호출 - 보고서 수정
   */
  async modifyReportDirect(request: AIReportModifyRequest): Promise<AIReportModifyResponse> {
    const response = await fetch(`${AI_SERVICE_URL}/internal/v1/reports/modify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`AI Service error: ${response.status}`);
    }

    return response.json();
  }
};

export default reportApi;
