<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Calendar, Newspaper, Plus, TrendingUp, RefreshCw } from 'lucide-vue-next';
import type { NewsItem, ScheduleItem } from '@/types';
import KeywordGraph from '@/components/charts/KeywordGraph.vue';
import WordCloud from '@/components/charts/WordCloud.vue';
import mediaApi from '@/api/media.api';
import type { EsgIssue } from '@/api/media.api';

// Constants
const EMISSION_DATA = [
  { month: 'Jan', value: 420 },
  { month: 'Feb', value: 380 },
  { month: 'Mar', value: 440 },
  { month: 'Apr', value: 390 },
  { month: 'May', value: 370 },
  { month: 'Jun', value: 350 }
];

const CREDIT_DATA = [
  { month: 'Jan', value: 120 },
  { month: 'Feb', value: 145 },
  { month: 'Mar', value: 135 },
  { month: 'Apr', value: 160 },
  { month: 'May', value: 175 },
  { month: 'Jun', value: 190 }
];

// 캐시 설정
const CACHE_KEY_KEYWORD = 'home_keyword_trend_cache';
const CACHE_KEY_NEWS = 'home_esg_news_cache';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24시간

// 기본 뉴스 데이터 (API 실패시 fallback)
const DEFAULT_NEWS: NewsItem[] = [
  { id: '1', title: 'SK, 2024년 탄소배출 30% 감축 목표 달성...친환경 투자 확대', source: '한국경제', time: '2시간 전', category: 'carbon' },
  { id: '2', title: 'EU 탄소국경세(CBAM) 본격 시행, 국내 수출기업 대응 시급', source: '매일경제', time: '5시간 전', category: 'regulation' },
  { id: '3', title: '삼성전자, RE100 이행 로드맵 발표...2030년까지 재생에너지 100% 전환', source: '조선일보', time: '1일 전', category: 're100' },
  { id: '4', title: '국내 ESG 공시 의무화 2025년 적용 예정, 대기업 준비 박차', source: '연합뉴스', time: '1일 전', category: 'esg' },
  { id: '5', title: 'CDP 한국위원회, 2024 기후변화 우수기업', source: '서울경제', time: '2일 전', category: 'esg' }
];

// 반응형 뉴스 데이터
const newsItems = ref<NewsItem[]>(DEFAULT_NEWS);
const isLoadingNews = ref(false);

// State
const scheduleView = ref<'yearly' | 'weekly' | 'daily'>('yearly');
const showAddSchedule = ref(false);

// 연간 일정 데이터 (체크박스 형태)
const yearlySchedules = ref([
  {
    id: '1',
    period: '2~4월',
    tasks: [
      { id: 'y1-1', title: '보고서 기획', completed: true },
      { id: 'y1-2', title: '국내외 벤치마킹', completed: true },
      { id: 'y1-3', title: '중대성 평가 시행', completed: true },
      { id: 'y1-4', title: '스토리라인 구성', completed: false },
      { id: 'y1-5', title: 'ESG 투자 전략', completed: false }
    ]
  },
  {
    id: '2',
    period: '4~6월',
    tasks: [
      { id: 'y2-1', title: '데이터 커버리지 충족 조건 공개', completed: false },
      { id: 'y2-2', title: '매출액, 영업이익 등 연결기준 명시', completed: false },
      { id: 'y2-3', title: 'SK 및 관계사 ESG 원고 작성', completed: false },
      { id: 'y2-4', title: '정량 정성 데이터 양식 개발 및 배포', completed: false }
    ]
  },
  {
    id: '3',
    period: '7~8월',
    tasks: [
      { id: 'y3-1', title: '디자인 완성', completed: false },
      { id: 'y3-2', title: '외부 전문가 검증', completed: false },
      { id: 'y3-3', title: '영문 번역 및 인쇄', completed: false },
      { id: 'y3-4', title: 'ESG위원회 제출', completed: false }
    ]
  },
  {
    id: '4',
    period: '9~11월',
    tasks: [
      { id: 'y4-1', title: '평가기관 대응을 위한 문항 분석', completed: false },
      { id: 'y4-2', title: '개선안 도출', completed: false },
      { id: 'y4-3', title: '자료 수집 제출', completed: false }
    ]
  }
]);

