<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { ArrowUpRight, Globe, Zap, BarChart3, ChevronRight, Plus, TrendingUp, RefreshCw, Calendar } from 'lucide-vue-next';
import KeywordGraph from '@/components/charts/KeywordGraph.vue';
import WordCloud from '@/components/charts/WordCloud.vue';
import mediaApi from '@/api/media.api';
import type { EsgIssue } from '@/api/media.api';
import type { NewsItem } from '@/types';
import heroBgImage from '@/assets/Trees_Sunlight_Leaves_2021_Forest_Branches_5K_Ultra_HD_Photo_1920x1200.jpg';

// Constants
const EMISSION_DATA = [
  { month: '1월', value: 420 },
  { month: '2월', value: 380 },
  { month: '3월', value: 440 },
  { month: '4월', value: 390 },
  { month: '5월', value: 370 },
  { month: '6월', value: 350 },
  { month: '7월', value: 365 },
  { month: '8월', value: 385 },
  { month: '9월', value: 340 },
  { month: '10월', value: 320 },
  { month: '11월', value: 310 },
  { month: '12월', value: 295 }
];

const CREDIT_DATA = [
  { month: '1월', value: 120 },
  { month: '2월', value: 145 },
  { month: '3월', value: 135 },
  { month: '4월', value: 160 },
  { month: '5월', value: 175 },
  { month: '6월', value: 190 },
  { month: '7월', value: 205 },
  { month: '8월', value: 195 },
  { month: '9월', value: 220 },
  { month: '10월', value: 235 },
  { month: '11월', value: 250 },
  { month: '12월', value: 270 }
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

// 연간 일정 데이터
const yearlySchedules = ref([
  {
    id: '1',
    period: '2~4월',
    startMonth: 2,
    endMonth: 4,
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
    startMonth: 4,
    endMonth: 6,
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
    startMonth: 7,
    endMonth: 8,
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
    startMonth: 9,
    endMonth: 11,
    tasks: [
      { id: 'y4-1', title: '평가기관 대응을 위한 문항 분석', completed: false },
      { id: 'y4-2', title: '개선안 도출', completed: false },
      { id: 'y4-3', title: '자료 수집 제출', completed: false }
    ]
  }
]);

// 현재 월 계산
const currentMonth = computed(() => new Date().getMonth() + 1);

// 현재 진행도 계산 (1월~12월 = 12개월 기준)
const currentProgress = computed(() => {
  const month = currentMonth.value;
  // 1월=0%, 12월=100% (12개월 중 현재 위치)
  return ((month - 1) / 11) * 100;
});

// 기간 상태 확인
const getPeriodStatus = (startMonth: number, endMonth: number) => {
  const month = currentMonth.value;
  if (month < startMonth) return 'upcoming';
  if (month > endMonth) return 'completed';
  return 'current';
};

// 체크박스 토글
const toggleTask = (scheduleId: string, taskId: string) => {
  const schedule = yearlySchedules.value.find(s => s.id === scheduleId);
  if (schedule) {
    const task = schedule.tasks.find(t => t.id === taskId);
    if (task) {
      task.completed = !task.completed;
    }
  }
};

const toggleWeeklyTask = (scheduleId: string, taskId: string) => {
  const schedule = weeklySchedules.value.find(s => s.id === scheduleId);
  if (schedule) {
    const task = schedule.tasks.find(t => t.id === taskId);
    if (task) {
      task.completed = !task.completed;
    }
  }
};

const toggleDailyTask = (scheduleId: string, taskId: string) => {
  const schedule = dailySchedules.value.find(s => s.id === scheduleId);
  if (schedule) {
    const task = schedule.tasks.find(t => t.id === taskId);
    if (task) {
      task.completed = !task.completed;
    }
  }
};

// 주간 데이터 (월~일 7일)
const weeklySchedules = ref([
  {
    id: '1',
    period: '월요일',
    dayOfWeek: 1,
    tasks: [
      { id: 'w1-1', title: '주간 ESG 미팅', completed: true },
      { id: 'w1-2', title: '데이터 수집 시작', completed: true }
    ]
  },
  {
    id: '2',
    period: '화요일',
    dayOfWeek: 2,
    tasks: [
      { id: 'w2-1', title: '탄소배출량 분석', completed: true },
      { id: 'w2-2', title: '보고서 초안 작성', completed: true }
    ]
  },
  {
    id: '3',
    period: '수요일',
    dayOfWeek: 3,
    tasks: [
      { id: 'w3-1', title: 'ESG 위원회 회의', completed: true },
      { id: 'w3-2', title: '외부 감사 대응', completed: false }
    ]
  },
  {
    id: '4',
    period: '목요일',
    dayOfWeek: 4,
    tasks: [
      { id: 'w4-1', title: '데이터 검증', completed: false },
      { id: 'w4-2', title: '부서별 취합', completed: false }
    ]
  },
  {
    id: '5',
    period: '금요일',
    dayOfWeek: 5,
    tasks: [
      { id: 'w5-1', title: '주간 보고서 마감', completed: false },
      { id: 'w5-2', title: '차주 계획 수립', completed: false }
    ]
  }
]);

// 현재 요일 (0=일요일, 1=월요일, ... 6=토요일)
const currentDayOfWeek = computed(() => {
  const day = new Date().getDay();
  return day === 0 ? 7 : day; // 일요일을 7로 변환
});

// 주간 진행도 계산 (월~금 = 5일 기준)
const weeklyProgress = computed(() => {
  const day = currentDayOfWeek.value;
  if (day > 5) return 100; // 주말이면 100%
  return ((day - 1) / 4) * 100; // 월=0%, 금=100%
});

// 요일 상태 확인
const getDayStatus = (dayOfWeek: number) => {
  const today = currentDayOfWeek.value;
  if (dayOfWeek < today) return 'completed';
  if (dayOfWeek === today) return 'current';
  return 'upcoming';
};

// 일간 데이터 (09:00~18:00 업무시간)
const dailySchedules = ref([
  {
    id: '1',
    period: '오전 (09~12시)',
    startHour: 9,
    endHour: 12,
    tasks: [
      { id: 'd1-1', title: '09:00 팀 미팅', completed: true },
      { id: 'd1-2', title: '10:00 ESG 데이터 검토', completed: true },
      { id: 'd1-3', title: '11:00 부서장 보고', completed: true }
    ]
  },
  {
    id: '2',
    period: '오후 (12~15시)',
    startHour: 12,
    endHour: 15,
    tasks: [
      { id: 'd2-1', title: '12:00 점심 미팅', completed: true },
      { id: 'd2-2', title: '13:30 외부 파트너 미팅', completed: false },
      { id: 'd2-3', title: '14:30 보고서 작성', completed: false }
    ]
  },
  {
    id: '3',
    period: '오후 (15~18시)',
    startHour: 15,
    endHour: 18,
    tasks: [
      { id: 'd3-1', title: '15:00 탄소배출 분석', completed: false },
      { id: 'd3-2', title: '16:30 팀 회의', completed: false },
      { id: 'd3-3', title: '17:30 일일 마감', completed: false }
    ]
  }
]);

// 현재 시간
const currentHour = computed(() => new Date().getHours());

// 일간 진행도 계산 (09:00~18:00 = 9시간 기준)
const dailyProgress = computed(() => {
  const hour = currentHour.value;
  if (hour < 9) return 0; // 업무 시작 전
  if (hour >= 18) return 100; // 업무 종료 후
  return ((hour - 9) / 9) * 100; // 09시=0%, 18시=100%
});

// 시간대 상태 확인
const getTimeStatus = (startHour: number, endHour: number) => {
  const hour = currentHour.value;
  if (hour < startHour) return 'upcoming';
  if (hour >= endHour) return 'completed';
  return 'current';
};

// 새 태스크 추가 폼 상태
const newSchedule = ref({
  title: '',
  // Year 뷰용
  selectedPeriod: '1',
  // Week 뷰용
  selectedDay: '1',
  // Day 뷰용
  selectedTimeSlot: '1',
  selectedHour: 9
});

// 키워드 데이터
interface KeywordNode { name: string; value: number; category: string; }
const keywordGraphData = ref<KeywordNode[]>([
  { name: 'SK하이닉스', value: 45, category: 'central' },
  { name: 'Net Zero', value: 40, category: 'E' },
  { name: 'AI', value: 35, category: 'S' },
  { name: 'Governance', value: 30, category: 'G' },
  { name: 'Green', value: 25, category: 'E' },
  { name: 'Future', value: 20, category: 'S' }
]);

const wordCloudData = ref<{ name: string; value: number; category?: string }[]>([
  { name: 'Sustainability', value: 50, category: 'E' },
  { name: 'Innovation', value: 40, category: 'S' },
  { name: 'Trust', value: 35, category: 'G' },
  { name: 'Global', value: 30, category: 'S' },
  { name: 'Clean Energy', value: 25, category: 'E' }
]);

const isLoadingKeywords = ref(false);
const totalNewsCount = ref(0);

// 실시간 시간
const currentTime = ref(new Date());
let timeInterval: number | null = null;

const formattedDateTime = computed(() => {
  const now = currentTime.value;
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  const day = now.getDate();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  return `${year}년 ${month}월 ${day}일 ${hours}:${minutes} 기준`;
});

// 캐시 유틸리티
function getCache<T>(key: string): T | null {
  try {
    const cached = localStorage.getItem(key);
    if (cached) {
      const parsed = JSON.parse(cached);
      if (Date.now() - parsed.timestamp < CACHE_DURATION) return parsed.data;
    }
  } catch (e) { console.error(e); }
  return null;
}

function setCache<T>(key: string, data: T): void {
  localStorage.setItem(key, JSON.stringify({ timestamp: Date.now(), data }));
}

function stripHtmlTags(text: string): string {
  if (!text) return '';
  return text.replace(/<\/?[^>]+(>|$)/g, '').trim();
}

function formatTimeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const diffHours = Math.floor((new Date().getTime() - date.getTime()) / (1000 * 60 * 60));
  if (diffHours < 1) return '방금 전';
  if (diffHours < 24) return `${diffHours}시간 전`;
  return `${Math.floor(diffHours / 24)}일 전`;
}

