export interface Issue {
  id: string;
  title: string;
  description: string;
  category: string;
  financialScore: number;
  impactScore: number;
  dataHubLinked: boolean;
  sources: string[];
  active: boolean;
}

export interface Topic {
  id: string;
  title: string;
  description: string;
  score: number;
  dataHubLinked: boolean;
}

export interface SurveyResponse {
  selectedIssues: string[];
  scores: Record<string, number>;
  stakeholderType: string;
}

export interface MaterialityData {
  issueId: string;
  title: string;
  financialMateriality: number;
  impactMateriality: number;
}

export interface CarbonSignal {
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  predictedPrice: number;
  recommendation: string;
}
