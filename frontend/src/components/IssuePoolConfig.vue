<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { 
  Sparkles, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  X, 
  ChevronRight, 
  BarChart2, 
  Globe, 
  TrendingUp, 
  ArrowRight,
  ExternalLink,
  Loader2,
  Send
} from 'lucide-vue-next';
import apiClient from '@/api/axios.config';
import aiClient from '@/api/aiClient';
import { mediaApi } from '@/api/media.api';

// =============================================================================
// Cache Helpers
// =============================================================================
const CACHE_DURATION = 30 * 60 * 1000; // 30 minutes

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const getCache = <T>(key: string): T | null => {
  try {
    const cached = localStorage.getItem(key);
    if (!cached) return null;
    const entry: CacheEntry<T> = JSON.parse(cached);
    if (Date.now() - entry.timestamp > CACHE_DURATION) {
      localStorage.removeItem(key);
      return null;
    }
    return entry.data;
  } catch {
    return null;
  }
};

const setCache = <T>(key: string, data: T): void => {
  try {
    localStorage.setItem(key, JSON.stringify({ data, timestamp: Date.now() }));
  } catch (e) {
    console.warn('Cache storage failed:', e);
  }
};

// =============================================================================
// State & Data
// =============================================================================
const isIssuePoolGenerated = ref(false);
const isGeneratingReport = ref(false);
const showReportModal = ref(false);
const showSurveyModal = ref(false);
const generationProgress = ref(0);
const generationStep = ref('');

const issues = ref([
  { id: 'issue1', name: '기후변화 대응', category: 'environment' },
  { id: 'issue2', name: '신재생에너지 확대 및 전력 효율화', category: 'environment' },
  { id: 'issue3', name: '환경영향 관리', category: 'environment' },
  { id: 'issue4', name: '생물다양성 보호', category: 'environment' },
  { id: 'issue5', name: '친환경 사업/기술 투자', category: 'environment' },
  { id: 'issue6', name: '인재양성 및 다양성', category: 'social' },
  { id: 'issue7', name: '인권경영 고도화', category: 'social' },
  { id: 'issue8', name: '안전보건 관리', category: 'social' },
  { id: 'issue9', name: '공급망 ESG 관리', category: 'governance' },
  { id: 'issue10', name: '책임있는 제품/서비스 관리', category: 'social' },
  { id: 'issue11', name: '정보보안 및 프라이버시', category: 'governance' },
  { id: 'issue12', name: '지역사회 공헌', category: 'social' },
  { id: 'issue13', name: '포트폴리오 ESG 관리', category: 'governance' },
  { id: 'issue14', name: '투명한 이사회 경영', category: 'governance' },
  { id: 'issue15', name: '윤리 및 컴플라이언스', category: 'governance' },
  { id: 'issue16', name: '주주가치 제고', category: 'governance' },
  { id: 'issue17', name: '리스크 관리', category: 'governance' },
  { id: 'issue18', name: '이해관계자 소통', category: 'governance' }
]);

const analyses = ref([
  { id: 'esg', name: 'ESG 표준 분석', summary: 'GRI/SASB 표준 기반 분석', icon: Globe, color: '#10B981' },
  { id: 'benchmark', name: '벤치마킹 분석', summary: '경쟁사 이슈 커버리지 비교', icon: TrendingUp, color: '#6366F1' },
  { id: 'media', name: '미디어 분석', summary: '뉴스 트렌드 및 감성 분석', icon: FileText, color: '#EC4899' },
  { id: 'company', name: '기업 현황 분석', summary: '지속가능성 회계 기준 분석', icon: BarChart2, color: '#F59E0B' }
]);

// LLM 요약 상태
const analysisSummaries = ref<Record<string, string>>({});
const summaryLoading = ref<Record<string, boolean>>({});

const selectedIssue = ref('issue1');
const selectedAnalysis = ref('esg');

const currentIssue = computed(() => issues.value.find(i => i.id === selectedIssue.value));
const currentAnalysis = computed(() => analyses.value.find(a => a.id === selectedAnalysis.value));

// =============================================================================
// Benchmark Logic
// =============================================================================
const benchmarkLoading = ref(false);
const benchmarkData = ref<any>({});
const sk18Issues = ref<string[]>([]);
const benchmarkDetailData = ref<any>(null);
const BENCHMARK_CACHE_KEY = 'esg_benchmark_data_cache';

const loadBenchmarkData = async () => {
  benchmarkLoading.value = true;
  const cached = getCache<any>(BENCHMARK_CACHE_KEY);
  if (cached && cached.issues && cached.data) {
    sk18Issues.value = cached.issues;
    benchmarkData.value = cached.data;
    benchmarkLoading.value = false;
    return;
  }

  try {
    const issuesResponse = await aiClient.get('/internal/v1/benchmarks/issues');
    if (issuesResponse.data.success) sk18Issues.value = issuesResponse.data.issues;
    
    const dataResponse = await aiClient.get('/internal/v1/benchmarks/data');
    if (dataResponse.data.success) {
      benchmarkData.value = dataResponse.data.data;
      setCache(BENCHMARK_CACHE_KEY, { issues: sk18Issues.value, data: benchmarkData.value });
    }
  } catch (e) { console.error(e); } finally { benchmarkLoading.value = false; }
};

const benchmarkCompanies = computed(() => Object.keys(benchmarkData.value));
const getBenchmarkCoverage = (company: string, issue: string) => benchmarkData.value[company]?.[issue]?.coverage || 'No';

const top5Issues = computed(() => {
  if (!sk18Issues.value.length) return [];
  return sk18Issues.value.map(issue => ({
    issue,
    count: benchmarkCompanies.value.filter(c => getBenchmarkCoverage(c, issue) === 'Yes').length
  })).sort((a, b) => b.count - a.count).slice(0, 5);
});