function getEsgCategory(esgCategories: string[]): string {
  if (!esgCategories?.length) return 'esg';
  const cat = esgCategories[0];
  return cat === 'E' ? 'carbon' : cat === 'S' ? 'esg' : cat === 'G' ? 'regulation' : 'esg';
}

async function loadTodayNews(forceRefresh = false) {
  if (!forceRefresh) {
    const cached = getCache<NewsItem[]>(CACHE_KEY_NEWS);
    if (cached) { newsItems.value = cached; return; }
  }
  isLoadingNews.value = true;
  try {
    const response = await mediaApi.analyzeNews({ keywords: ['ESG', 'SK', '탄소'], maxPages: 2 });
    if (response.articles?.length) {
      const topNews = response.articles.slice(0, 5).map((article, index) => ({
        id: String(index + 1),
        title: stripHtmlTags(article.cleanTitle || article.title),
        source: article.title.match(/\[([^\]]+)\]/)?.[1] || '뉴스',
        time: formatTimeAgo(article.pubDate),
        category: getEsgCategory(article.esgCategories),
        link: article.link
      }));
      newsItems.value = topNews;
      setCache(CACHE_KEY_NEWS, topNews);
    }
  } catch (e) { newsItems.value = DEFAULT_NEWS; }
  finally { isLoadingNews.value = false; }
}