// 주간 일정 데이터 (체크박스 형태)
const weeklySchedules = ref([
  {
    id: '1',
    period: '월요일',
    tasks: [
      { id: 'w1-1', title: 'ESG 위원회 회의', completed: true },
      { id: 'w1-2', title: '회의 자료 준비', completed: true },
      { id: 'w1-3', title: '회의록 작성', completed: false }
    ]
  },
  {
    id: '2',
    period: '화요일',
    tasks: [
      { id: 'w2-1', title: '탄소배출권 거래 검토', completed: true },
      { id: 'w2-2', title: '시장 동향 분석', completed: true },
      { id: 'w2-3', title: '거래 전략 수립', completed: false }
    ]
  },
  {
    id: '3',
    period: '수요일',
    tasks: [
      { id: 'w3-1', title: '지속가능경영 보고서 작성', completed: false },
      { id: 'w3-2', title: '데이터 수집', completed: false },
      { id: 'w3-3', title: '검토 및 승인', completed: false }
    ]
  },
  {
    id: '4',
    period: '목요일',
    tasks: [
      { id: 'w4-1', title: 'RE100 이행 현황 점검', completed: false },
      { id: 'w4-2', title: '재생에너지 구매 계획', completed: false }
    ]
  },
  {
    id: '5',
    period: '금요일',
    tasks: [
      { id: 'w5-1', title: '주간 업무 보고', completed: false },
      { id: 'w5-2', title: '차주 일정 계획', completed: false }
    ]
  }
]);

// 일간 일정 데이터 (체크박스 형태)
const dailySchedules = ref([
  {
    id: '1',
    period: '오전',
    tasks: [
      { id: 'd1-1', title: '09:00 ESG 팀 미팅', completed: true },
      { id: 'd1-2', title: '10:00 탄소배출 데이터 검토', completed: true },
      { id: 'd1-3', title: '11:00 외부 미팅 준비', completed: false }
    ]
  },
  {
    id: '2',
    period: '오후',
    tasks: [
      { id: 'd2-1', title: '14:00 협력사 ESG 평가', completed: false },
      { id: 'd2-2', title: '15:30 보고서 초안 작성', completed: false },
      { id: 'd2-3', title: '17:00 일일 업무 정리', completed: false }
    ]
  }
]);

const newSchedule = ref({
  date: '',
  time: '',
  title: ''
});

// 키워드 데이터
interface KeywordNode {
  name: string;
  value: number;
  category: string;
}

const keywordGraphData = ref<KeywordNode[]>([
  { name: 'SK하이닉스', value: 45, category: 'central' },
  { name: '현대엔지니어링', value: 35, category: 'E' },
  { name: '삼성전자', value: 32, category: 'E' },
  { name: 'M15X', value: 28, category: 'G' },
  { name: '미국', value: 25, category: 'S' },
  { name: 'SK텔레콤', value: 24, category: 'G' },
  { name: 'AWS', value: 22, category: 'E' },
  { name: '하이브리드', value: 20, category: 'E' },
  { name: '엔비디아', value: 18, category: 'G' },
  { name: '경기도', value: 16, category: 'S' },
  { name: '대통령', value: 15, category: 'S' },
  { name: '기아', value: 14, category: 'E' },
  { name: '패러다임', value: 12, category: 'G' },
  { name: '검색어', value: 11, category: 'S' },
  { name: '정의선', value: 10, category: 'G' }
]);

const wordCloudData = ref<{ name: string; value: number; category?: string }[]>([
  { name: 'SK하이닉스', value: 45, category: 'E' },
  { name: '현대자동차그룹', value: 38, category: 'E' },
  { name: '패러다임', value: 32, category: 'G' },
  { name: '미국', value: 30, category: 'S' },
  { name: 'SK그룹', value: 28, category: 'G' },
  { name: '현대엔지니어링', value: 26, category: 'E' },
  { name: 'AWS', value: 24, category: 'E' },
  { name: '최태원', value: 22, category: 'G' },
  { name: '현대제철', value: 20, category: 'E' },
  { name: '대한민국', value: 19, category: 'S' },
  { name: '서울시', value: 18, category: 'S' },
  { name: '경기도', value: 17, category: 'S' },
  { name: '기아', value: 16, category: 'E' },
  { name: '서산', value: 15, category: 'S' },
  { name: 'M15X', value: 14, category: 'G' }
]);

