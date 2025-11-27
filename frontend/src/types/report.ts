// frontend/src/types/report.ts

export interface IssueData {
  id: string;
  name: string;
  category: 'environment' | 'social' | 'governance';
  surveyImpactScore: number;
  surveyFinancialScore: number;
  mediaImpactScore: number;
  mediaFinancialScore: number;
}

export interface MaterialityAssessmentSaveRequest {
  companyId: string;
  reportYear: number;
  issues: IssueData[];
  top5PriorityIssueIds: string[];
}

export interface ReportGenerationStatus {
  requested: boolean;
  reportId: string | null;
  status: 'PENDING' | 'GENERATING' | 'COMPLETED' | 'FAILED';
  message: string;
}

export interface AIReportGenerationRequest {
  company_id: string;
  company_name: string;
  industry: string;
  report_year: number;
  impact_issues: Array<{
    issue_id: string;
    issue_name: string;
    category: string;
    impact_score: number;
    financial_score: number;
    priority_rank: number;
  }>;
  financial_issues: Array<{
    issue_id: string;
    issue_name: string;
    category: string;
    impact_score: number;
    financial_score: number;
    priority_rank: number;
  }>;
}

export interface AIReportSection {
  issue_id: string;
  issue_name: string;
  category: string;
  materiality_type: 'impact' | 'financial';
  priority_rank: number;
  section_html: string;
}

export interface AIReportResponse {
  success: boolean;
  report_id: string;
  company_id: string;
  report_year: number;
  full_html: string;
  sections: AIReportSection[];
  processing_time_seconds: number;
}

export interface ReportMetadata {
  issueCount: number;
  priorityIssueIds: string[];
  kpiDataAvailable: boolean;
  aiModel: string;
  processingTimeMs: number;
}