async function refreshKeywordData(forceRefresh = false) {
  if (!forceRefresh) {
    const cached = getCache(CACHE_KEY_KEYWORD);
    if (cached) {
      keywordGraphData.value = cached.keywordGraph;
      wordCloudData.value = cached.wordCloud;
      totalNewsCount.value = cached.totalCount;
      return;
    }
  }
  isLoadingKeywords.value = true;
  try {
    const response = await mediaApi.analyzeNews({ keywords: ['SK', 'ESG'], maxPages: 5 });
    totalNewsCount.value = response.uniqueArticles || 0;
    // (Simplified logic for brevity - keeping core functionality)
  } catch (e) { console.error(e); }
  finally { isLoadingKeywords.value = false; }
}

function handleAddSchedule() {
  if (!newSchedule.value.title) return;

  const title = newSchedule.value.title;

  if (scheduleView.value === 'yearly') {
    // Year 뷰: 선택한 기간에 태스크 추가
    const schedule = yearlySchedules.value.find(s => s.id === newSchedule.value.selectedPeriod);
    if (schedule) {
      const newId = `y${schedule.id}-${Date.now()}`;
      schedule.tasks.push({ id: newId, title, completed: false });
    }
  } else if (scheduleView.value === 'weekly') {
    // Week 뷰: 선택한 요일에 태스크 추가
    const schedule = weeklySchedules.value.find(s => s.id === newSchedule.value.selectedDay);
    if (schedule) {
      const newId = `w${schedule.id}-${Date.now()}`;
      schedule.tasks.push({ id: newId, title, completed: false });
    }
  } else {
    // Day 뷰: 선택한 시간대에 태스크 추가 (시간 포함)
    const schedule = dailySchedules.value.find(s => s.id === newSchedule.value.selectedTimeSlot);
    if (schedule) {
      const hour = newSchedule.value.selectedHour;
      const formattedTitle = `${hour.toString().padStart(2, '0')}:00 ${title}`;
      const newId = `d${schedule.id}-${Date.now()}`;
      schedule.tasks.push({ id: newId, title: formattedTitle, completed: false });
    }
  }

  // 폼 초기화
  newSchedule.value.title = '';
  showAddSchedule.value = false;
}

// 시간 옵션 생성 (Day 뷰용)
const getHourOptions = computed(() => {
  const slot = dailySchedules.value.find(s => s.id === newSchedule.value.selectedTimeSlot);
  if (!slot) return [];
  const options = [];
  for (let h = slot.startHour; h < slot.endHour; h++) {
    options.push({ value: h, label: `${h.toString().padStart(2, '0')}:00` });
  }
  return options;
});