const isLoadingKeywords = ref(false);
const totalNewsCount = ref(0);

// 캐시 유틸리티 함수
interface CacheData<T> {
  timestamp: number;
  data: T;
}

function getCache<T>(key: string): T | null {
  try {
    const cached = localStorage.getItem(key);
    if (cached) {
      const parsed: CacheData<T> = JSON.parse(cached);
      if (Date.now() - parsed.timestamp < CACHE_DURATION) {
        return parsed.data;
      }
    }
  } catch (e) {
    console.error('캐시 파싱 실패:', e);
  }
  return null;
}

function setCache<T>(key: string, data: T): void {
  const cacheData: CacheData<T> = {
    timestamp: Date.now(),
    data
  };
  localStorage.setItem(key, JSON.stringify(cacheData));
}

// HTML 태그 제거 함수
function stripHtmlTags(text: string): string {
  if (!text) return '';
  return text
    .replace(/<\/?[^>]+(>|$)/g, '')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .trim();
}

// 시간 포맷 함수
function formatTimeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  if (diffHours < 1) return '방금 전';
  if (diffHours < 24) return `${diffHours}시간 전`;
  if (diffDays < 7) return `${diffDays}일 전`;
  return `${Math.floor(diffDays / 7)}주 전`;
}

// ESG 카테고리 결정
function getEsgCategory(esgCategories: string[]): string {
  if (!esgCategories || esgCategories.length === 0) return 'esg';
  const cat = esgCategories[0];
  if (cat === 'E') return 'carbon';
  if (cat === 'S') return 'esg';
  if (cat === 'G') return 'regulation';
  return 'esg';
}

// 오늘의 ESG 뉴스 로드 (캐싱 적용)
async function loadTodayNews(forceRefresh = false) {
  // 캐시 확인
  if (!forceRefresh) {
    const cached = getCache<NewsItem[]>(CACHE_KEY_NEWS);
    if (cached) {
      newsItems.value = cached;
      console.log('오늘의 뉴스: 캐시 사용');
      return;
    }
  }

  isLoadingNews.value = true;
  try {
    const response = await mediaApi.analyzeNews({
      keywords: ['ESG', 'SK하이닉스', '탄소중립', 'RE100', '친환경'],
      maxPages: 2
    });

    if (response.articles && response.articles.length > 0) {
      // 상위 5개 뉴스 선택
      const topNews = response.articles.slice(0, 5).map((article, index) => ({
        id: String(index + 1),
        title: stripHtmlTags(article.cleanTitle || article.title),
        source: article.title.match(/\[([^\]]+)\]/)?.[1] || '뉴스',
        time: formatTimeAgo(article.pubDate),
        category: getEsgCategory(article.esgCategories)
      }));

      newsItems.value = topNews;
      setCache(CACHE_KEY_NEWS, topNews);
    }
  } catch (error) {
    console.error('오늘의 뉴스 로드 실패:', error);
    newsItems.value = DEFAULT_NEWS;
  } finally {
    isLoadingNews.value = false;
  }
}

// 키워드 트렌드 데이터 로드 (캐싱 적용)
interface KeywordCacheData {
  keywordGraph: KeywordNode[];
  wordCloud: { name: string; value: number; category?: string }[];
  totalCount: number;
}

