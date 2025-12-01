```vue
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { Search, RefreshCw, ChevronLeft, ChevronRight, Calendar } from 'lucide-vue-next';
import { mediaApi } from '@/api/media.api';
import type { NewsArticle } from '@/api/media.api';

// Types
interface NewsItem {
  id: string;
  title: string;
  description: string;
  url: string;
  urlToImage: string | null;
  publishedAt: string;
  source: string;
  category: 'company' | 'competitor' | 'regulation';
  esgCategories?: string[];
  esgIssues?: string[];  // ESG 관련 키워드/이슈
  sentiment?: string;
}

interface CachedNewsData {
  timestamp: number;
  data: {
    company: NewsItem[];
    competitor: NewsItem[];
    regulation: NewsItem[];
  };
}

// Constants
const TABS = [
  { id: 'company', label: '자사' },
  { id: 'competitor', label: '타사' },
  { id: 'regulation', label: '규제' }
];

const CACHE_KEY = 'esg_news_cache';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24시간 (하루)
const ITEMS_PER_PAGE = 8; // 한 페이지당 뉴스 개수 (4x2 그리드)

// 카테고리별 검색 키워드 (자사=SK, 타사=경쟁사)
const CATEGORY_KEYWORDS: Record<string, string[]> = {
  company: ['SK ESG', 'SK하이닉스 ESG', 'SK이노베이션 ESG', 'SK 지속가능', 'SK 탄소중립'],
  competitor: ['삼성전자 ESG', 'LG ESG', '현대 ESG', '삼성 지속가능경영', '현대차 탄소중립'],
  regulation: ['ESG 규제', '탄소중립 정책', '환경규제', 'ESG 공시', '지속가능경영 의무화']
};

// State
const selectedCategory = ref<'company' | 'competitor' | 'regulation'>('company');
const searchQuery = ref('');
const dateRange = ref('1개월');
const allNews = ref<Record<string, NewsItem[]>>({
  company: [],
  competitor: [],
  regulation: []
});
const loading = ref(false);
const lastUpdated = ref<Date | null>(null);
const isRefreshing = ref(false);
const currentPage = ref(1);

// Computed
const filteredNews = computed(() => {
  let news = allNews.value[selectedCategory.value] || [];

  // 검색어 필터
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    news = news.filter(item =>
      item.title.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query)
    );
  }

  // 날짜 범위 필터
  const now = new Date();
  let filterDate = new Date();

  switch (dateRange.value) {
    case '1일':
      filterDate.setDate(now.getDate() - 1);
      break;
    case '1주':
      filterDate.setDate(now.getDate() - 7);
      break;
    case '1개월':
      filterDate.setMonth(now.getMonth() - 1);
      break;
    case '3개월':
      filterDate.setMonth(now.getMonth() - 3);
      break;
    case '6개월':
      filterDate.setMonth(now.getMonth() - 6);
      break;
    case '1년':
      filterDate.setFullYear(now.getFullYear() - 1);
      break;
  }

  news = news.filter(item => new Date(item.publishedAt) >= filterDate);

  return news;
});

const headlines = computed(() => {
  return filteredNews.value.slice(0, 3);
});

const regularNews = computed(() => {
  return filteredNews.value.slice(3);
});

// 캐러셀 상태
const currentHeadlineIndex = ref(0);
let carouselInterval: ReturnType<typeof setInterval> | null = null;

function nextHeadline() {
  if (headlines.value.length > 0) {
    currentHeadlineIndex.value = (currentHeadlineIndex.value + 1) % headlines.value.length;
  }
}

function prevHeadline() {
  if (headlines.value.length > 0) {
    currentHeadlineIndex.value = (currentHeadlineIndex.value - 1 + headlines.value.length) % headlines.value.length;
  }
}

function goToHeadline(index: number) {
  currentHeadlineIndex.value = index;
  resetCarouselInterval();
}

// 슬라이드 위치 계산 (prev, active, next)
function getSlidePosition(index: number): 'prev' | 'active' | 'next' | 'hidden' {
  const total = headlines.value.length;
  if (total === 0) return 'hidden';

  const current = currentHeadlineIndex.value;
  const prevIndex = (current - 1 + total) % total;
  const nextIndex = (current + 1) % total;

  if (index === current) return 'active';
  if (index === prevIndex) return 'prev';
  if (index === nextIndex) return 'next';
  return 'hidden';
}

function startCarouselInterval() {
  if (carouselInterval) clearInterval(carouselInterval);
  carouselInterval = setInterval(() => {
    nextHeadline();
  }, 5000); // 5초마다 자동 전환
}

function resetCarouselInterval() {
  startCarouselInterval();
}

// 페이지네이션 관련 computed
const totalPages = computed(() => {
  return Math.ceil(regularNews.value.length / ITEMS_PER_PAGE);
});

const paginatedNews = computed(() => {
  const start = (currentPage.value - 1) * ITEMS_PER_PAGE;
  const end = start + ITEMS_PER_PAGE;
  return regularNews.value.slice(start, end);
});

const pageNumbers = computed(() => {
  const pages: number[] = [];
  const total = totalPages.value;
  const current = currentPage.value;

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i);
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i);
      pages.push(-1); // ellipsis
      pages.push(total);
    } else if (current >= total - 3) {
      pages.push(1);
      pages.push(-1);
      for (let i = total - 4; i <= total; i++) pages.push(i);
    } else {
      pages.push(1);
      pages.push(-1);
      for (let i = current - 1; i <= current + 1; i++) pages.push(i);
      pages.push(-1);
      pages.push(total);
    }
  }
  return pages;
});

// Methods
function getCacheData(): CachedNewsData | null {
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (cached) {
      return JSON.parse(cached);
    }
  } catch (e) {
    console.error('Failed to parse cache:', e);
  }
  return null;
}

function setCacheData(data: CachedNewsData['data']) {
  try {
    const cacheData: CachedNewsData = {
      timestamp: Date.now(),
      data
    };
    localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
  } catch (e: any) {
    if (e.name === 'QuotaExceededError' || e.code === 22) {
      console.warn('LocalStorage quota exceeded. Trying to store reduced data...');
      try {
        // Try storing only the first 50 items per category
        const reducedData = {
          company: data.company.slice(0, 50),
          competitor: data.competitor.slice(0, 50),
          regulation: data.regulation.slice(0, 50)
        };
        const cacheData: CachedNewsData = {
          timestamp: Date.now(),
          data: reducedData
        };
        localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
        console.log('Stored reduced news data to cache.');
      } catch (retryError) {
        console.error('Failed to store even reduced data to cache:', retryError);
        // If still failing, maybe clear old cache
        localStorage.removeItem(CACHE_KEY);
      }
    } else {
      console.error('Failed to save to cache:', e);
    }
  }
}

function isCacheValid(cache: CachedNewsData): boolean {
  const now = Date.now();
  return (now - cache.timestamp) < CACHE_DURATION;
}

// HTML 태그 완전 제거 함수
function stripHtmlTags(text: string): string {
  if (!text) return '';
  return text
    .replace(/<\/?[^>]+(>|$)/g, '') // 모든 HTML 태그 제거
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, ' ')
    .trim();
}

// Smart Image Matching Logic
const IMAGE_KEYWORD_MAP: Record<string, string[]> = {
  // Environment (환경)
  'environment': ['https://images.unsplash.com/photo-1497436072909-60f360e1d4b0?auto=format&fit=crop&q=80&w=800', 'https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&q=80&w=800', 'https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?auto=format&fit=crop&q=80&w=800'],
  'energy': ['https://images.unsplash.com/photo-1466611653911-95081537e5b7?auto=format&fit=crop&q=80&w=800', 'https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=800'],
  'carbon': ['https://images.unsplash.com/photo-1569163139599-0f4517e36b51?auto=format&fit=crop&q=80&w=800'],
  
  // Social (사회)
  'social': ['https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&q=80&w=800', 'https://images.unsplash.com/photo-1544027993-37dbfe43562a?auto=format&fit=crop&q=80&w=800'],
  'safety': ['https://images.unsplash.com/photo-1581092921461-eab62e97a782?auto=format&fit=crop&q=80&w=800'],
  
  // Governance (지배구조)
  'governance': ['https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&q=80&w=800', 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&q=80&w=800'],
  'meeting': ['https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&q=80&w=800'],

  // Tech/Business
  'tech': ['https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=800', 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=800'],
  'business': ['https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&q=80&w=800', 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=800']
};

const KEYWORD_MAPPING: Record<string, string[]> = {
  'environment': ['탄소', '환경', '그린', '녹색', '에너지', '기후', '재생', '태양광', '풍력', '수소', 'E'],
  'energy': ['배터리', '전력', '발전', '충전'],
  'social': ['사회', '상생', '동반', '협력', '기부', '봉사', '인권', 'S'],
  'safety': ['안전', '보건', '재해'],
  'governance': ['지배구조', '이사회', '투명', '윤리', '주주', 'G'],
  'meeting': ['경영', '회의', '주총'],
  'tech': ['반도체', 'AI', '디지털', '기술', '혁신', 'SK', '삼성', 'LG', '칩'],
  'business': ['투자', '실적', '매출', '영업', '시장']
};

function getSmartImage(title: string, description: string): string {
  const text = `${title} ${description}`.toLowerCase();
  
  for (const [category, keywords] of Object.entries(KEYWORD_MAPPING)) {
    if (keywords.some(k => text.includes(k.toLowerCase()))) {
      const images = IMAGE_KEYWORD_MAP[category];
      // Use a deterministic hash based on title length to pick an image
      // so the same article always gets the same image
      const index = title.length % images.length;
      return images[index];
    }
  }
  
  // Fallback
  return 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=800';
}

function convertApiArticleToNewsItem(article: NewsArticle, category: 'company' | 'competitor' | 'regulation'): NewsItem {
  // 제목에서 HTML 태그 제거
  const cleanTitle = stripHtmlTags(article.cleanTitle || article.title);
  const cleanDescription = stripHtmlTags(article.description);

  // source 추출 (원본 제목에서)
  const sourceMatch = article.title.match(/\[([^\]]+)\]/);
  const source = sourceMatch ? stripHtmlTags(sourceMatch[1]) : '뉴스';

  // Smart Image Selection
  const smartImage = getSmartImage(cleanTitle, cleanDescription);

  return {
    id: article.link,
    title: cleanTitle,
    description: cleanDescription,
    url: article.link,
    urlToImage: smartImage,
    publishedAt: article.pubDate,
    source: source,
    category: category,
    esgCategories: article.esgCategories,
    esgIssues: article.esgIssues,  // ESG 관련 키워드 추가
    sentiment: article.sentiment
  };
}

async function fetchNewsFromApi(category: 'company' | 'competitor' | 'regulation'): Promise<NewsItem[]> {
  const keywords = CATEGORY_KEYWORDS[category];

  try {
    const response = await mediaApi.analyzeNews({
      keywords: keywords,
      maxPages: 10
    });

    return response.articles.map(article => convertApiArticleToNewsItem(article, category));
  } catch (error) {
    console.error(`Failed to fetch ${category} news:`, error);
    return [];
  }
}

async function fetchAllNews(forceRefresh = false) {
  // 캐시 확인
  if (!forceRefresh) {
    const cache = getCacheData();
    if (cache && isCacheValid(cache)) {
      allNews.value = cache.data;
      lastUpdated.value = new Date(cache.timestamp);
      console.log('Using cached news data');
      return;
    }
  }

  loading.value = true;
  isRefreshing.value = forceRefresh;

  try {
    // 서버 부하 방지를 위해 순차적으로 요청 (Promise.all 대신)
    // 자사 뉴스
    const companyNews = await fetchNewsFromApi('company');
    
    // 타사 뉴스 (약간의 딜레이 후 요청)
    await new Promise(resolve => setTimeout(resolve, 500));
    const competitorNews = await fetchNewsFromApi('competitor');
    
    // 규제 뉴스 (약간의 딜레이 후 요청)
    await new Promise(resolve => setTimeout(resolve, 500));
    const regulationNews = await fetchNewsFromApi('regulation');

    // 하나라도 데이터가 있으면 성공으로 처리
    if (companyNews.length > 0 || competitorNews.length > 0 || regulationNews.length > 0) {
      const newsData = {
        company: companyNews,
        competitor: competitorNews,
        regulation: regulationNews
      };

      allNews.value = newsData;
      setCacheData(newsData);
      lastUpdated.value = new Date();
    } else {
      throw new Error('No news data fetched');
    }

  } catch (error) {
    console.error('Failed to fetch news:', error);
    // API 실패 시 mock 데이터 사용
    console.log('Falling back to mock data...');
    loadMockData();
  } finally {
    loading.value = false;
    isRefreshing.value = false;
  }
}

function loadMockData() {
  const mockNews: NewsItem[] = [
    {
      id: '1',
      title: "SK, '넷제로' 달성 위해 100조원 투자... 친환경 사업 가속화",
      description: "SK그룹이 2050년 넷제로 달성을 위해 향후 5년간 100조원을 투자한다. 전기차 배터리, 수소 등 친환경 미래 사업에 역량을 집중할 계획이다.",
      url: 'https://www.hankyung.com',
      urlToImage: 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=1200',
      publishedAt: new Date().toISOString(),
      source: '한국경제',
      category: selectedCategory.value,
      esgCategories: ['E'],
      esgIssues: ['탄소중립', '친환경투자']
    },
    {
      id: '2',
      title: "글로벌 ESG 평가서 'A등급' 획득... 지속가능경영 성과 입증",
      description: "주요 계열사들이 글로벌 ESG 평가기관인 MSCI로부터 A등급 이상을 획득하며 지속가능경영 성과를 국제적으로 인정받았다.",
      url: 'https://www.mk.co.kr',
      urlToImage: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&q=80&w=1200',
      publishedAt: new Date(Date.now() - 86400000).toISOString(),
      source: '매일경제',
      category: selectedCategory.value,
      esgCategories: ['G'],
      esgIssues: ['투명경영', '이사회']
    },
    {
      id: '3',
      title: "협력사 상생 프로그램 확대... 공급망 ESG 관리 강화",
      description: "협력사들의 ESG 경영 역량 강화를 위해 금융 지원 및 컨설팅 프로그램을 대폭 확대한다. 공급망 전체의 리스크를 선제적으로 관리하기 위함이다.",
      url: 'https://www.sedaily.com',
      urlToImage: 'https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&q=80&w=1200',
      publishedAt: new Date(Date.now() - 172800000).toISOString(),
      source: '서울경제',
      category: selectedCategory.value,
      esgCategories: ['S'],
      esgIssues: ['동반성장', '공급망관리']
    },
    {
      id: '4',
      title: "재생에너지 사용 비율 50% 돌파... RE100 달성 청신호",
      description: "국내 사업장의 재생에너지 사용 비율이 50%를 넘어섰다. 태양광 발전 설비 확충과 PPA 계약 체결 등이 주효했다.",
      url: 'https://www.etnews.com',
      urlToImage: 'https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&q=80&w=1200',
      publishedAt: new Date(Date.now() - 259200000).toISOString(),
      source: '전자신문',
      category: selectedCategory.value,
      esgCategories: ['E'],
      esgIssues: ['RE100', '재생에너지']
    },
    {
      id: '5',
      title: "사회공헌 활동의 진화... 단순 기부 넘어 '소셜 임팩트' 창출",
      description: "단순한 기부 활동을 넘어 사회적 문제를 해결하고 경제적 가치까지 창출하는 '소셜 임팩트' 중심의 사회공헌 활동으로 전환하고 있다.",
      url: 'https://www.chosun.com',
      urlToImage: 'https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&q=80&w=1200',
      publishedAt: new Date(Date.now() - 345600000).toISOString(),
      source: '조선일보',
      category: selectedCategory.value,
      esgCategories: ['S'],
      esgIssues: ['사회공헌', '지역사회']
    }
  ];

  allNews.value = {
    company: mockNews.map(n => ({ ...n, category: 'company' as const })),
    competitor: mockNews.map(n => ({ ...n, category: 'competitor' as const })),
    regulation: mockNews.map(n => ({ ...n, category: 'regulation' as const }))
  };
}

function handleSearch() {
  // 검색어 변경 시 필터링은 computed에서 자동 처리됨
}

function handleKeyPress(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    handleSearch();
  }
}

// ESG 카테고리 한글 변환
function getEsgCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    'E': '환경',
    'S': '사회',
    'G': '지배구조'
  };
  return labels[category] || category;
}

// ESG 카테고리별 색상 반환
function getEsgCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    'E': '#10B981',  // 환경 - 녹색
    'S': '#3B82F6',  // 사회 - 파랑
    'G': '#F59E0B',  // 지배구조 - 주황
    '환경': '#10B981',
    '사회': '#3B82F6',
    '지배구조': '#F59E0B'
  };
  return colors[category] || '#6B7280';  // 기본 회색
}

function handleRefresh() {
  fetchAllNews(true);
}

// 페이지네이션 함수
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    // 스크롤을 뉴스 섹션 상단으로
    document.querySelector('.news-section')?.scrollIntoView({ behavior: 'smooth' });
  }
}

function prevPage() {
  goToPage(currentPage.value - 1);
}

function nextPage() {
  goToPage(currentPage.value + 1);
}

function formatLastUpdated(date: Date | null): string {
  if (!date) return '';
  return `마지막 업데이트: ${date.toLocaleString('ko-KR')}`;
}

// Lifecycle
onMounted(() => {
  fetchAllNews();
  startCarouselInterval();
});

onUnmounted(() => {
  if (carouselInterval) {
    clearInterval(carouselInterval);
  }
});

// Watchers
watch([selectedCategory, searchQuery, dateRange], () => {
  // 필터 변경 시 첫 페이지로 리셋
  currentPage.value = 1;
});
</script>

<template>
  <div class="news-container">
    <!-- Header Section -->
    <div class="header-section">
      <div class="header-content">
        <h1 class="page-title">ESG News Trend</h1>
        <p class="page-subtitle">실시간으로 업데이트되는 ESG 관련 최신 뉴스와 이슈를 확인하세요.</p>
      </div>
      
      <div class="search-bar">
        <div class="search-input-wrapper">
          <Search class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="관심있는 키워드를 검색해보세요"
            class="search-input"
            @keypress="handleKeyPress"
          />
        </div>

        <div class="filter-group">
          <div class="date-select-wrapper">
            <select v-model="dateRange" class="date-select">
              <option value="1일">최근 24시간</option>
              <option value="1주">최근 1주일</option>
              <option value="1개월">최근 1개월</option>
              <option value="3개월">최근 3개월</option>
            </select>
            <ChevronDown class="select-icon" />
          </div>

          <button
            class="refresh-button"
            @click="handleRefresh"
            :disabled="isRefreshing"
            :title="formatLastUpdated(lastUpdated)"
          >
            <RefreshCw class="w-4 h-4" :class="{ 'spinning': isRefreshing }" />
          </button>
        </div>
      </div>
    </div>

    <!-- Category Tabs -->
    <div class="tabs-container">
      <div class="category-tabs">
        <button
          v-for="tab in TABS"
          :key="tab.id"
          class="tab-button"
          :class="{ 'tab-button-active': selectedCategory === tab.id }"
          @click="selectedCategory = tab.id as 'company' | 'competitor' | 'regulation'"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="content-area">
      <div v-if="loading && !isRefreshing" class="loading-state">
        <div class="loading-spinner"></div>
        <span>뉴스를 불러오는 중...</span>
      </div>

      <template v-else>
        <!-- Empty State -->
        <div v-if="filteredNews.length === 0" class="empty-state">
          <div class="empty-icon">📰</div>
          <p>검색 결과가 없습니다.</p>
          <button class="refresh-link" @click="handleRefresh">새로고침</button>
        </div>

        <template v-else>
          <!-- Headline News Section (Carousel) -->
          <div v-if="headlines.length > 0" class="headline-section">
            <div class="section-header">
              <h2 class="section-title">Headline News</h2>
              <span class="section-subtitle">오늘의 주요 이슈</span>
            </div>

            <div class="headline-carousel">
              <!-- Carousel Container -->
              <div class="carousel-container">
                <a
                  v-for="(headline, index) in headlines"
                  :key="headline.id"
                  :href="getSlidePosition(index) === 'active' ? headline.url : undefined"
                  :target="getSlidePosition(index) === 'active' ? '_blank' : undefined"
                  rel="noopener noreferrer"
                  class="carousel-slide"
                  :class="`carousel-slide-${getSlidePosition(index)}`"
                  @click.prevent="getSlidePosition(index) !== 'active' && (getSlidePosition(index) === 'prev' ? prevHeadline() : nextHeadline())"
                >
                  <div class="headline-image-wrapper">
                    <img
                      :src="headline.urlToImage || `https://source.unsplash.com/random/800x600?esg,business&sig=${index}`"
                      alt="News Thumbnail"
                      class="headline-image"
                      @error="($event.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=1200'"
                    />
                    <div class="headline-overlay"></div>
                    <div class="headline-badges">
                      <span
                        v-if="headline.esgCategories?.length"
                        class="badge category-badge"
                        :style="{ backgroundColor: getEsgCategoryColor(headline.esgCategories[0]) }"
                      >
                        {{ getEsgCategoryLabel(headline.esgCategories[0]) }}
                      </span>
                      <span class="badge source-badge">{{ headline.source }}</span>
                    </div>
                  </div>
                  <div class="headline-content">
                    <h3 class="headline-title">{{ headline.title }}</h3>
                    <p class="headline-description">{{ headline.description }}</p>
                    <div class="headline-meta">
                      <span class="date">{{ new Date(headline.publishedAt).toLocaleDateString() }}</span>
                      <span v-if="headline.esgIssues?.length" class="issues">
                        #{{ headline.esgIssues.slice(0, 2).join(' #') }}
                      </span>
                    </div>
                  </div>
                </a>
              </div>

              <!-- Carousel Navigation Buttons -->
              <button class="carousel-nav carousel-prev" @click="prevHeadline(); resetCarouselInterval()">
                <ChevronLeft class="w-6 h-6" />
              </button>
              <button class="carousel-nav carousel-next" @click="nextHeadline(); resetCarouselInterval()">
                <ChevronRight class="w-6 h-6" />
              </button>

              <!-- Carousel Indicators -->
              <div class="carousel-indicators">
                <button
                  v-for="(_, index) in headlines"
                  :key="index"
                  class="carousel-dot"
                  :class="{ 'carousel-dot-active': index === currentHeadlineIndex }"
                  @click="goToHeadline(index)"
                />
              </div>
            </div>
          </div>

          <!-- News Cards Grid -->
          <div v-if="regularNews.length > 0" class="news-section">
            <div class="section-header">
              <h2 class="section-title">Latest News</h2>
              <span class="news-count">총 {{ regularNews.length }}건</span>
            </div>
            
            <div class="news-grid">
              <a
                v-for="(item, index) in paginatedNews"
                :key="item.id"
                :href="item.url"
                target="_blank"
                rel="noopener noreferrer"
                class="news-card"
              >
                <div class="news-image-wrapper">
                  <img 
                    :src="item.urlToImage || `https://source.unsplash.com/random/400x300?office,meeting&sig=${index + 10}`" 
                    alt="News Thumbnail" 
                    class="news-image"
                    @error="$event.target.src = 'https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&q=80&w=800'"
                  />
                  <div class="news-badges">
                    <span
                      v-if="item.esgCategories?.length"
                      class="badge category-badge"
                      :style="{ backgroundColor: getEsgCategoryColor(item.esgCategories[0]) }"
                    >
                      {{ getEsgCategoryLabel(item.esgCategories[0]) }}
                    </span>
                  </div>
                </div>
                <div class="news-card-content">
                  <div class="news-meta-top">
                    <span class="news-source">{{ item.source }}</span>
                    <span class="news-date">{{ new Date(item.publishedAt).toLocaleDateString() }}</span>
                  </div>
                  <h3 class="news-card-title">{{ item.title }}</h3>
                  <p class="news-card-description">{{ item.description }}</p>
                  <div class="news-footer">
                    <div v-if="item.esgIssues?.length" class="news-tags">
                      <span v-for="issue in item.esgIssues.slice(0, 2)" :key="issue" class="tag">#{{ issue }}</span>
                    </div>
                  </div>
                </div>
              </a>
            </div>

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="pagination">
              <button
                class="pagination-btn nav-btn"
                :disabled="currentPage === 1"
                @click="prevPage"
              >
                <ChevronLeft class="w-4 h-4" />
              </button>

              <div class="pagination-numbers">
                <template v-for="page in pageNumbers" :key="page">
                  <span v-if="page === -1" class="pagination-ellipsis">...</span>
                  <button
                    v-else
                    class="pagination-btn num-btn"
                    :class="{ 'active': currentPage === page }"
                    @click="goToPage(page)"
                  >
                    {{ page }}
                  </button>
                </template>
              </div>

              <button
                class="pagination-btn nav-btn"
                :disabled="currentPage === totalPages"
                @click="nextPage"
              >
                <ChevronRight class="w-4 h-4" />
              </button>
            </div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