const showBenchmarkDetail = (company: string, issue: string) => {
  const data = benchmarkData.value[company]?.[issue];
  if (data) {
    let matchedIssue = '';
    const response = data.response || '';
    const match = response.match(/(?:매칭:|폴백 매칭:|키워드 발견:)\s*(?:관련 섹션명:\s*)?(.+?)(?:\s*\(유사도|$)/);
    if (match) matchedIssue = match[1].trim();
    
    benchmarkDetailData.value = {
      company, issue, matched_issue: matchedIssue, response, source_pages: data.source_pages || []
    };
  }
};

// =============================================================================
// ESG Standards Logic
// =============================================================================
const esgStandardsLoading = ref(false);
const esgStandardsError = ref('');
const esgIssuesWithDisclosures = ref<any[]>([]);
const esgAnalysisResult = ref<any>(null);
const esgAnalysisLoading = ref(false);
const ESG_STANDARDS_CACHE_KEY = 'esg_standards_data_cache';

const loadESGStandardsData = async () => {
  esgStandardsLoading.value = true;
  const cached = getCache<any[]>(ESG_STANDARDS_CACHE_KEY);
  if (cached) {
    esgIssuesWithDisclosures.value = cached;
    esgStandardsLoading.value = false;
    return;
  }

  try {
    const response = await apiClient.get('/api/v1/standards/issues/with-disclosures');
    if (response.data.success) {
      esgIssuesWithDisclosures.value = response.data.data;
      setCache(ESG_STANDARDS_CACHE_KEY, response.data.data);
    } else esgStandardsError.value = response.data.error?.message;
  } catch (e: any) { esgStandardsError.value = e.message; } finally { esgStandardsLoading.value = false; }
};

const selectedESGIssueData = computed(() => {
  const issueName = currentIssue.value?.name;
  return issueName ? esgIssuesWithDisclosures.value.find(i => i.issue === issueName) : null;
});

const getESGCategoryColor = (cat: string) => ({ E: '#10B981', S: '#3B82F6', G: '#8B5CF6' }[cat] || '#6B7280');
const getESGCategoryLabel = (cat: string) => ({ E: '환경', S: '사회', G: '지배구조' }[cat] || '');
const getStandardColor = (std: string) => std === 'GRI' ? '#EA7F52' : '#0891B2';

// =============================================================================
// Media Logic
// =============================================================================
const mediaLoading = ref(false);
const mediaError = ref('');
const mediaTotalArticles = ref(0);
const mediaArticles = ref<any[]>([]);
const mediaPositiveCount = ref(0);
const mediaNegativeCount = ref(0);
const mediaNeutralCount = ref(0);
const MEDIA_CACHE_KEY = 'esg_media_data_cache';

const loadMediaData = async () => {
  mediaLoading.value = true;
  const cached = getCache<any>(MEDIA_CACHE_KEY);
  if (cached) {
    mediaTotalArticles.value = cached.totalArticles;
    mediaArticles.value = cached.articles;
    mediaPositiveCount.value = cached.positiveCount;
    mediaNegativeCount.value = cached.negativeCount;
    mediaNeutralCount.value = cached.neutralCount;
    mediaLoading.value = false;
    return;
  }

  try {
    // analyzeNews API 사용 (NewsView와 동일)
    const response = await mediaApi.analyzeNews({
      keywords: ['ESG', 'SK', '탄소', '지속가능', '환경'],
      maxPages: 3
    });

    mediaTotalArticles.value = response.uniqueArticles || response.articles?.length || 0;
    mediaArticles.value = response.articles?.map(article => ({
      title: article.title,
      clean_title: article.cleanTitle,
      description: article.description,
      link: article.link,
      pubDate: article.pubDate,
      esg_issues: article.esgIssues,
      esg_categories: article.esgCategories,
      sentiment: article.sentiment,
      sentimentScore: article.sentimentScore
    })) || [];

    const stats = response.statistics?.sentimentStatistics;
    mediaPositiveCount.value = stats?.positive || 0;
    mediaNegativeCount.value = stats?.negative || 0;
    mediaNeutralCount.value = stats?.neutral || 0;

    setCache(MEDIA_CACHE_KEY, {
      totalArticles: mediaTotalArticles.value,
      articles: mediaArticles.value,
      positiveCount: mediaPositiveCount.value,
      negativeCount: mediaNegativeCount.value,
      neutralCount: mediaNeutralCount.value
    });
  } catch (e: any) {
    console.error('Media data load failed:', e);
    mediaError.value = e.message;

    // API 실패 시 샘플 데이터로 fallback
    const sampleArticles = [
      { title: 'SK그룹, ESG 경영 강화로 지속가능 성장 추진', clean_title: 'SK그룹, ESG 경영 강화로 지속가능 성장 추진', description: 'SK그룹이 ESG 경영 강화를 통해 지속 가능한 성장을 추진하고 있다.', link: '#', pubDate: new Date().toISOString(), esg_issues: ['탄소중립', 'ESG 경영'], esg_categories: ['환경', '지배구조'], sentiment: '긍정', sentimentScore: 0.85 },
      { title: '기후변화 대응, 탄소중립 2050 목표 달성 위한 전략', clean_title: '기후변화 대응, 탄소중립 2050 목표 달성 위한 전략', description: '기업들이 탄소중립 2050 목표 달성을 위해 다양한 전략을 수립하고 있다.', link: '#', pubDate: new Date().toISOString(), esg_issues: ['탄소중립', '기후변화'], esg_categories: ['환경'], sentiment: '긍정', sentimentScore: 0.78 },
      { title: '공급망 ESG 리스크 관리 중요성 대두', clean_title: '공급망 ESG 리스크 관리 중요성 대두', description: '글로벌 공급망에서 ESG 리스크 관리의 중요성이 높아지고 있다.', link: '#', pubDate: new Date().toISOString(), esg_issues: ['공급망 관리', 'ESG 리스크'], esg_categories: ['사회', '지배구조'], sentiment: '중립', sentimentScore: 0.5 },
      { title: '산업안전 강화, 근로자 보호 정책 확대', clean_title: '산업안전 강화, 근로자 보호 정책 확대', description: '기업들이 산업안전 강화와 근로자 보호를 위한 정책을 확대하고 있다.', link: '#', pubDate: new Date().toISOString(), esg_issues: ['산업안전', '근로자 권리'], esg_categories: ['사회'], sentiment: '긍정', sentimentScore: 0.72 },
      { title: '환경오염 논란, 일부 기업 제재 조치', clean_title: '환경오염 논란, 일부 기업 제재 조치', description: '환경오염 문제로 일부 기업들이 규제 당국의 제재를 받고 있다.', link: '#', pubDate: new Date().toISOString(), esg_issues: ['환경오염', '규제 리스크'], esg_categories: ['환경'], sentiment: '부정', sentimentScore: -0.65 },
      { title: '재생에너지 투자 확대, 친환경 전환 가속화', clean_title: '재생에너지 투자 확대, 친환경 전환 가속화', description: '기업들의 재생에너지 투자가 확대되며 친환경 전환이 가속화되고 있다.', link: '#', pubDate: new Date().toISOString(), esg_issues: ['재생에너지', '친환경'], esg_categories: ['환경'], sentiment: '긍정', sentimentScore: 0.82 },
      { title: 'ESG 공시 의무화, 기업 대응 준비 필요', clean_title: 'ESG 공시 의무화, 기업 대응 준비 필요', description: 'ESG 공시가 의무화됨에 따라 기업들의 대응 준비가 필요한 상황이다.', link: '#', pubDate: new Date().toISOString(), esg_issues: ['ESG 공시', '규제 대응'], esg_categories: ['지배구조'], sentiment: '중립', sentimentScore: 0.4 },
      { title: '다양성 경영, 여성 임원 비율 확대', clean_title: '다양성 경영, 여성 임원 비율 확대', description: '기업들이 다양성 경영의 일환으로 여성 임원 비율을 확대하고 있다.', link: '#', pubDate: new Date().toISOString(), esg_issues: ['다양성', '여성 리더십'], esg_categories: ['사회', '지배구조'], sentiment: '긍정', sentimentScore: 0.75 }
    ];

    mediaTotalArticles.value = sampleArticles.length;
    mediaArticles.value = sampleArticles;
    mediaPositiveCount.value = sampleArticles.filter(a => a.sentiment === '긍정').length;
    mediaNegativeCount.value = sampleArticles.filter(a => a.sentiment === '부정').length;
    mediaNeutralCount.value = sampleArticles.filter(a => a.sentiment === '중립').length;

    setCache(MEDIA_CACHE_KEY, {
      totalArticles: mediaTotalArticles.value,
      articles: mediaArticles.value,
      positiveCount: mediaPositiveCount.value,
      negativeCount: mediaNegativeCount.value,
      neutralCount: mediaNeutralCount.value
    });
  } finally {
    mediaLoading.value = false;
  }
};

const filteredMediaArticles = computed(() => {
  const issueToFilter = currentIssue.value?.name;
  if (!issueToFilter) return mediaArticles.value.slice(0, 10);
  return mediaArticles.value.filter(article => 
    article.esg_issues?.some((i: string) => i.includes(issueToFilter) || issueToFilter.includes(i))
  ).slice(0, 10);
});

const getMediaSentimentStyle = (sentiment: string) => {
  switch (sentiment) {
    case '긍정': return { background: '#D1FAE5', color: '#047857' };
    case '부정': return { background: '#FEE2E2', color: '#B91C1C' };
    default: return { background: '#F3F4F6', color: '#6B7280' };
  }
};

const formatMediaDate = (dateStr: string) => {
  try { return new Date(dateStr).toLocaleDateString('ko-KR', { month: '2-digit', day: '2-digit' }); }
  catch { return dateStr; }
};

const openMediaArticle = (link: string) => { if (link) window.open(link, '_blank'); };

// =============================================================================
// General Logic
// =============================================================================
const handleAnalysisSelect = (id: string) => {
  selectedAnalysis.value = id;
  if (id === 'benchmark') loadBenchmarkData();
  else if (id === 'esg') loadESGStandardsData();
  else if (id === 'media') loadMediaData();
};

// 이슈별 LLM 요약 키 생성
const getSummaryKey = (analysisId: string, issueId: string) => `${analysisId}_${issueId}`;

// LLM 요약 로드 함수 (이슈별로 다른 요약 생성)
const loadAnalysisSummary = async (analysisId: string, issueId?: string) => {
  const currentIssueId = issueId || selectedIssue.value;
  const summaryKey = getSummaryKey(analysisId, currentIssueId);

  if (analysisSummaries.value[summaryKey]) return;

  summaryLoading.value[summaryKey] = true;

  try {
    let summary = '';
    const issue = issues.value.find(i => i.id === currentIssueId);
    const issueName = issue?.name || '';
    const issueCategory = issue?.category || '';

    switch (analysisId) {
      case 'esg':
        await loadESGStandardsData();
        if (esgIssuesWithDisclosures.value.length > 0) {
          const issueData = esgIssuesWithDisclosures.value.find((i: any) => i.issue === issueName);
          if (issueData) {
            const griCount = issueData.gri_count || 0;
            const sasbCount = issueData.sasb_count || 0;
            const disclosures = issueData.disclosures || [];
            const griItems = disclosures.filter((d: any) => d.standard === 'GRI').slice(0, 2);
            const sasbItems = disclosures.filter((d: any) => d.standard === 'SASB').slice(0, 2);

            let detailText = '';
            if (griItems.length > 0) {
              detailText += `GRI 주요 지표: ${griItems.map((d: any) => d.id).join(', ')}. `;
            }
            if (sasbItems.length > 0) {
              detailText += `SASB 주요 지표: ${sasbItems.map((d: any) => d.id).join(', ')}.`;
            }

            summary = `"${issueName}" 이슈에 GRI ${griCount}개, SASB ${sasbCount}개 공시 기준이 매핑되어 있습니다. ${detailText} 해당 표준에 따른 정량적/정성적 공시가 권고됩니다.`;
          } else {
            summary = `"${issueName}" 이슈에 대한 ESG 표준 매핑 정보가 준비 중입니다. GRI/SASB 기준에 따른 공시 항목을 확인해주세요.`;
          }
        } else {
          summary = 'ESG 표준 데이터를 분석 중입니다.';
        }
        break;

      case 'benchmark':
        await loadBenchmarkData();
        if (benchmarkCompanies.value.length > 0 && sk18Issues.value.length > 0) {
          const coverageCount = benchmarkCompanies.value.filter(c => getBenchmarkCoverage(c, issueName) === 'Yes').length;
          const coverageRate = Math.round((coverageCount / benchmarkCompanies.value.length) * 100);
          const companiesWithIssue = benchmarkCompanies.value.filter(c => getBenchmarkCoverage(c, issueName) === 'Yes').slice(0, 3);

          if (coverageCount > 0) {
            summary = `"${issueName}" 이슈는 ${benchmarkCompanies.value.length}개 경쟁사 중 ${coverageCount}개사(${coverageRate}%)가 다루고 있습니다. ${companiesWithIssue.length > 0 ? `주요 기업: ${companiesWithIssue.join(', ')}.` : ''} ${coverageRate >= 70 ? '업계 필수 이슈로 판단됩니다.' : coverageRate >= 40 ? '주요 이슈로 검토가 필요합니다.' : '차별화 기회가 있는 이슈입니다.'}`;
          } else {
            summary = `"${issueName}" 이슈는 분석 대상 ${benchmarkCompanies.value.length}개 경쟁사 중 공시된 기업이 없습니다. 선제적 대응을 통한 차별화 기회로 활용할 수 있습니다.`;
          }
        } else {
          summary = '벤치마킹 데이터를 분석 중입니다.';
        }
        break;

      case 'media':
        // 미디어 분석: 이슈 카테고리별 맞춤 인사이트 제공
        const mediaInsights: Record<string, string> = {
          environment: '기후변화, 탄소중립, 재생에너지 관련 뉴스가 증가 추세입니다. 환경 이슈에 대한 선제적 커뮤니케이션이 중요합니다.',
          social: '인권, 다양성, 안전 관련 뉴스가 주목받고 있습니다. 사회적 가치 창출 활동의 적극적 홍보를 권장합니다.',
          governance: '지배구조 투명성, ESG 경영에 대한 미디어 관심이 높습니다. 이사회 활동과 윤리경영 성과 공개를 권장합니다.'
        };

        const categoryMediaInsight = mediaInsights[issueCategory] || 'ESG 관련 미디어 동향을 모니터링하여 리스크 관리에 활용하세요.';
        summary = `"${issueName}" 관련 미디어 트렌드 분석: ${categoryMediaInsight} 뉴스 페이지에서 상세 기사를 확인할 수 있습니다.`;
        break;

      case 'company':
        const categoryLabels: Record<string, string> = {
          environment: '환경(E)',
          social: '사회(S)',
          governance: '지배구조(G)'
        };
        const categoryLabel = categoryLabels[issueCategory] || 'ESG';

        const industryInsights: Record<string, string> = {
          environment: '탄소배출량, 에너지사용량, 폐기물 관리 등 정량 데이터 수집 및 목표 설정이 중요합니다.',
          social: '임직원 다양성, 안전사고율, 사회공헌 활동 등의 지표 관리가 필요합니다.',
          governance: '이사회 구성, 윤리경영 체계, 리스크 관리 프로세스 점검이 권고됩니다.'
        };

        summary = `"${issueName}"은 ${categoryLabel} 영역의 핵심 이슈입니다. SASB 기준에 따르면 ${industryInsights[issueCategory] || '해당 이슈에 대한 체계적인 관리와 공시가 필요합니다.'} 재무적 영향도를 고려한 우선순위 설정을 권장합니다.`;
        break;
    }

    analysisSummaries.value[summaryKey] = summary;
  } catch (error) {
    console.error(`Failed to load summary for ${analysisId}:`, error);
    analysisSummaries.value[getSummaryKey(analysisId, currentIssueId)] = '요약 정보를 불러올 수 없습니다.';
  } finally {
    summaryLoading.value[summaryKey] = false;
  }
};

// 현재 선택된 이슈에 대한 모든 분석 요약 로드
const loadAllSummaries = async () => {
  await Promise.all([
    loadAnalysisSummary('esg'),
    loadAnalysisSummary('benchmark'),
    loadAnalysisSummary('media'),
    loadAnalysisSummary('company')
  ]);
};

// 이슈 변경 시 요약 다시 로드
watch(selectedIssue, () => {
  loadAllSummaries();
});

const startIssuePoolGeneration = () => {
  isGeneratingReport.value = true;
  showReportModal.value = true;
  generationProgress.value = 0;

  const interval = setInterval(() => {
    generationProgress.value += 5;
    if (generationProgress.value <= 30) generationStep.value = 'ESG 표준 분석 중...';
    else if (generationProgress.value <= 60) generationStep.value = '벤치마킹 데이터 분석 중...';
    else if (generationProgress.value <= 90) generationStep.value = '미디어 트렌드 분석 중...';
    else generationStep.value = '종합 리포트 생성 중...';

    if (generationProgress.value >= 100) {
      clearInterval(interval);
      isGeneratingReport.value = false;
      isIssuePoolGenerated.value = true;
      // Load initial data and summaries
      loadESGStandardsData();
      loadAllSummaries();
    }
  }, 150);
};

const handleSendSurvey = () => {
  alert('설문조사가 전송되었습니다!');
  showSurveyModal.value = false;
};

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'environment': return '#10B981';
    case 'social': return '#3B82F6';
    case 'governance': return '#8B5CF6';
    default: return '#6B7280';
  }
};