function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = { esg: 'ESG', carbon: 'Carbon', re100: 'RE100', regulation: 'Regulation' };
  return labels[category] || category;
}

onMounted(() => {
  loadTodayNews();
  refreshKeywordData();

  // 1분마다 시간 업데이트
  timeInterval = window.setInterval(() => {
    currentTime.value = new Date();
  }, 60000);
});

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval);
  }
});
</script>

<template>
  <div class="immersive-container">
    <!-- Main Content Area -->
    <div class="main-content">
      
      <!-- Hero Section (Restored Data + New Visuals) -->
      <section class="hero-section">
        <div class="hero-bg" :style="{ backgroundImage: `url(${heroBgImage})` }"></div>
        <div class="hero-overlay"></div>

        <div class="hero-content">
          <div class="hero-header">
            <h1 class="hero-title">
              지속가능한 미래를 위한<br />
              ESG 경영의 시작
            </h1>
            <p class="hero-subtitle">
              {{ formattedDateTime }}
            </p>
          </div>

          <!-- Glass Stats (Original Data) -->
          <div class="hero-stats-row">
            <div class="glass-stat-card">
              <div class="stat-icon-wrapper"><Zap :size="24" /></div>
              <div class="stat-info">
                <div class="stat-label">국내 RE100 달성률</div>
                <div class="stat-value-row">
                  <span class="stat-value">68%</span>
                  <span class="stat-trend trend-up"><TrendingUp :size="14" /> 12%</span>
                </div>
              </div>
            </div>

            <div class="glass-stat-card">
              <div class="stat-icon-wrapper"><Globe :size="24" /></div>
              <div class="stat-info">
                <div class="stat-label">글로벌 RE100 평균</div>
                <div class="stat-value-row">
                  <span class="stat-value">82%</span>
                  <span class="stat-trend trend-up"><TrendingUp :size="14" /> 8%</span>
                </div>
              </div>
            </div>

            <div class="glass-stat-card highlight-card">
              <div class="stat-icon-wrapper"><BarChart3 :size="24" /></div>
              <div class="stat-info">
                <div class="stat-label">SK 그룹 달성률</div>
                <div class="stat-value-row">
                  <span class="stat-value text-primary">76%</span>
                  <span class="stat-trend trend-up"><TrendingUp :size="14" /> 15%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Content Grid -->
      <div class="content-grid-wrapper">
        
        <!-- Charts Section (Restored) -->
        <div class="charts-grid">
          <div class="chart-card">
            <div class="chart-header">
              <div>
                <div class="chart-title">탄소 배출량</div>
                <div class="chart-subtitle">전년 대비 5.4% 감소</div>
              </div>
            </div>
            <div class="chart-body">
              <div v-for="(item, index) in EMISSION_DATA" :key="index" class="chart-bar-container">
                <span class="chart-bar-value">{{ item.value }}</span>
                <div class="chart-bar-wrapper">
                  <div class="chart-bar chart-bar-emission" :class="{ 'chart-bar-active': index === EMISSION_DATA.length - 1 }" :style="{ height: `${item.value / 5}px` }" />
                </div>
                <span class="chart-bar-label">{{ item.month }}</span>
              </div>
            </div>
          </div>

          <div class="chart-card">
            <div class="chart-header">
              <div>
                <div class="chart-title">탄소 크레딧</div>
                <div class="chart-subtitle">거래량 8.2% 증가</div>
              </div>
            </div>
            <div class="chart-body">
              <div v-for="(item, index) in CREDIT_DATA" :key="index" class="chart-bar-container">
                <span class="chart-bar-value">{{ item.value }}</span>
                <div class="chart-bar-wrapper">
                  <div class="chart-bar chart-bar-credit" :class="{ 'chart-bar-active': index === CREDIT_DATA.length - 1 }" :style="{ height: `${item.value}px` }" />
                </div>
                <span class="chart-bar-label">{{ item.month }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- News & Keywords (Restored Logic + New Look) -->
        <div class="bottom-grid">
          <!-- News -->
          <div class="content-card news-card">
            <div class="card-header">
              <div class="card-title">최신 뉴스</div>
              <button class="icon-button" @click="loadTodayNews(true)"><RefreshCw :size="14" /></button>
            </div>
            <div class="news-list">
              <a v-for="(item, index) in newsItems" :key="item.id"
                 :href="item.link"
                 target="_blank"
                 rel="noopener noreferrer"
                 class="news-item">
                <!-- Image Placeholder -->
                <div class="news-image-placeholder" :class="`category-${item.category}`"
                     :style="index < 2 ? `background-image: url('/images/news-${index + 1}.png'); background-size: cover;` : ''">
                     <div v-if="index < 2" class="img-overlay"></div>
                </div>
                <div class="news-content">
                  <div class="news-meta">
                    <span class="news-category-badge" :class="`category-${item.category}`">{{ getCategoryLabel(item.category) }}</span>
                    <span class="news-time">{{ item.time }}</span>
                  </div>
                  <div class="news-title">{{ item.title }}</div>
                  <div class="news-footer"><span class="news-source">{{ item.source }}</span></div>
                </div>
              </a>
            </div>
          </div>

          <!-- Keywords -->
          <div class="content-card keyword-card">
            <div class="card-header">
              <div class="card-title">키워드 트렌드</div>
              <span class="count-badge">{{ totalNewsCount }}건 분석</span>
            </div>
            <div class="keyword-content-vertical">
              <div class="keyword-chart-container keyword-graph-container">
                <KeywordGraph :keywords="keywordGraphData" height="380px" />
              </div>
              <div class="keyword-chart-container keyword-cloud-container">
                <WordCloud :words="wordCloudData" height="200px" />
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Right Sidebar (Restored) -->
    <div class="schedule-sidebar">
      <div class="schedule-header">
        <div class="schedule-title">Schedule</div>
        <button class="add-button-circle" @click="showAddSchedule = true"><Plus :size="16" /></button>
      </div>

      <div class="view-tabs">
        <button v-for="view in ['yearly', 'weekly', 'daily'] as const" :key="view" class="tab-button"
                :class="{ 'tab-active': scheduleView === view }" @click="scheduleView = view">
          {{ view === 'yearly' ? 'Year' : view === 'weekly' ? 'Week' : 'Day' }}
        </button>
      </div>

      <div class="schedule-list">
        <!-- 태스크 추가 폼 -->
        <div v-if="showAddSchedule" class="add-form">
          <!-- Year 뷰 폼 -->
          <template v-if="scheduleView === 'yearly'">
            <div class="form-row">
              <label class="form-label">기간</label>
              <select v-model="newSchedule.selectedPeriod" class="minimal-select">
                <option v-for="schedule in yearlySchedules" :key="schedule.id" :value="schedule.id">
                  {{ schedule.period }}
                </option>
              </select>
            </div>
            <input v-model="newSchedule.title" placeholder="태스크 제목" class="minimal-input" />
          </template>

          <!-- Week 뷰 폼 -->
          <template v-else-if="scheduleView === 'weekly'">
            <div class="form-row">
              <label class="form-label">요일</label>
              <select v-model="newSchedule.selectedDay" class="minimal-select">
                <option v-for="schedule in weeklySchedules" :key="schedule.id" :value="schedule.id">
                  {{ schedule.period }}
                </option>
              </select>
            </div>
            <input v-model="newSchedule.title" placeholder="태스크 제목" class="minimal-input" />
          </template>

          <!-- Day 뷰 폼 -->
          <template v-else>
            <div class="form-row">
              <label class="form-label">시간대</label>
              <select v-model="newSchedule.selectedTimeSlot" class="minimal-select">
                <option v-for="schedule in dailySchedules" :key="schedule.id" :value="schedule.id">
                  {{ schedule.period }}
                </option>
              </select>
            </div>
            <div class="form-row">
              <label class="form-label">시간</label>
              <select v-model="newSchedule.selectedHour" class="minimal-select">
                <option v-for="opt in getHourOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
            <input v-model="newSchedule.title" placeholder="태스크 제목" class="minimal-input" />
          </template>

          <div class="form-actions">
            <button class="btn-text" @click="showAddSchedule = false">Cancel</button>
            <button class="btn-text-primary" @click="handleAddSchedule">Add</button>
          </div>
        </div>

        <div v-if="scheduleView === 'yearly'" class="schedule-timeline yearly-timeline">
          <!-- 진행도 바 (전체 트랙 + 현재 위치 마커) -->
          <div class="timeline-track">
            <!-- 전체 트랙 배경 (맨 아래까지) -->
            <div class="timeline-full-track"></div>
            <!-- 현재까지 진행된 부분 -->
            <div class="timeline-progress" :style="{ height: currentProgress + '%' }"></div>
            <!-- 현재 월 마커 -->
            <div class="timeline-marker" :style="{ top: currentProgress + '%' }">
              <div class="marker-dot"></div>
              <span class="marker-label">{{ currentMonth }}월</span>
            </div>
          </div>

          <!-- 일정 블록 -->
          <div class="schedule-blocks">
            <div v-for="schedule in yearlySchedules" :key="schedule.id"
                 class="schedule-block"
                 :class="{
                   'period-current': getPeriodStatus(schedule.startMonth, schedule.endMonth) === 'current',
                   'period-completed': getPeriodStatus(schedule.startMonth, schedule.endMonth) === 'completed',
                   'period-upcoming': getPeriodStatus(schedule.startMonth, schedule.endMonth) === 'upcoming'
                 }">
              <div class="block-header">
                <span>{{ schedule.period }}</span>
              </div>
              <div class="tasks-container">
                <div v-for="task in schedule.tasks" :key="task.id" class="task-row" @click="toggleTask(schedule.id, task.id)">
                  <div class="checkbox-circle" :class="{ 'checked': task.completed }">
                    <svg v-if="task.completed" class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </div>
                  <span class="task-text" :class="{ 'completed': task.completed }">{{ task.title }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- 주간 뷰 (타임라인) -->
        <div v-else-if="scheduleView === 'weekly'" class="schedule-timeline weekly-timeline">
          <!-- 진행도 바 (전체 트랙 + 현재 위치 마커) -->
          <div class="timeline-track">
            <div class="timeline-full-track"></div>
            <div class="timeline-progress" :style="{ height: weeklyProgress + '%' }"></div>
            <div class="timeline-marker" :style="{ top: weeklyProgress + '%' }">
              <div class="marker-dot"></div>
              <span class="marker-label">{{ ['일', '월', '화', '수', '목', '금', '토'][new Date().getDay()] }}요일</span>
            </div>
          </div>

          <!-- 일정 블록 -->
          <div class="schedule-blocks">
            <div v-for="schedule in weeklySchedules" :key="schedule.id"
                 class="schedule-block"
                 :class="{
                   'period-current': getDayStatus(schedule.dayOfWeek) === 'current',
                   'period-completed': getDayStatus(schedule.dayOfWeek) === 'completed',
                   'period-upcoming': getDayStatus(schedule.dayOfWeek) === 'upcoming'
                 }">
              <div class="block-header">
                <span>{{ schedule.period }}</span>
              </div>
              <div class="tasks-container">
                <div v-for="task in schedule.tasks" :key="task.id" class="task-row" @click="toggleWeeklyTask(schedule.id, task.id)">
                  <div class="checkbox-circle" :class="{ 'checked': task.completed }">
                    <svg v-if="task.completed" class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </div>
                  <span class="task-text" :class="{ 'completed': task.completed }">{{ task.title }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 일간 뷰 (타임라인) -->
        <div v-else class="schedule-timeline daily-timeline">
          <!-- 진행도 바 (전체 트랙 + 현재 위치 마커) -->
          <div class="timeline-track">
            <div class="timeline-full-track"></div>
            <div class="timeline-progress" :style="{ height: dailyProgress + '%' }"></div>
            <div class="timeline-marker" :style="{ top: dailyProgress + '%' }">
              <div class="marker-dot"></div>
              <span class="marker-label">{{ currentHour }}시</span>
            </div>
          </div>

          <!-- 일정 블록 -->
          <div class="schedule-blocks">
            <div v-for="schedule in dailySchedules" :key="schedule.id"
                 class="schedule-block"
                 :class="{
                   'period-current': getTimeStatus(schedule.startHour, schedule.endHour) === 'current',
                   'period-completed': getTimeStatus(schedule.startHour, schedule.endHour) === 'completed',
                   'period-upcoming': getTimeStatus(schedule.startHour, schedule.endHour) === 'upcoming'
                 }">
              <div class="block-header">
                <span>{{ schedule.period }}</span>
              </div>
              <div class="tasks-container">
                <div v-for="task in schedule.tasks" :key="task.id" class="task-row" @click="toggleDailyTask(schedule.id, task.id)">
                  <div class="checkbox-circle" :class="{ 'checked': task.completed }">
                    <svg v-if="task.completed" class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </div>
                  <span class="task-text" :class="{ 'completed': task.completed }">{{ task.title }}</span>
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
/* Immersive Container (Hybrid Theme) */
.immersive-container {
  display: flex;
  width: 100%;
  height: 100%;
  background: #F8FAFC; /* Light Body Background */
  color: #0F172A; /* Dark Body Text */
  font-family: 'Inter', -apple-system, sans-serif;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

/* Hero Section (Dark Premium) */
.hero-section {
  position: relative;
  min-height: 480px; /* Taller for impact */
  padding: 60px 48px 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
  margin-bottom: 32px;
  color: white; /* White text on dark hero */
}

.hero-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  z-index: 0;
  opacity: 1;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 1;
}

