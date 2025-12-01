<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import { Search, ChevronDown, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-vue-next';
import { mediaApi, type NewsArticle } from '@/api/media.api';

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
const ITEMS_PER_PAGE = 9; // 한 페이지당 뉴스 개수 (3x3 그리드)

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
  return filteredNews.value.slice(0, 2);
});

const regularNews = computed(() => {
  return filteredNews.value.slice(2);
});

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
  const cacheData: CachedNewsData = {
    timestamp: Date.now(),
    data
  };
  localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
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

function convertApiArticleToNewsItem(article: NewsArticle, category: 'company' | 'competitor' | 'regulation'): NewsItem {
  // 제목에서 HTML 태그 제거
  const cleanTitle = stripHtmlTags(article.cleanTitle || article.title);
  const cleanDescription = stripHtmlTags(article.description);

  // source 추출 (원본 제목에서)
  const sourceMatch = article.title.match(/\[([^\]]+)\]/);
  const source = sourceMatch ? stripHtmlTags(sourceMatch[1]) : '뉴스';

  return {
    id: article.link,
    title: cleanTitle,
    description: cleanDescription,
    url: article.link,
    urlToImage: null, // 네이버 뉴스 API는 썸네일 미제공
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
      maxPages: 3
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
    // 모든 카테고리 병렬로 가져오기
    const [companyNews, competitorNews, regulationNews] = await Promise.all([
      fetchNewsFromApi('company'),
      fetchNewsFromApi('competitor'),
      fetchNewsFromApi('regulation')
    ]);

    const newsData = {
      company: companyNews,
      competitor: competitorNews,
      regulation: regulationNews
    };

    allNews.value = newsData;
    setCacheData(newsData);
    lastUpdated.value = new Date();

  } catch (error) {
    console.error('Failed to fetch news:', error);
    // API 실패 시 mock 데이터 사용
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
      title: "[단독] 삼성전자, ESG 경영 강화...2030 탄소중립 목표",
      description: "삼성전자가 ESG 경영을 강화하며 2030년까지 탄소중립을 달성하겠다는 목표를 발표했다. 이번 발표에는 구체적인 실행 계획이 포함되어 있다.",
      url: 'https://example.com/news1',
      urlToImage: 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&h=400&fit=crop',
      publishedAt: new Date().toISOString(),
      source: '비즈니스포스트',
      category: selectedCategory.value
    },
    {
      id: '2',
      title: "[ESG] 지속가능경영보고서 발간...환경 투자 확대",
      description: "주요 대기업들이 지속가능경영보고서를 발간하며 환경 분야 투자를 확대하고 있다. 특히 재생에너지 도입이 주목받고 있다.",
      url: 'https://example.com/news2',
      urlToImage: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&h=400&fit=crop',
      publishedAt: new Date().toISOString(),
      source: '한국경제',
      category: selectedCategory.value
    },
    {
      id: '3',
      title: "[분석] ESG 평가 기준 강화...기업들 대응 분주",
      description: "ESG 평가 기준이 강화되면서 기업들이 대응에 분주하다. 특히 환경(E) 영역에서의 성과 개선이 시급한 상황이다.",
      url: 'https://example.com/news3',
      urlToImage: null,
      publishedAt: new Date().toISOString(),
      source: '매일경제',
      category: selectedCategory.value
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
});

// Watchers
watch([selectedCategory, searchQuery, dateRange], () => {
  // 필터 변경 시 첫 페이지로 리셋
  currentPage.value = 1;
});
</script>