const getCategoryLabel = (category: string) => {
  switch (category) {
    case 'environment': return '환경';
    case 'social': return '사회';
    case 'governance': return '지배구조';
    default: return '';
  }
};
</script>

<template>
  <div class="issue-pool-container">
    <!-- Header (Only show when generated or generating) -->
    <header v-if="isIssuePoolGenerated || isGeneratingReport" class="header">
      <div class="header-content">
        <div class="title-section">
          <h1>이슈풀 구성</h1>
          <span class="subtitle">AI 기반 ESG 이슈 분석 및 도출</span>
        </div>
        
        <div v-if="isIssuePoolGenerated" class="actions">
          <button class="action-btn secondary" @click="startIssuePoolGeneration" :disabled="isGeneratingReport">
            <Sparkles class="w-4 h-4" />
            <span>재구성</span>
          </button>
          <button class="action-btn primary" @click="showSurveyModal = true">
            <FileText class="w-4 h-4" />
            <span>설문조사 생성</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      
      <!-- Empty State (Landing Page Style) -->
      <div v-if="!isIssuePoolGenerated && !isGeneratingReport" class="empty-state-landing">
        <div class="landing-content">
          <div class="landing-text-section">
            <div class="badge-pill">AI Analysis</div>
            <h1>
              <span class="main-title">이슈풀 구성</span><br/>
              <span class="sub-title">AI 기반 ESG 이슈 분석</span>
            </h1>
            <p class="description">
              기업의 지속가능경영 보고서와 미디어 데이터를 심층 분석하여<br/>
              <strong>최적의 중대성 이슈</strong>를 자동으로 도출해 드립니다.
            </p>
            <button class="start-btn-large" @click="startIssuePoolGeneration">
              <span class="btn-text">분석 시작하기</span>
              <ArrowRight class="w-5 h-5" />
            </button>
            <div class="feature-tags">
              <span>#GRI/SASB 표준</span>
              <span>#경쟁사 벤치마킹</span>
              <span>#미디어 트렌드</span>
            </div>
          </div>
          <div class="landing-visual">
            <div class="visual-bg-circle"></div>
            <img src="/dashboard_preview.png" alt="Dashboard Preview" class="dashboard-preview-img" />
            <div class="floating-card c1">
              <BarChart2 class="w-5 h-5 text-blue-500" />
              <span>데이터 분석</span>
            </div>
            <div class="floating-card c2">
              <Sparkles class="w-5 h-5 text-orange-500" />
              <span>AI 인사이트</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Generation Overlay (3D Animation) -->
      <div v-if="isGeneratingReport" class="generation-overlay">
        <div class="generation-content">
          <h2>기업의 ESG 데이터를<br/>면밀히 분석하고 있어요.</h2>
          
          <div class="card-stack-animation">
            <div class="card-item card-1"></div>
            <div class="card-item card-2"></div>
            <div class="card-item card-3">
              <div class="card-inner">
                <div class="skeleton-line w-3/4"></div>
                <div class="skeleton-line w-1/2"></div>
                <div class="skeleton-box"></div>
              </div>
            </div>
            <div class="floating-sparkle">
              <Sparkles class="w-8 h-8 text-white" />
            </div>
          </div>

          <div class="progress-status">
            <p class="step-text">{{ generationStep }}</p>
            <div class="progress-bar-track">
              <div class="progress-bar-fill" :style="{ width: generationProgress + '%' }"></div>
            </div>
            <span class="percent-text">{{ generationProgress }}%</span>
          </div>
        </div>
      </div>

      <!-- Dashboard -->
      <div v-if="isIssuePoolGenerated" class="dashboard">
        <!-- Sidebar: Issue List -->
        <aside class="sidebar">
          <div class="sidebar-header">
            <h3>도출된 이슈 목록</h3>
            <span class="badge">{{ issues.length }}개</span>
          </div>
          <div class="issue-list">
            <button
              v-for="(issue, index) in issues"
              :key="issue.id"
              class="issue-item"
              :class="{ active: selectedIssue === issue.id }"
              @click="selectedIssue = issue.id"
            >
              <span class="issue-rank">{{ index + 1 }}</span>
              <span class="issue-name">{{ issue.name }}</span>
              <ChevronRight class="w-4 h-4 arrow" />
            </button>
          </div>
        </aside>

        <!-- Content: Analysis Area -->
        <section class="content-area">
          <!-- Analysis Selector (Cards) -->
          <div class="analysis-selector">
            <div 
              v-for="analysis in analyses" 
              :key="analysis.id"
              class="selector-card"
              :class="{ active: selectedAnalysis === analysis.id }"
              @click="handleAnalysisSelect(analysis.id)"
            >
              <div class="card-icon-wrapper" :style="{ background: analysis.color + '15', color: analysis.color }">
                <component :is="analysis.icon" class="w-6 h-6" />
              </div>
              <div class="card-content">
                <div class="card-title-row">
                  <span class="selector-name">{{ analysis.name }}</span>
                  <CheckCircle v-if="selectedAnalysis === analysis.id" class="w-4 h-4 text-orange-500" />
                </div>
                <p class="selector-desc">
                  <template v-if="summaryLoading[getSummaryKey(analysis.id, selectedIssue)]">
                    <span class="summary-loading">
                      <Loader2 class="w-3 h-3 animate-spin" />
                      <span>분석 중...</span>
                    </span>
                  </template>
                  <template v-else-if="analysisSummaries[getSummaryKey(analysis.id, selectedIssue)]">
                    {{ analysisSummaries[getSummaryKey(analysis.id, selectedIssue)] }}
                  </template>
                  <template v-else>
                    {{ analysis.summary }}
                  </template>
                </p>
              </div>
            </div>
          </div>

          <!-- Analysis Detail View -->
          <div class="analysis-detail">
            <div class="detail-header">
              <div class="header-left">
                <h3>{{ currentAnalysis?.name }}</h3>
                <span class="status-badge">분석 완료</span>
              </div>
              <p>{{ currentAnalysis?.summary }}</p>
            </div>

            <!-- 1. Benchmark Analysis View -->
            <div v-if="selectedAnalysis === 'benchmark'" class="detail-content">
              <div v-if="benchmarkLoading" class="loading-state">
                <Loader2 class="w-8 h-8 animate-spin text-orange-500" />
                <span>벤치마킹 데이터 분석 중...</span>
              </div>
              <div v-else-if="benchmarkCompanies.length > 0" class="benchmark-view">
                <!-- Top 5 Issues -->
                <div class="top-issues-card">
                  <h4>경쟁사 중요 이슈 TOP 5</h4>
                  <div class="tags-wrapper">
                    <div v-for="(item, idx) in top5Issues" :key="idx" class="issue-tag" :class="{ top: idx === 0 }">
                      <span class="rank">#{{ idx + 1 }}</span>
                      <span class="text">{{ item.issue }}</span>
                      <span class="count">{{ item.count }}개사</span>
                    </div>
                  </div>
                </div>

                <!-- Table -->
                <div class="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th class="sticky-col">2024 이슈풀 (18개)</th>
                        <th v-for="company in benchmarkCompanies" :key="company">{{ company }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(issue, idx) in sk18Issues" :key="issue">
                        <td class="sticky-col">
                          <span class="row-idx">{{ idx + 1 }}.</span> {{ issue }}
                        </td>
                        <td v-for="company in benchmarkCompanies" :key="company">
                          <span 
                            v-if="getBenchmarkCoverage(company, issue) === 'Yes'"
                            class="dot-indicator"
                            @click="showBenchmarkDetail(company, issue)"
                          ></span>
                          <span v-else class="dash">-</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div v-else class="empty-data">데이터가 없습니다.</div>
            </div>

            <!-- 2. ESG Standards View -->
            <div v-else-if="selectedAnalysis === 'esg'" class="detail-content">
              <div v-if="esgStandardsLoading" class="loading-state">
                <Loader2 class="w-8 h-8 animate-spin text-orange-500" />
                <span>ESG 표준 데이터 로딩 중...</span>
              </div>
              <div v-else-if="selectedESGIssueData" class="esg-view">
                <div class="esg-header-card">
                  <span class="category-badge" :style="{ background: getESGCategoryColor(selectedESGIssueData.category) }">
                    {{ getESGCategoryLabel(selectedESGIssueData.category) }}
                  </span>
                  <h4>{{ selectedESGIssueData.issue }}</h4>
                  <span class="count-badge">{{ selectedESGIssueData.disclosure_count }}개 공시 기준</span>
                </div>

                <div class="disclosure-list">
                  <div v-for="d in selectedESGIssueData.disclosures" :key="d.id" class="disclosure-card">
                    <div class="d-header">
                      <span class="std-badge" :style="{ color: getStandardColor(d.standard), background: getStandardColor(d.standard) + '20' }">
                        {{ d.standard }}
                      </span>
                      <span class="d-id">{{ d.id }}</span>
                    </div>
                    <p class="d-title">{{ d.title }}</p>
                    <p v-if="d.description" class="d-desc">{{ d.description }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="empty-data">선택된 이슈에 대한 ESG 표준 데이터가 없습니다.</div>
            </div>

            <!-- 3. Media Analysis View -->
            <div v-else-if="selectedAnalysis === 'media'" class="detail-content">
              <div v-if="mediaLoading" class="loading-state">
                <Loader2 class="w-8 h-8 animate-spin text-orange-500" />
                <span>미디어 데이터 분석 중...</span>
              </div>
              <div v-else-if="mediaTotalArticles > 0" class="media-view">
                <div class="stats-row">
                  <div class="stat-card">
                    <span class="val">{{ mediaTotalArticles }}</span>
                    <span class="label">총 기사</span>
                  </div>
                  <div class="stat-card positive">
                    <span class="val">{{ mediaPositiveCount }}</span>
                    <span class="label">긍정</span>
                  </div>
                  <div class="stat-card negative">
                    <span class="val">{{ mediaNegativeCount }}</span>
                    <span class="label">부정</span>
                  </div>
                </div>

                <div class="article-list">
                  <div v-for="(article, idx) in filteredMediaArticles" :key="idx" class="article-card" @click="openMediaArticle(article.link)">
                    <div class="a-header">
                      <span class="sentiment-badge" :style="getMediaSentimentStyle(article.sentiment)">
                        {{ article.sentiment }}
                      </span>
                      <span class="date">{{ formatMediaDate(article.pubDate) }}</span>
                    </div>
                    <h5 class="a-title">{{ article.clean_title || article.title }}</h5>
                    <div class="a-footer">
                      <div class="tags">
                        <span v-for="tag in (article.esg_issues || []).slice(0, 1)" :key="tag" class="tag">#{{ tag }}</span>
                      </div>
                      <ExternalLink class="w-3 h-3 text-gray-400" />
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-data">미디어 데이터가 없습니다.</div>
            </div>

            <!-- 4. Company Analysis View (Placeholder) -->
            <div v-else class="detail-content">
               <div class="empty-data">기업 현황 분석 데이터 준비 중입니다.</div>
            </div>

          </div>
        </section>
      </div>
    </main>

    <!-- Modals (Survey, Benchmark Detail) -->
    <!-- Survey Modal -->
    <div v-if="showSurveyModal" class="modal-overlay" @click.self="showSurveyModal = false">
      <div class="modal-card survey-modal">
        <div class="modal-header">
          <h3>설문조사 생성</h3>
          <button class="close-icon" @click="showSurveyModal = false"><X class="w-5 h-5" /></button>
        </div>
        <div class="survey-content">
          <div class="info-box">
            <p>18개 이슈에 대한 중대성 평가 설문지를 생성합니다.</p>
          </div>
          <div class="survey-list">
            <div v-for="(issue, idx) in issues" :key="issue.id" class="survey-item">
              <span class="idx">{{ idx + 1 }}</span>
              <span class="name">{{ issue.name }}</span>
              <div class="scales">
                <div class="scale-group">
                  <span>영향 중대성</span>
                  <div class="dots"><span v-for="i in 5" :key="i" class="dot"></span></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="action-btn primary" @click="handleSendSurvey">
            <Send class="w-4 h-4" /> 전송하기
          </button>
        </div>
      </div>
    </div>

    <!-- Benchmark Detail Modal -->
    <div v-if="benchmarkDetailData" class="modal-overlay" @click.self="benchmarkDetailData = null">
      <div class="modal-card detail-modal">
        <div class="detail-modal-header">
          <h3>{{ benchmarkDetailData.company }}</h3>
          <button @click="benchmarkDetailData = null"><X class="w-5 h-5 text-white" /></button>
        </div>
        <div class="detail-body">
          <div class="detail-row">
            <label>SK 이슈</label>
            <div class="val">{{ benchmarkDetailData.issue }}</div>
          </div>
          <div class="detail-row">
            <label>매핑된 이슈</label>
            <div class="val highlight">{{ benchmarkDetailData.matched_issue || '없음' }}</div>
          </div>
          <div class="detail-row" v-if="benchmarkDetailData.source_pages?.length">
            <label>참조 페이지</label>
            <div class="pages">
              <span v-for="p in benchmarkDetailData.source_pages" :key="p" class="page-tag">p.{{ p }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* --- Layout & Base --- */
.issue-pool-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #F8F9FC;
  font-family: 'Pretendard', sans-serif;
  position: relative;
}

.header {
  background: #FFFFFF;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  padding: 20px 40px;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
}

.title-section h1 { font-size: 24px; font-weight: 700; color: #1A1F2E; margin-bottom: 4px; }
.subtitle { font-size: 14px; color: #64748B; }

.actions { display: flex; gap: 12px; }
.action-btn {
  display: flex; align-items: center; gap: 8px; padding: 10px 20px; border-radius: 12px;
  font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s ease;
}
.action-btn.primary { background: #1A1F2E; color: white; border: 1px solid transparent; }
.action-btn.primary:hover { background: #2D3748; transform: translateY(-1px); }
.action-btn.secondary { background: white; color: #1A1F2E; border: 1px solid #E2E8F0; }

.main-content { flex: 1; overflow: hidden; position: relative; display: flex; flex-direction: column; }

/* --- Empty State (Landing Page Style) --- */
.empty-state-landing {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
  padding: 40px;
}

.landing-content {
  display: flex;
  align-items: center;
  gap: 80px;
  max-width: 1200px;
  width: 100%;
}

.landing-text-section {
  flex: 1;
  max-width: 500px;
}

.badge-pill {
  display: inline-block;
  background: #DBEAFE;
  color: #2563EB;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 100px;
  margin-bottom: 24px;
}

.landing-text-section h1 {
  font-size: 48px;
  line-height: 1.2;
  font-weight: 800;
  margin-bottom: 24px;
  color: #1A1F2E;
}

.main-title { color: #1A1F2E; }
.sub-title { 
  background: linear-gradient(90deg, #2563EB, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.description {
  font-size: 18px;
  color: #64748B;
  line-height: 1.6;
  margin-bottom: 40px;
}

.start-btn-large {
  background: #1A1F2E;
  color: white;
  padding: 18px 40px;
  border-radius: 100px;
  font-size: 18px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 10px 25px rgba(26, 31, 46, 0.2);
}

.start-btn-large:hover {
  transform: translateY(-4px);
  box-shadow: 0 15px 35px rgba(26, 31, 46, 0.3);
  background: #2D3748;
}

.feature-tags {
  margin-top: 32px;
  display: flex;
  gap: 16px;
  color: #94A3B8;
  font-size: 14px;
  font-weight: 500;
}

.landing-visual {
  flex: 1;
  position: relative;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  perspective: 1000px;
}

.visual-bg-circle {
  position: absolute;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(59,130,246,0.1) 0%, rgba(255,255,255,0) 70%);
  border-radius: 50%;
  z-index: 0;
}

.dashboard-preview-img {
  width: 100%;
  max-width: 600px;
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  transform: rotateY(-10deg) rotateX(5deg);
  transition: transform 0.5s ease;
  z-index: 1;
  border: 4px solid white;
}

.landing-visual:hover .dashboard-preview-img {
  transform: rotateY(-5deg) rotateX(2deg) scale(1.02);
}

.floating-card {
  position: absolute;
  background: white;
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 14px;
  color: #1A1F2E;
  z-index: 2;
  animation: float 6s ease-in-out infinite;
}

.floating-card.c1 { top: 20%; left: 0; animation-delay: 0s; }
.floating-card.c2 { bottom: 20%; right: 0; animation-delay: 3s; }

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

/* --- Generation Overlay (3D Animation) --- */
.generation-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(255, 255, 255, 0.98);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.generation-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.generation-content h2 {
  font-size: 28px;
  font-weight: 800;
  color: #1A1F2E;
  margin-bottom: 60px;
  line-height: 1.4;
}

.card-stack-animation {
  position: relative;
  width: 240px;
  height: 160px;
  margin-bottom: 60px;
  perspective: 1000px;
}

.card-item {
  position: absolute;
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  border: 1px solid #E2E8F0;
  transform-origin: center center;
  animation: stack-shuffle 4s infinite ease-in-out;
}

.card-1 { background: #EFF6FF; z-index: 1; animation-delay: 0s; }
.card-2 { background: #DBEAFE; z-index: 2; animation-delay: 1.3s; }
.card-3 { background: white; z-index: 3; animation-delay: 2.6s; display: flex; align-items: center; justify-content: center; }

.card-inner { width: 80%; display: flex; flex-direction: column; gap: 10px; }
.skeleton-line { height: 8px; background: #F1F5F9; border-radius: 4px; }
.skeleton-box { height: 40px; background: #F8FAFC; border-radius: 8px; margin-top: 10px; }

.floating-sparkle {
  position: absolute;
  top: -30px;
  right: -30px;
  background: linear-gradient(135deg, #FF8F68, #FF6B35);
  width: 60px;
  height: 60px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 20px rgba(255, 107, 53, 0.3);
  animation: bounce 2s infinite;
  z-index: 10;
}

@keyframes stack-shuffle {
  0% { transform: translateY(0) scale(1); z-index: 1; opacity: 1; }
  33% { transform: translateY(-40px) scale(0.95); z-index: 0; opacity: 0.8; }
  66% { transform: translateY(10px) scale(0.9); z-index: 0; opacity: 0.5; }
  100% { transform: translateY(0) scale(1); z-index: 1; opacity: 1; }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.progress-status { width: 300px; text-align: center; }
.step-text { font-size: 14px; font-weight: 600; color: #64748B; margin-bottom: 12px; }
.progress-bar-track {
  height: 6px; background: #F1F5F9; border-radius: 3px; overflow: hidden; margin-bottom: 8px;
}
.progress-bar-fill {
  height: 100%; background: linear-gradient(90deg, #3B82F6, #2563EB); transition: width 0.3s ease;
}
.percent-text { font-size: 12px; color: #94A3B8; font-weight: 600; }

/* --- Dashboard --- */
.dashboard { display: flex; height: 100%; }
.sidebar { width: 280px; background: white; border-right: 1px solid #F1F5F9; display: flex; flex-direction: column; }
.sidebar-header { padding: 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F1F5F9; }
.sidebar-header h3 { font-size: 14px; font-weight: 700; color: #1A1F2E; }
.badge { background: #FFF7ED; color: #FF6B35; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.issue-list { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 8px; }
.issue-item {
  display: flex; align-items: center; padding: 12px 16px; border-radius: 12px;
  border: 1px solid transparent; background: transparent; cursor: pointer; transition: all 0.2s ease; text-align: left;
}
.issue-item:hover { background: #F8FAFC; }
.issue-item.active { background: #FFF7ED; border-color: #FFEDD5; }
.issue-rank { font-size: 12px; font-weight: 700; color: #94A3B8; width: 24px; }
.issue-item.active .issue-rank { color: #FF6B35; }
.issue-name { flex: 1; font-size: 13px; font-weight: 500; color: #475569; }
.issue-item.active .issue-name { color: #1A1F2E; font-weight: 600; }
.arrow { color: #CBD5E1; opacity: 0; transition: all 0.2s; }
.issue-item.active .arrow { opacity: 1; color: #FF6B35; }

/* --- Content Area --- */
.content-area { flex: 1; padding: 32px; overflow-y: auto; background: #F8F9FC; display: flex; flex-direction: column; gap: 24px; }

/* Analysis Selector - 2x2 Grid */
.analysis-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr) !important;
  grid-template-rows: repeat(2, auto);
  gap: 16px;
  max-width: 100%;
}

.selector-card {
  background: white;
  padding: 20px;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.04);
  display: flex;
  align-items: flex-start;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  box-shadow: 0 4px 6px rgba(0,0,0,0.01);
  min-height: 100px;
  width: 100%;
  box-sizing: border-box;
}

.selector-card:hover { 
  transform: translateY(-4px); 
  box-shadow: 0 12px 24px rgba(0,0,0,0.06);
  border-color: rgba(0,0,0,0.08);
}

.selector-card.active { 
  border: 2px solid #FF6B35; 
  background: #FFFBF7;
  box-shadow: 0 12px 24px rgba(255, 107, 53, 0.1);
}

.card-icon-wrapper { 
  width: 56px; 
  height: 56px; 
  border-radius: 16px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

.selector-card:hover .card-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.card-content {
  flex: 1;
  min-width: 0; /* For text truncation */
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.selector-name { 
  font-size: 18px; 
  font-weight: 700; 
  color: #1A1F2E; 
}

.summary-loading {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #94A3B8;
}

.selector-desc {
  font-size: 13px;
  color: #64748B;
  line-height: 1.6;
  margin: 0;
}

/* Analysis Detail */
.analysis-detail { 
  background: white; 
  border-radius: 24px; 
  padding: 32px; 
  box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  border: 1px solid rgba(0,0,0,0.04);
}

.detail-header { 
  margin-bottom: 24px; 
  border-bottom: 1px solid #F1F5F9; 
  padding-bottom: 20px; 
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.status-badge {
  background: #ECFDF5;
  color: #059669;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
}

.detail-header h3 { 
  font-size: 22px; 
  font-weight: 800; 
  color: #1A1F2E; 
}

.detail-header p { 
  font-size: 15px; 
  color: #64748B; 
}

.detail-content { flex: 1; }
.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 200px; gap: 16px; color: #64748B; font-size: 14px; }
.empty-data { text-align: center; padding: 40px; color: #94A3B8; font-size: 14px; }

/* Benchmark View */
.top-issues-card { background: #F8FAFC; border-radius: 16px; padding: 20px; margin-bottom: 24px; }
.top-issues-card h4 { font-size: 14px; font-weight: 700; color: #1A1F2E; margin-bottom: 12px; }
.tags-wrapper { display: flex; flex-wrap: wrap; gap: 8px; }
.issue-tag {
  background: white; padding: 6px 12px; border-radius: 8px; border: 1px solid #E2E8F0;
  display: flex; align-items: center; gap: 6px; font-size: 12px;
}
.issue-tag.top { background: #FF6B35; color: white; border-color: #FF6B35; }
.issue-tag .rank { font-weight: 700; opacity: 0.7; }
.issue-tag .count { background: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 4px; }
.issue-tag.top .count { background: rgba(255,255,255,0.2); }

.table-container { overflow-x: auto; border: 1px solid #E2E8F0; border-radius: 12px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { padding: 12px 16px; border-bottom: 1px solid #F1F5F9; text-align: center; white-space: nowrap; }
th { background: #F8FAFC; font-weight: 600; color: #64748B; }
.sticky-col { position: sticky; left: 0; background: inherit; z-index: 1; text-align: left; border-right: 1px solid #F1F5F9; }
.row-idx { color: #FF6B35; font-weight: 600; margin-right: 8px; }
.dot-indicator {
  display: inline-block; width: 10px; height: 10px; background: #FF6B35; border-radius: 50%;
  cursor: pointer; transition: transform 0.2s;
}
.dot-indicator:hover { transform: scale(1.4); }
.dash { color: #E2E8F0; }

/* ESG View */
.esg-header-card {
  background: #F8FAFC; border-radius: 16px; padding: 20px; margin-bottom: 24px;
  display: flex; align-items: center; gap: 12px;
}
.category-badge { padding: 4px 10px; border-radius: 6px; color: white; font-size: 11px; font-weight: 700; }
.esg-header-card h4 { font-size: 16px; font-weight: 700; color: #1A1F2E; flex: 1; }
.count-badge { font-size: 12px; color: #64748B; font-weight: 600; }
.disclosure-list { display: flex; flex-direction: column; gap: 12px; }
.disclosure-card { border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px; transition: all 0.2s; }
.disclosure-card:hover { border-color: #CBD5E1; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
.d-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.std-badge { font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.d-id { font-size: 12px; font-weight: 700; color: #1A1F2E; }
.d-title { font-size: 14px; color: #334155; margin-bottom: 4px; }
.d-desc { font-size: 12px; color: #64748B; line-height: 1.5; }

/* Media View */
.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: #F8FAFC; padding: 16px; border-radius: 12px; text-align: center; }
.stat-card.positive { background: #ECFDF5; color: #047857; }
.stat-card.negative { background: #FEF2F2; color: #B91C1C; }
.stat-card .val { display: block; font-size: 20px; font-weight: 700; margin-bottom: 4px; }
.stat-card .label { font-size: 12px; opacity: 0.8; }
.article-list { display: flex; flex-direction: column; gap: 12px; }
.article-card { border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px; cursor: pointer; transition: all 0.2s; }
.article-card:hover { border-color: #FF6B35; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
.a-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.sentiment-badge { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px; }
.date { font-size: 11px; color: #94A3B8; }
.a-title { font-size: 14px; font-weight: 600; color: #1A1F2E; margin-bottom: 12px; }
.a-footer { display: flex; justify-content: space-between; align-items: center; }
.tags { display: flex; gap: 6px; }
.tag { font-size: 10px; color: #64748B; background: #F1F5F9; padding: 2px 6px; border-radius: 4px; }

/* Modals */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(26, 31, 46, 0.6);
  backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal-card { background: white; border-radius: 24px; box-shadow: 0 24px 48px rgba(0,0,0,0.2); overflow: hidden; }
.survey-modal { width: 800px; max-height: 80vh; display: flex; flex-direction: column; }
.modal-header { padding: 24px; border-bottom: 1px solid #F1F5F9; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { font-size: 18px; font-weight: 700; color: #1A1F2E; }
.survey-content { padding: 24px; overflow-y: auto; flex: 1; }
.info-box { background: #FFF7ED; padding: 16px; border-radius: 12px; margin-bottom: 24px; color: #C2410C; font-size: 13px; }
.survey-list { display: flex; flex-direction: column; gap: 12px; }
.survey-item { display: flex; align-items: center; padding: 16px; border: 1px solid #E2E8F0; border-radius: 12px; gap: 16px; }
.survey-item .idx { width: 24px; height: 24px; background: #1A1F2E; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; }
.survey-item .name { flex: 1; font-weight: 600; color: #1A1F2E; }
.scale-group { display: flex; align-items: center; gap: 12px; }
.dots { display: flex; gap: 8px; }
.dot { width: 12px; height: 12px; border-radius: 50%; border: 1px solid #CBD5E1; }
.modal-footer { padding: 20px; border-top: 1px solid #F1F5F9; display: flex; justify-content: flex-end; }

.report-modal { width: 400px; padding: 40px; text-align: center; }
.modal-header.center { justify-content: center; flex-direction: column; border: none; padding: 0 0 24px 0; }
.icon-box.pulse { width: 64px; height: 64px; background: linear-gradient(135deg, #FF8F68, #FF6B35); border-radius: 20px; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; animation: pulse 2s infinite; }
.progress-section { margin-bottom: 24px; }
.progress-info { display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 8px; }
.progress-bar-bg { height: 8px; background: #F1F5F9; border-radius: 4px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: linear-gradient(90deg, #FF8F68, #FF6B35); transition: width 0.3s ease; }
.close-btn { width: 100%; padding: 12px; background: #1A1F2E; color: white; border-radius: 12px; font-weight: 600; }

.detail-modal { width: 400px; }
.detail-modal-header { background: #EA7F52; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; color: white; }
.detail-modal-header h3 { font-size: 16px; font-weight: 700; }
.detail-body { padding: 24px; }
.detail-row { margin-bottom: 16px; }
.detail-row label { display: block; font-size: 12px; color: #64748B; margin-bottom: 4px; }
.detail-row .val { font-size: 14px; color: #1A1F2E; font-weight: 500; }
.detail-row .val.highlight { color: #EA7F52; background: #FFF7ED; padding: 8px; border-radius: 8px; }
.page-tag { display: inline-block; padding: 4px 10px; border: 1px solid #FDBA74; color: #EA7F52; border-radius: 12px; font-size: 12px; margin-right: 6px; }

@keyframes pulse { 0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 107, 53, 0.4); } 70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(255, 107, 53, 0); } 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 107, 53, 0); } }
</style>
```