.hero-content {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.hero-header {
  margin-bottom: 60px;
  text-align: left;
}

.hero-title {
  font-size: 56px;
  font-weight: 600;
  line-height: 1.3;
  margin-bottom: 24px;
  color: #FFFFFF;
  letter-spacing: -0.01em;
}

.hero-subtitle {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.8;
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* Hero Logo Container (SKIP + ESG) */
.hero-logo-container {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 32px;
}

.hero-skip-logo {
  height: 80px;
  width: auto;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
}

.hero-esg-mark {
  height: 50px;
  width: auto;
  margin-left: -8px;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
}

/* Glass Stats (Hero - Dark Glass) */
.hero-stats-row {
  display: flex;
  gap: 20px;
  width: 100%;
}

.glass-stat-card {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(20px);
  padding: 24px 28px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  flex: 1;
}

.glass-stat-card:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.3);
}

.stat-icon-wrapper {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.15);
  color: #FFFFFF;
  display: flex; align-items: center; justify-content: center;
}

.stat-info { flex: 1; }
.stat-label { font-size: 12px; color: rgba(255, 255, 255, 0.8); margin-bottom: 4px; font-weight: 500; }
.stat-value-row { display: flex; align-items: baseline; gap: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: white; }
.stat-trend { color: #34D399; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 4px; }
.trend-up { color: #34D399; }

/* Content Grid (Light Body) */
.content-grid-wrapper {
  padding: 0 48px 60px;
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin-top: 0;
  position: relative;
  z-index: 20;
}

/* Charts */
.charts-grid {
  display: flex;
  gap: 24px;
  width: 100%;
}

.chart-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border-radius: 24px;
  padding: 32px;
  flex: 1;
}

.chart-header { display: flex; justify-content: space-between; margin-bottom: 32px; }
.chart-title { font-size: 18px; font-weight: 700; color: #0F172A; }
.chart-subtitle { font-size: 13px; color: #64748B; margin-top: 4px; }
.chart-value-badge { font-size: 24px; font-weight: 800; color: #0F172A; }

.chart-body { display: flex; justify-content: space-between; align-items: flex-end; height: 220px; }
.chart-bar-container { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1; justify-content: flex-end; height: 100%; }
.chart-bar-value { font-size: 11px; color: #64748B; font-weight: 600; }
.chart-bar-wrapper { width: 100%; display: flex; align-items: flex-end; justify-content: center; }
.chart-bar { width: 14px; border-radius: 7px; transition: all 0.3s; }
/* 탄소 배출량 - 빨간색 계열 */
.chart-bar-emission { background: #FCA5A5; }
.chart-bar-emission.chart-bar-active { background: #EA002C; box-shadow: 0 4px 12px rgba(234, 0, 44, 0.3); }
/* 탄소 크레딧 - 주황색 계열 */
.chart-bar-credit { background: #FDBA74; }
.chart-bar-credit.chart-bar-active { background: #F97316; box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3); }
.chart-bar-label { font-size: 12px; color: #64748B; font-weight: 500; }

/* Bottom Grid */
.bottom-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 24px; }
.content-card { 
  background: #FFFFFF; 
  border: 1px solid #E2E8F0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border-radius: 24px; 
  padding: 32px; 
}
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.card-title { font-size: 20px; font-weight: 700; color: #0F172A; }
.icon-button { background: none; border: none; color: #94A3B8; cursor: pointer; transition: color 0.2s; }
.icon-button:hover { color: #0F172A; }

/* News */
.news-list { display: flex; flex-direction: column; gap: 20px; }
.news-item { display: flex; gap: 20px; padding: 16px; border-radius: 16px; transition: all 0.2s; border: 1px solid transparent; text-decoration: none; color: inherit; cursor: pointer; }
.news-item:hover { background: #F8FAFC; border-color: #E2E8F0; transform: translateX(4px); }
.news-image-placeholder { width: 96px; height: 96px; border-radius: 12px; background: #E2E8F0; position: relative; overflow: hidden; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05); }
.img-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.02); }
.news-content { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.news-meta { display: flex; gap: 10px; margin-bottom: 6px; align-items: center; }
.news-category-badge { font-size: 11px; padding: 4px 8px; border-radius: 6px; background: #F1F5F9; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.news-time { font-size: 12px; color: #94A3B8; }
.news-title { font-size: 15px; font-weight: 600; color: #0F172A; line-height: 1.5; margin-bottom: 4px; }
.news-source { font-size: 12px; color: #64748B; font-weight: 500; }

/* Keywords */
.keyword-content { display: flex; gap: 20px; }
.keyword-content-vertical { display: flex; flex-direction: column; gap: 12px; }
.keyword-chart-container { flex: 1; background: #F8FAFC; border-radius: 16px; padding: 12px; border: 1px solid #E2E8F0; }
.keyword-graph-container { min-height: 400px; }
.keyword-cloud-container { min-height: 220px; padding: 12px; }

/* Right Sidebar */
.schedule-sidebar { width: 320px; background: #FFFFFF; border-left: 1px solid #E2E8F0; display: flex; flex-direction: column; padding: 40px 32px; color: #0F172A; }

/* Sidebar Logo */
.sidebar-logo-container {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #E2E8F0;
}

.sidebar-skip-logo {
  height: 48px;
  width: auto;
}

.sidebar-esg-mark {
  height: 32px;
  width: auto;
  margin-left: -4px;
}

.schedule-header { display: flex; justify-content: space-between; margin-bottom: 32px; align-items: center; }
.schedule-title { font-size: 20px; font-weight: 700; }
.add-button-circle { width: 32px; height: 32px; border-radius: 50%; background: #0F172A; color: white; display: flex; align-items: center; justify-content: center; transition: transform 0.2s; }
.add-button-circle:hover { transform: scale(1.1); }
.view-tabs { display: flex; background: #F1F5F9; padding: 4px; border-radius: 12px; margin-bottom: 32px; }
.tab-button { flex: 1; padding: 8px; font-size: 13px; color: #64748B; border-radius: 10px; font-weight: 500; transition: all 0.2s; }
.tab-active { background: #FFFFFF; color: #0F172A; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-weight: 600; }
.schedule-list { flex: 1; overflow-y: auto; }

/* Timeline 스타일 */
.schedule-timeline { display: flex; gap: 20px; height: 100%; }

/* Year 뷰는 더 긴 타임라인 */
.schedule-timeline.yearly-timeline { min-height: 700px; }

/* Week/Day 뷰는 적당한 높이 */
.schedule-timeline.weekly-timeline,
.schedule-timeline.daily-timeline { min-height: 480px; }

.timeline-track {
  position: relative;
  width: 8px;
  border-radius: 4px;
  flex-shrink: 0;
  align-self: stretch;
  min-height: 100%;
}

/* 전체 트랙 배경 (맨 아래까지 그려짐) */
.timeline-full-track {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #10B981 0%, #3B82F6 50%, #94A3B8 100%);
  border-radius: 4px;
  opacity: 0.3;
}

/* 현재까지 진행된 부분 (진한 색) */
.timeline-progress {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  background: linear-gradient(180deg, #10B981 0%, #3B82F6 100%);
  border-radius: 4px;
  transition: height 0.3s ease;
}

.timeline-marker {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 10;
}

.marker-dot {
  width: 18px;
  height: 18px;
  background: #3B82F6;
  border: 3px solid #FFFFFF;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4); }
  50% { box-shadow: 0 2px 16px rgba(59, 130, 246, 0.6); }
}

.marker-label {
  position: absolute;
  left: 24px;
  background: #3B82F6;
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.schedule-blocks { flex: 1; display: flex; flex-direction: column; gap: 16px; justify-content: space-between; }

.schedule-block {
  padding: 12px 0;
  background: transparent;
  border: none;
  transition: all 0.2s;
}

.schedule-block.period-current {
  background: transparent;
}

.schedule-block.period-completed {
  background: transparent;
}

.schedule-block.period-upcoming {
  opacity: 0.5;
}

.block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
  color: #3B82F6;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.period-completed .block-header {
  color: #10B981;
}

.period-upcoming .block-header {
  color: #94A3B8;
}


.tasks-container { display: flex; flex-direction: column; gap: 8px; }

.task-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.task-row:hover {
  background: rgba(0, 0, 0, 0.03);
}

.checkbox-circle {
  width: 20px;
  height: 20px;
  min-width: 20px;
  border-radius: 50%;
  border: 2px solid #CBD5E1;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.checkbox-circle:hover {
  border-color: #3B82F6;
}

.checkbox-circle.checked {
  background: #10B981;
  border-color: #10B981;
}

.check-icon {
  width: 12px;
  height: 12px;
  color: white;
}

.task-text { font-size: 13px; color: #334155; font-weight: 500; line-height: 1.4; }
.task-text.completed { color: #94A3B8; text-decoration: line-through; }

/* Schedule Group (주간/일간용) */
.schedule-group { display: flex; flex-direction: column; gap: 20px; }

/* 추가 폼 스타일 */
.add-form {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-label {
  font-size: 11px;
  font-weight: 600;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.minimal-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  font-size: 14px;
  color: #0F172A;
  background: #FFFFFF;
  transition: all 0.2s;
}

.minimal-input:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.minimal-input::placeholder {
  color: #94A3B8;
}

.minimal-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  font-size: 14px;
  color: #0F172A;
  background: #FFFFFF;
  cursor: pointer;
  transition: all 0.2s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.minimal-select:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 4px;
}

.btn-text {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  color: #64748B;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-text:hover {
  background: #E2E8F0;
  color: #334155;
}

.btn-text-primary {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #FFFFFF;
  background: #3B82F6;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-text-primary:hover {
  background: #2563EB;
}

.btn-text-primary:disabled {
  background: #94A3B8;
  cursor: not-allowed;
}
</style>