async function refreshKeywordData(forceRefresh = false) {
  // 캐시 확인
  if (!forceRefresh) {
    const cached = getCache<KeywordCacheData>(CACHE_KEY_KEYWORD);
    if (cached) {
      keywordGraphData.value = cached.keywordGraph;
      wordCloudData.value = cached.wordCloud;
      totalNewsCount.value = cached.totalCount;
      console.log('키워드 트렌드: 캐시 사용');
      return;
    }
  }

  isLoadingKeywords.value = true;
  try {
    const response = await mediaApi.analyzeNews({
      keywords: ['SK하이닉스', 'ESG', '탄소중립', 'RE100', '친환경', '삼성전자', '현대자동차', '지속가능'],
      maxPages: 5
    });

    totalNewsCount.value = response.uniqueArticles || response.totalCollected || 0;

    if (response.statistics?.issueStatistics && response.statistics.issueStatistics.length > 0) {
      const newKeywords = response.statistics.issueStatistics.map((stat, index) => ({
        name: stat.issue,
        value: Math.max(stat.count * 5, 10),
        category: stat.esgCategory || (index === 0 ? 'central' : ['E', 'S', 'G'][index % 3])
      }));

      if (newKeywords.length > 0) {
        keywordGraphData.value = newKeywords.slice(0, 25);
        wordCloudData.value = newKeywords.slice(0, 40).map(kw => ({
          name: kw.name,
          value: kw.value,
          category: kw.category
        }));
      }

      if (response.statistics?.categoryStatistics) {
        const categoryKeywords = Object.entries(response.statistics.categoryStatistics).map(([name, count]) => ({
          name: name === 'E' ? '환경(E)' : name === 'S' ? '사회(S)' : '지배구조(G)',
          value: (count as number) * 3,
          category: name === 'E' ? 'E' : name === 'S' ? 'S' : 'G'
        }));
        wordCloudData.value = [...wordCloudData.value, ...categoryKeywords];
      }

      // 캐시 저장
      setCache<KeywordCacheData>(CACHE_KEY_KEYWORD, {
        keywordGraph: keywordGraphData.value,
        wordCloud: wordCloudData.value,
        totalCount: totalNewsCount.value
      });
    } else {
      await loadEsgIssuesData();
    }
  } catch (error) {
    console.error('키워드 데이터 로드 실패:', error);
    await loadEsgIssuesData();
  } finally {
    isLoadingKeywords.value = false;
  }
}

async function loadEsgIssuesData() {
  try {
    const response = await mediaApi.getEsgIssues();
    if (response?.data?.issues) {
      const issues: EsgIssue[] = response.data.issues;
      const graphKeywords: KeywordNode[] = [{ name: 'ESG', value: 50, category: 'central' }];

      issues.forEach((issue, index) => {
        graphKeywords.push({
          name: issue.name,
          value: 35 - index * 1.5,
          category: issue.category
        });
      });

      keywordGraphData.value = graphKeywords.slice(0, 15);

      const cloudWords: { name: string; value: number; category?: string }[] = [];
      issues.forEach((issue) => {
        issue.keywords.forEach((keyword, idx) => {
          cloudWords.push({
            name: keyword,
            value: 30 - idx * 5,
            category: issue.category
          });
        });
      });
      wordCloudData.value = cloudWords.slice(0, 30);
    }
  } catch (esgError) {
    console.error('ESG 이슈 데이터 로드 실패:', esgError);
  }
}

onMounted(() => {
  refreshKeywordData();
  loadTodayNews();
});

// Methods
function handleAddSchedule() {
  if (!newSchedule.value.date || !newSchedule.value.time || !newSchedule.value.title) return;

  const schedule: ScheduleItem = {
    id: Date.now().toString(),
    date: newSchedule.value.date,
    time: newSchedule.value.time,
    title: newSchedule.value.title,
    status: 'pending',
    progress: 0,
    view: scheduleView.value,
    tasks: []
  };

  schedules.value.push(schedule);
  newSchedule.value = { date: '', time: '', title: '' };
  showAddSchedule.value = false;
}

function getCategoryColor(category: string) {
  const colors: Record<string, string> = {
    esg: '#597EFF',
    carbon: '#10B981',
    re100: '#F59E0B',
    regulation: '#EF4444'
  };
  return colors[category] || '#6B7280';
}

function getCategoryLabel(category: string) {
  const labels: Record<string, string> = {
    esg: 'ESG',
    carbon: '탄소',
    re100: 'RE100',
    regulation: '규제'
  };
  return labels[category] || '';
}

function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    done: '#10B981',
    progress: '#F59E0B',
    pending: '#6B7280'
  };
  return colors[status] || '#6B7280';
}
</script>