.news-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8f9fa; /* Light gray background for better contrast */
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
}

/* Header Section */
.header-section {
  padding: 32px 40px;
  background: white;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.page-title {
  font-size: 28px;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: -0.5px;
  margin: 0;
}

.page-subtitle {
  font-size: 15px;
  color: #666;
  margin: 0;
}

.search-bar {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input-wrapper {
  position: relative;
  width: 320px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #999;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 42px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-input:focus {
  background: white;
  border-color: #ea7f52;
  box-shadow: 0 0 0 3px rgba(234, 127, 82, 0.1);
  outline: none;
}

.filter-group {
  display: flex;
  gap: 8px;
}

.date-select-wrapper {
  position: relative;
}

.date-select {
  appearance: none;
  padding: 12px 36px 12px 16px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: white;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.date-select:hover {
  border-color: #d1d5db;
}

.select-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #6b7280;
  pointer-events: none;
}

.refresh-button {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-button:hover {
  background: #f9fafb;
  color: #ea7f52;
  border-color: #ea7f52;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Tabs */
.tabs-container {
  padding: 0 40px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.category-tabs {
  display: flex;
  gap: 32px;
}

.tab-button {
  padding: 16px 4px;
  font-size: 16px;
  font-weight: 600;
  color: #9ca3af;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-button:hover {
  color: #4b5563;
}

.tab-button-active {
  color: #ea7f52;
  border-bottom-color: #ea7f52;
}

/* Content Area */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 32px 40px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

/* Headline Section */
.headline-section {
  margin-bottom: 80px; /* 인디케이터 공간 확보 */
  padding-bottom: 20px;
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.section-subtitle {
  font-size: 14px;
  color: #6b7280;
}

/* Carousel Styles - Flat Carousel */
.headline-carousel {
  position: relative;
  width: 100%;
  height: 400px;
  overflow: visible;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-slide {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 55%;
  height: 90%;
  transform: translate(-50%, -50%);
  text-decoration: none;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transition: all 0.4s ease;
  cursor: pointer;
  background: #e5e7eb;
}

/* 활성 슬라이드 (중앙) */
.carousel-slide-active {
  z-index: 10;
  transform: translate(-50%, -50%) scale(1);
  opacity: 1;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.25);
}

/* 이전 슬라이드 (왼쪽) - 70% 크기 */
.carousel-slide-prev {
  z-index: 5;
  transform: translate(-120%, -50%) scale(0.7);
  opacity: 0.6;
}

/* 다음 슬라이드 (오른쪽) - 70% 크기 */
.carousel-slide-next {
  z-index: 5;
  transform: translate(20%, -50%) scale(0.7);
  opacity: 0.6;
}

/* 숨겨진 슬라이드 */
.carousel-slide-hidden {
  z-index: 0;
  transform: translate(-50%, -50%) scale(0.7);
  opacity: 0;
  pointer-events: none;
}

.carousel-slide-prev:hover,
.carousel-slide-next:hover {
  opacity: 0.85;
}

.carousel-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #374151;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  z-index: 20;
}

.carousel-nav:hover {
  background: white;
  transform: translateY(-50%) scale(1.15);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
}

.carousel-prev {
  left: 21%;
}

.carousel-next {
  right: 21%;
}

.carousel-indicators {
  position: absolute;
  bottom: -50px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
  z-index: 10;
}

.carousel-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #d1d5db;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.carousel-dot:hover {
  background: #9ca3af;
}

.carousel-dot-active {
  background: #ea7f52;
  transform: scale(1.3);
}

.headline-image-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.headline-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.headline-card:hover .headline-image {
  transform: scale(1.05);
}

.headline-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0.1) 100%);
}

.headline-badges {
  position: absolute;
  top: 24px;
  left: 24px;
  display: flex;
  gap: 8px;
  z-index: 1;
}

.badge {
  padding: 6px 12px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.category-badge {
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.source-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.headline-content {
  position: relative;
  z-index: 1;
  padding: 32px;
}

.headline-title {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.3;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.headline-description {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  margin: 0 0 20px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.headline-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

/* News Grid */
.news-section {
  margin-top: 48px;
}

.news-count {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.news-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  text-decoration: none;
  border: 1px solid #f3f4f6;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.news-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: transparent;
}

.news-image-wrapper {
  position: relative;
  padding-top: 60%; /* 5:3 Aspect Ratio */
  overflow: hidden;
}

.news-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.news-card:hover .news-image {
  transform: scale(1.05);
}

.news-badges {
  position: absolute;
  top: 16px;
  left: 16px;
}

.news-card-content {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.news-meta-top {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 12px;
}

.news-source {
  font-weight: 600;
  color: #ea7f52;
}

.news-card-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.4;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-card-description {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0 0 20px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.news-footer {
  margin-top: auto;
}

.news-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 6px;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 60px;
  padding-bottom: 40px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #e5e7eb;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
}

.num-btn {
  min-width: 40px;
  height: 40px;
  padding: 0 12px;
  border-radius: 12px;
  font-weight: 500;
}

.pagination-numbers {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.pagination-ellipsis {
  color: #6b7280;
  padding: 0 4px;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #ea7f52;
  color: #ea7f52;
}

.pagination-btn.active {
  background: #ea7f52;
  border-color: #ea7f52;
  color: white;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f9fafb;
}

/* Loading & Empty States */
.loading-state, .empty-state {
  height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 16px;
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #ea7f52;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.refresh-link {
  color: #ea7f52;
  background: none;
  border: none;
  text-decoration: underline;
  cursor: pointer;
  font-weight: 600;
}

/* Responsive */
@media (max-width: 1024px) {
  .headline-carousel {
    height: 340px;
  }

  .carousel-slide {
    width: 60%;
  }

  .carousel-slide-prev {
    transform: translate(-115%, -50%) scale(0.65);
  }

  .carousel-slide-next {
    transform: translate(15%, -50%) scale(0.65);
  }

  .carousel-nav {
    width: 44px;
    height: 44px;
  }

  .carousel-prev {
    left: 18%;
  }

  .carousel-next {
    right: 18%;
  }

  .headline-title {
    font-size: 22px;
  }

  .headline-content {
    padding: 24px;
  }
}

@media (max-width: 1400px) {
  .news-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1100px) {
  .news-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
    padding: 24px;
  }

  .search-bar {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .search-input-wrapper {
    width: 100%;
  }

  .filter-group {
    justify-content: space-between;
  }

  .content-area {
    padding: 24px;
  }

  .news-grid {
    grid-template-columns: 1fr;
  }

  .headline-section {
    margin-bottom: 60px;
  }

  .headline-carousel {
    height: 280px;
  }

  .carousel-slide {
    width: 75%;
  }

  .carousel-slide-prev {
    transform: translate(-105%, -50%) scale(0.6);
    opacity: 0.5;
  }

  .carousel-slide-next {
    transform: translate(5%, -50%) scale(0.6);
    opacity: 0.5;
  }

  .carousel-nav {
    width: 36px;
    height: 36px;
  }

  .carousel-prev {
    left: 12%;
  }

  .carousel-next {
    right: 12%;
  }

  .headline-title {
    font-size: 16px;
  }

  .headline-description {
    font-size: 13px;
    -webkit-line-clamp: 2;
  }

  .headline-content {
    padding: 16px;
  }

  .carousel-indicators {
    bottom: -40px;
  }

  .carousel-dot {
    width: 8px;
    height: 8px;
  }
}
</style>