<template>
  <div class="news-container">
    <!-- Search Bar -->
    <div class="search-bar">
      <div class="search-controls">
        <div class="search-input-wrapper">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="뉴스 검색..."
            class="search-input"
            @keypress="handleKeyPress"
          />
          <button class="search-button" @click="handleSearch">
            <Search class="w-4 h-4" />
          </button>
        </div>

        <div class="date-select-wrapper">
          <select v-model="dateRange" class="date-select">
            <option value="1일">1일</option>
            <option value="1주">1주</option>
            <option value="1개월">1개월</option>
            <option value="3개월">3개월</option>
            <option value="6개월">6개월</option>
            <option value="1년">1년</option>
          </select>
          <ChevronDown class="w-4 h-4 select-icon" />
        </div>

        <button
          class="refresh-button"
          @click="handleRefresh"
          :disabled="isRefreshing"
          :title="formatLastUpdated(lastUpdated)"
        >
          <RefreshCw class="w-4 h-4" :class="{ 'spinning': isRefreshing }" />
          <span>새로고침</span>
        </button>
      </div>

      <div v-if="lastUpdated" class="last-updated">
        {{ formatLastUpdated(lastUpdated) }}
      </div>
    </div>

    <!-- Category Tabs -->
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

    <!-- Main Content -->
    <div class="content-area">
      <div v-if="loading && !isRefreshing" class="loading-state">
        <div class="loading-spinner"></div>
        <span>뉴스를 불러오는 중...</span>
      </div>

      <template v-else>
        <!-- Empty State -->
        <div v-if="filteredNews.length === 0" class="empty-state">
          <p>표시할 뉴스가 없습니다.</p>
          <button class="refresh-link" @click="handleRefresh">새로고침</button>
        </div>

        <template v-else>
          <!-- Headline News Section -->
          <div v-if="headlines.length > 0" class="headline-section">
            <div class="section-title">헤드라인 뉴스</div>

            <div class="headline-list">
              <a
                v-for="headline in headlines"
                :key="headline.id"
                :href="headline.url"
                target="_blank"
                rel="noopener noreferrer"
                class="headline-item"
              >
                <div class="headline-content">
                  <div class="headline-badges">
                    <span
                      v-if="headline.esgCategories?.length"
                      class="esg-category-badge"
                      :style="{ backgroundColor: getEsgCategoryColor(headline.esgCategories[0]) }"
                    >
                      {{ headline.esgCategories[0] }}
                    </span>
                    <span v-if="headline.esgIssues?.length" class="keyword-text">
                      {{ headline.esgIssues.slice(0, 2).join(', ') }}
                    </span>
                    <span class="news-source-text">{{ headline.source }}</span>
                  </div>
                  <div class="headline-title">{{ headline.title }}</div>
                  <div class="headline-description">{{ headline.description }}</div>
                </div>
              </a>
            </div>
          </div>

          <!-- News Cards Grid -->
          <div v-if="regularNews.length > 0" class="news-section">
            <div class="section-title-row">
              <div class="section-title">최신 뉴스</div>
              <div class="news-count">총 {{ regularNews.length }}건</div>
            </div>
            <div class="news-grid">
              <a
                v-for="item in paginatedNews"
                :key="item.id"
                :href="item.url"
                target="_blank"
                rel="noopener noreferrer"
                class="news-card"
              >
                <div class="news-card-content">
                  <div class="news-card-badges">
                    <span
                      v-if="item.esgCategories?.length"
                      class="esg-category-badge"
                      :style="{ backgroundColor: getEsgCategoryColor(item.esgCategories[0]) }"
                    >
                      {{ item.esgCategories[0] }}
                    </span>
                    <span v-if="item.esgIssues?.length" class="keyword-text">
                      {{ item.esgIssues.slice(0, 2).join(', ') }}
                    </span>
                  </div>
                  <div class="news-card-title">{{ item.title }}</div>
                  <div class="news-card-description">{{ item.description }}</div>
                </div>
              </a>
            </div>

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="pagination">
              <button
                class="pagination-btn pagination-nav"
                :disabled="currentPage === 1"
                @click="prevPage"
              >
                <ChevronLeft class="w-4 h-4" />
                <span>이전</span>
              </button>

              <div class="pagination-numbers">
                <template v-for="page in pageNumbers" :key="page">
                  <span v-if="page === -1" class="pagination-ellipsis">...</span>
                  <button
                    v-else
                    class="pagination-btn pagination-num"
                    :class="{ 'pagination-active': currentPage === page }"
                    @click="goToPage(page)"
                  >
                    {{ page }}
                  </button>
                </template>
              </div>

              <button
                class="pagination-btn pagination-nav"
                :disabled="currentPage === totalPages"
                @click="nextPage"
              >
                <span>다음</span>
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
  background: var(--color-background);
}