<template>
  <div class="home-container">
    <!-- Main Content Area -->
    <div class="main-content">
      <!-- Top - RE100 달성현황 -->
      <div class="section">
        <h2 class="section-title">국내외 RE100 달성현황</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">국내 RE100 달성률</div>
            <div class="stat-value stat-value-primary">68%</div>
            <div class="stat-trend trend-up">
              <TrendingUp :size="16" />
              <span>+12% 전년 대비</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-label">글로벌 RE100 평균</div>
            <div class="stat-value stat-value-info">82%</div>
            <div class="stat-trend trend-up">
              <TrendingUp :size="16" />
              <span>+8% 전년 대비</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-label">SK 그룹 달성률</div>
            <div class="stat-value stat-value-success">76%</div>
            <div class="stat-trend trend-up">
              <TrendingUp :size="16" />
              <span>+15% 전년 대비</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Middle - Charts -->
      <div class="charts-grid">
        <!-- 탄소배출량 -->
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-subtitle">Carbon Emissions</div>
            <div class="chart-title">탄소배출량 추이</div>
            <div class="chart-value">
              350t <span class="chart-change trend-up">▼ 5.4%</span>
            </div>
          </div>
          <div class="chart-body">
            <div v-for="(item, index) in EMISSION_DATA" :key="index" class="chart-bar-container">
              <div
                class="chart-bar chart-bar-emission"
                :style="{ height: `${item.value / 5}px` }"
              />
              <span class="chart-bar-label">{{ item.month }}</span>
            </div>
          </div>
        </div>

        <!-- 탄소배출권 -->
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-subtitle">Carbon Credits</div>
            <div class="chart-title">탄소배출권 거래량</div>
            <div class="chart-value">
              190K <span class="chart-change trend-up">▲ 8.2%</span>
            </div>
          </div>
          <div class="chart-body">
            <div v-for="(item, index) in CREDIT_DATA" :key="index" class="chart-bar-container">
              <div
                class="chart-bar chart-bar-credit"
                :style="{ height: `${item.value}px` }"
              />
              <span class="chart-bar-label">{{ item.month }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom - News & Keywords -->
      <div class="bottom-grid">
        <!-- 오늘의 ESG 뉴스 -->
        <div class="news-card">
          <div class="card-header">
            <Newspaper class="w-5 h-5 text-primary" />
            <div class="card-title">오늘의 ESG 뉴스</div>
          </div>
          <div class="news-list">
            <div v-if="isLoadingNews" class="loading-news">
              <RefreshCw :size="20" class="animate-spin" />
              <span>뉴스 로딩 중...</span>
            </div>
            <div v-for="item in newsItems" :key="item.id" class="news-item">
              <div class="news-item-header">
                <div
                  class="news-category"
                  :style="{ background: getCategoryColor(item.category) }"
                >
                  {{ getCategoryLabel(item.category) }}
                </div>
                <div class="news-time">{{ item.time }}</div>
              </div>
              <div class="news-title">{{ item.title }}</div>
              <div class="news-source">{{ item.source }}</div>
            </div>
          </div>
        </div>

        <!-- 키워드 트렌드 분석 -->
        <div class="keyword-card">
          <div class="keyword-header">
            <div class="keyword-title-section">
              <div class="card-title">키워드 트렌드 분석</div>
              <div v-if="totalNewsCount > 0" class="news-count-badge">
                {{ totalNewsCount }}건 분석
              </div>
            </div>
            <button
              class="refresh-button"
              :disabled="isLoadingKeywords"
              @click="refreshKeywordData"
            >
              <RefreshCw :size="14" :class="{ 'animate-spin': isLoadingKeywords }" />
              <span>{{ isLoadingKeywords ? '분석 중...' : '새로고침' }}</span>
            </button>
          </div>
          <div class="keyword-chart-container">
            <div class="chart-label">🔗 관계도 분석</div>
            <KeywordGraph :keywords="keywordGraphData" height="280px" />
          </div>
          <div class="keyword-chart-container keyword-chart-small">
            <div class="chart-label">📊 연관어 분석</div>
            <WordCloud :words="wordCloudData" height="220px" />
          </div>
        </div>
      </div>
    </div>

    <!-- Right Sidebar - 업무일정 -->
    <div class="schedule-sidebar">
      <!-- Header -->
      <div class="schedule-header">
        <div class="schedule-header-top">
          <div class="schedule-header-title">
            <Calendar class="w-5 h-5 text-primary" />
            <div class="card-title">업무일정</div>
          </div>
          <button class="add-button" @click="showAddSchedule = true">
            <Plus :size="18" :stroke-width="2.5" />
          </button>
        </div>

        <!-- View Selector -->
        <div class="view-selector">
          <button
            v-for="view in ['yearly', 'weekly', 'daily'] as const"
            :key="view"
            class="view-button"
            :class="{ 'view-button-active': scheduleView === view }"
            @click="scheduleView = view"
          >
            {{ view === 'yearly' ? '연간' : view === 'weekly' ? '주간' : '일간' }}
          </button>
        </div>
      </div>

      <!-- Schedule List -->
      <div class="schedule-list">
        <!-- Add Schedule Form -->
        <div v-if="showAddSchedule" class="add-schedule-form">
          <input
            v-model="newSchedule.date"
            type="text"
            placeholder="날짜 (예: 3월 15일)"
            class="schedule-input"
          />
          <input
            v-model="newSchedule.time"
            type="text"
            placeholder="시간 (예: 09:00)"
            class="schedule-input"
          />
          <input
            v-model="newSchedule.title"
            type="text"
            placeholder="제목"
            class="schedule-input"
          />
          <div class="form-buttons">
            <button class="btn-primary" @click="handleAddSchedule">추가</button>
            <button class="btn-secondary" @click="showAddSchedule = false">취소</button>
          </div>
        </div>

        <!-- 연간 일정 뷰 (체크박스 형태) -->
        <div v-if="scheduleView === 'yearly'" class="schedule-items">
          <div v-for="schedule in yearlySchedules" :key="schedule.id" class="schedule-item">
            <div class="schedule-period-header">{{ schedule.period }}</div>
            <div class="schedule-tasks">
              <div v-for="task in schedule.tasks" :key="task.id" class="task-item">
                <div
                  class="task-checkbox"
                  :class="{ 'task-checkbox-checked': task.completed }"
                >
                  <svg v-if="task.completed" width="10" height="8" viewBox="0 0 10 8" fill="none">
                    <path
                      d="M1 4L3.5 6.5L9 1"
                      stroke="#FFFFFF"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </div>
                <div class="task-title" :class="{ 'task-completed': task.completed }">
                  {{ task.title }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 주간 일정 뷰 (체크박스 형태) -->
        <div v-else-if="scheduleView === 'weekly'" class="schedule-items">
          <div v-for="schedule in weeklySchedules" :key="schedule.id" class="schedule-item">
            <div class="schedule-period-header">{{ schedule.period }}</div>
            <div class="schedule-tasks">
              <div v-for="task in schedule.tasks" :key="task.id" class="task-item">
                <div
                  class="task-checkbox"
                  :class="{ 'task-checkbox-checked': task.completed }"
                >
                  <svg v-if="task.completed" width="10" height="8" viewBox="0 0 10 8" fill="none">
                    <path
                      d="M1 4L3.5 6.5L9 1"
                      stroke="#FFFFFF"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </div>
                <div class="task-title" :class="{ 'task-completed': task.completed }">
                  {{ task.title }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 일간 일정 뷰 (체크박스 형태) -->
        <div v-else class="schedule-items">
          <div v-for="schedule in dailySchedules" :key="schedule.id" class="schedule-item">
            <div class="schedule-period-header">{{ schedule.period }}</div>
            <div class="schedule-tasks">
              <div v-for="task in schedule.tasks" :key="task.id" class="task-item">
                <div
                  class="task-checkbox"
                  :class="{ 'task-checkbox-checked': task.completed }"
                >
                  <svg v-if="task.completed" width="10" height="8" viewBox="0 0 10 8" fill="none">
                    <path
                      d="M1 4L3.5 6.5L9 1"
                      stroke="#FFFFFF"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </div>
                <div class="task-title" :class="{ 'task-completed': task.completed }">
                  {{ task.title }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  display: flex;
  width: 100%;
  height: 100%;
  background: var(--color-background);
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg) var(--spacing-lg) var(--spacing-lg) var(--spacing-2xl);
}

/* Section */
.section {
  margin-bottom: var(--spacing-lg);
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.stat-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border);
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.stat-value {
  font-size: 36px;
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-sm);
}

.stat-value-primary {
  color: var(--color-primary-light);
}

.stat-value-info {
  color: var(--color-info);
}

.stat-value-success {
  color: var(--color-success);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-sm);
}

