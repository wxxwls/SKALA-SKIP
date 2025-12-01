/**
 * Media API
 * 뉴스/미디어 분석 API
 */

import apiClient from './axios.config';

export interface NewsArticle {
  title: string;
  cleanTitle: string;
  description: string;
  link: string;
  pubDate: string;
  esgIssues: string[];
  esgCategories: string[];
  sentiment: string;
  sentimentScore: number;
  positiveCount: number;
  negativeCount: number;
}

export interface IssueStatistic {
  issue: string;
  count: number;
  percentage: number;
  esgCategory: string;
}

export interface SentimentStatistics {
  positive: number;
  negative: number;
  neutral: number;
  avgScore: number;
}

export interface Statistics {
  issueStatistics: IssueStatistic[];
  sentimentStatistics: SentimentStatistics;
  categoryStatistics: Record<string, number>;
}

export interface AnalyzeNewsResponse {
  totalCollected: number;
  uniqueArticles: number;
  articles: NewsArticle[];
  statistics: Statistics;
}

export interface AnalyzeNewsRequest {
  keywords: string[];
  maxPages?: number;
}

export interface EsgIssue {
  name: string;
  category: string;
  keywords: string[];
}

export interface EsgIssuesResponse {
  data: {
    issues: EsgIssue[];
    total_count: number;
  };
}

export const mediaApi = {
  /**
   * 미디어 데이터 조회
   */
  getMediaData: async () => {
    const response = await apiClient.get('/api/v1/media');
    return response.data;
  },

  /**
   * 뉴스 분석
   */
  analyzeNews: async (request: AnalyzeNewsRequest): Promise<AnalyzeNewsResponse> => {
    const response = await apiClient.post<{ data: AnalyzeNewsResponse }>('/api/v1/media/analyze', request);
    return response.data.data;
  },

  /**
   * ESG 이슈 정의 조회
   */
  getEsgIssues: async (): Promise<EsgIssuesResponse> => {
    const response = await apiClient.get<EsgIssuesResponse>('/api/v1/media/issues');
    return response.data;
  }
};

export default mediaApi;