/* Search Bar */
.search-bar {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: var(--spacing-md) var(--spacing-2xl);
}

.search-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
  max-width: 500px;
}

.search-input {
  width: 100%;
  padding: 10px 40px 10px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  font-size: var(--font-size-md);
  color: var(--color-text-primary);
  outline: none;
}

.search-input:focus {
  border-color: #ea7f52;
}

.search-button {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--color-text-secondary);
}

.date-select-wrapper {
  position: relative;
}

.date-select {
  padding: 10px 36px 10px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  font-size: var(--font-size-md);
  color: var(--color-text-primary);
  background: var(--color-surface);
  cursor: pointer;
  appearance: none;
  outline: none;
}

.select-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
  pointer-events: none;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: var(--font-size-md);
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

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.last-updated {
  margin-top: 8px;
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

/* Category Tabs */
.category-tabs {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 0 var(--spacing-2xl);
  display: flex;
  gap: 0;
}

.tab-button {
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  border: none;
  border-bottom: 3px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.tab-button-active {
  color: var(--color-text-primary);
  border-bottom-color: #ea7f52;
}

/* Content Area */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg) var(--spacing-2xl);
}

.loading-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 16px;
  height: 200px;
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: #ea7f52;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  height: 200px;
  color: var(--color-text-secondary);
}

.refresh-link {
  color: #ea7f52;
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: underline;
}

/* Section Title */
.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--color-border);
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.news-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

/* News Grid */
.news-section {
  margin-top: var(--spacing-2xl);
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.news-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 20px;
  border: 1px solid var(--color-border);
  text-decoration: none;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.news-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.news-card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.news-card-badges,
.headline-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.esg-category-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  background: #6B7280;  /* 기본값 (동적으로 변경됨) */
  color: white;
}

/* E(환경)=녹색, S(사회)=파랑, G(지배구조)=주황 */

.keyword-text {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.news-source-text {
  font-size: 12px;
  color: var(--color-text-muted);
}

.news-card-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-card-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: auto;
}

.news-source {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.sentiment-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: var(--font-weight-medium);
}

.sentiment-badge.positive {
  background: #dcfce7;
  color: #166534;
}

.sentiment-badge.negative {
  background: #fee2e2;
  color: #991b1b;
}

.sentiment-badge.neutral {
  background: #f3f4f6;
  color: #4b5563;
}

/* Headline Section */
.headline-section {
  margin-bottom: var(--spacing-xl);
}

.headline-list {
  background: var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.headline-item {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  gap: 20px;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.headline-item:hover {
  box-shadow: var(--shadow-lg);
}

.headline-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.headline-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  line-height: 1.4;
}

.headline-description {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

/* Responsive */
@media (max-width: 1200px) {
  .news-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .news-grid {
    grid-template-columns: 1fr;
  }

  .search-controls {
    flex-wrap: wrap;
  }

  .search-input-wrapper {
    max-width: 100%;
    width: 100%;
  }

  .headline-item {
    flex-direction: column;
  }
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.pagination-btn:hover:not(:disabled) {
  background: var(--color-background);
  border-color: #ea7f52;
  color: #ea7f52;
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-nav {
  min-width: 80px;
}

.pagination-numbers {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-num {
  min-width: 36px;
  padding: 8px;
}

.pagination-active {
  background: #ea7f52;
  border-color: #ea7f52;
  color: white;
}

.pagination-active:hover:not(:disabled) {
  background: #d96f45;
  border-color: #d96f45;
  color: white;
}

.pagination-ellipsis {
  padding: 0 8px;
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .pagination {
    flex-wrap: wrap;
    gap: 12px;
  }

  .pagination-nav {
    order: 1;
  }

  .pagination-numbers {
    order: 0;
    width: 100%;
    justify-content: center;
  }
}
</style>