.trend-up {
  color: var(--color-success);
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.chart-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border);
}

.chart-header {
  margin-bottom: 20px;
}

.chart-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.chart-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.chart-value {
  font-size: 28px;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-top: var(--spacing-sm);
}

.chart-change {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
}

.chart-body {
  height: 200px;
  display: flex;
  align-items: flex-end;
  gap: var(--spacing-sm);
  padding-top: 20px;
}

.chart-bar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
}

.chart-bar {
  width: 100%;
  border-radius: var(--radius-sm);
}

.chart-bar-emission {
  background: linear-gradient(to top, #ff6b9d20, #ff6b9d);
}

.chart-bar-credit {
  background: linear-gradient(to top, #10b98120, #10b981);
}

.chart-bar-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* Bottom Grid */
.bottom-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
}

/* News Card */
.news-card,
.keyword-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.text-primary {
  color: var(--color-primary-light);
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-item {
  padding: 12px;
  border-radius: var(--radius-md);
  transition: all var(--transition-normal);
  border: 1px solid #f3f4f6;
  cursor: pointer;
}

.news-item:hover {
  background: #f9fafb;
}

.news-item-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.news-category {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 10px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-surface);
}

.news-time {
  font-size: 10px;
  color: var(--color-text-muted);
}

.news-title {
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: 4px;
  line-height: 1.5;
}

.news-source {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.loading-news {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xl);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

/* Keyword Card */
.keyword-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.keyword-title-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.news-count-badge {
  padding: 4px 10px;
  border-radius: 12px;
  background: rgba(255, 143, 104, 0.1);
  font-size: 12px;
  color: #FF8F68;
  font-weight: 500;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  font-size: 12px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.refresh-button:hover {
  background: var(--color-background);
}

.refresh-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.keyword-chart-container {
  background: var(--color-background);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  height: 320px;
  margin-bottom: var(--spacing-md);
}

.keyword-chart-small {
  height: 260px;
  margin-bottom: 0;
}

.chart-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Schedule Sidebar */
.schedule-sidebar {
  width: 340px;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100%;
}

.schedule-header {
  padding: var(--spacing-lg) 20px var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}

.schedule-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.schedule-header-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.add-button {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: var(--color-background);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary-light);
  transition: all var(--transition-normal);
}

.add-button:hover {
  background: #e8eaed;
}

.view-selector {
  display: flex;
  gap: var(--spacing-sm);
}

.view-button {
  flex: 1;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  background: var(--color-background);
  color: var(--color-text-secondary);
  transition: all var(--transition-normal);
}

.view-button-active {
  background: var(--gradient-primary);
  color: var(--color-surface);
}

/* Schedule List */
.schedule-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md) 20px;
}

.add-schedule-form {
  padding: var(--spacing-md);
  background: var(--color-background);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-md);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-input {
  width: 100%;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  background: var(--color-surface);
}

.form-buttons {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-primary,
.btn-secondary {
  flex: 1;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  transition: all var(--transition-normal);
}

.btn-primary {
  background: var(--gradient-primary);
  color: var(--color-surface);
}

.btn-secondary {
  background: #f3f4f6;
  color: var(--color-text-secondary);
}

.schedule-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-item {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 14px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.schedule-item:hover {
  box-shadow: var(--shadow-md);
}

.schedule-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
}

.schedule-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
}

.schedule-time {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.schedule-title {
  font-size: 13px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 10px;
  line-height: 1.4;
}

.schedule-tasks {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.task-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.task-checkbox {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-sm);
  border: 2px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--transition-normal);
}

.task-checkbox-checked {
  border-color: transparent;
  background: #10B981;
}

.task-title {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.task-completed {
  color: var(--color-text-muted);
  text-decoration: line-through;
}

/* Schedule Period Header */
.schedule-period-header {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary-light);
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}
</style>
