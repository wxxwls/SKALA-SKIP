<template>
  <div class="h-full overflow-y-auto" :style="{ padding: '32px 40px' }">
    <div :style="{
      background: '#FFFFFF',
      borderRadius: '12px',
      border: '1px solid #E8EAED',
      overflow: 'hidden'
    }">
      <!-- Header Section -->
      <div :style="{
        padding: '24px',
        borderBottom: '1px solid #E8EAED',
        background: '#FAFBFC'
      }">
        <div :style="{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }">
          <div>
            <h3 :style="{ fontSize: '16px', fontWeight: 600, color: '#1A1F2E', marginBottom: '8px' }">
              ESG 미디어 분석
            </h3>
            <p :style="{ fontSize: '13px', color: '#6B7280' }">
              뉴스 기사를 수집하여 ESG 이슈 분류 및 감정 분석을 수행합니다.
            </p>
          </div>
          <div :style="{ display: 'flex', gap: '12px' }">
            <input
              type="text"
              v-model="searchKeyword"
              placeholder="검색 키워드 (예: SK 탄소중립)"
              @keyup.enter="handleAnalyze"
              :style="{
                padding: '10px 16px',
                border: '1px solid #E8EAED',
                borderRadius: '8px',
                fontSize: '13px',
                width: '240px',
                outline: 'none'
              }"
            />
            <button
              @click="handleAnalyze"
              :disabled="isLoading || !searchKeyword"
              :style="{
                padding: '10px 20px',
                background: (isLoading || !searchKeyword) ? '#E8EAED' : 'linear-gradient(120deg, #FF8F68, #F76D47)',
                borderRadius: '8px',
                border: 'none',
                cursor: (isLoading || !searchKeyword) ? 'not-allowed' : 'pointer',
                fontSize: '13px',
                fontWeight: 600,
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }"
            >
              <RefreshCw v-if="isLoading" class="w-4 h-4 animate-spin" />
              <Search v-else class="w-4 h-4" />
              {{ isLoading ? '분석 중...' : '뉴스 분석' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" :style="{
        padding: '16px 24px',
        background: '#FEE2E2',
        borderBottom: '1px solid #FECACA',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }">
        <AlertCircle class="w-5 h-5" :style="{ color: '#EF4444' }" />
        <span :style="{ fontSize: '13px', color: '#B91C1C' }">{{ errorMessage }}</span>
        <button
          @click="errorMessage = ''"
          :style="{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: '#B91C1C' }"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Summary Statistics -->
      <div :style="{ padding: '24px', borderBottom: '1px solid #E8EAED' }">
        <div :style="{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }">
          <div :style="{ padding: '20px', background: '#F3F4F6', borderRadius: '12px', textAlign: 'center' }">
            <div :style="{ fontSize: '28px', fontWeight: 700, color: '#1A1F2E' }">{{ totalArticles }}</div>
            <div :style="{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }">수집 기사</div>
          </div>
          <div :style="{ padding: '20px', background: '#D1FAE5', borderRadius: '12px', textAlign: 'center' }">
            <div :style="{ fontSize: '28px', fontWeight: 700, color: '#10B981' }">{{ positiveCount }}</div>
            <div :style="{ fontSize: '12px', color: '#047857', marginTop: '4px' }">긍정</div>
          </div>
          <div :style="{ padding: '20px', background: '#FEE2E2', borderRadius: '12px', textAlign: 'center' }">
            <div :style="{ fontSize: '28px', fontWeight: 700, color: '#EF4444' }">{{ negativeCount }}</div>
            <div :style="{ fontSize: '12px', color: '#B91C1C', marginTop: '4px' }">부정</div>
          </div>
          <div :style="{ padding: '20px', background: '#F3F4F6', borderRadius: '12px', textAlign: 'center' }">
            <div :style="{ fontSize: '28px', fontWeight: 700, color: '#6B7280' }">{{ neutralCount }}</div>
            <div :style="{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }">중립</div>
          </div>
          <div :style="{ padding: '20px', background: '#DBEAFE', borderRadius: '12px', textAlign: 'center' }">
            <div :style="{ fontSize: '28px', fontWeight: 700, color: '#3B82F6' }">{{ avgScore }}</div>
            <div :style="{ fontSize: '12px', color: '#1D4ED8', marginTop: '4px' }">평균 점수</div>
          </div>
        </div>
      </div>

      <!-- Two Column Layout -->
      <div :style="{ display: 'flex' }">
        <!-- Left Column: ESG Issue Statistics -->
        <div :style="{ flex: 1, padding: '24px', borderRight: '1px solid #E8EAED' }">
          <h4 :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E', marginBottom: '16px' }">
            ESG 이슈별 보도 현황
          </h4>

          <!-- Loading State -->
          <div v-if="isLoading" :style="{ textAlign: 'center', padding: '40px' }">
            <div :style="{
              width: '32px',
              height: '32px',
              border: '3px solid #E8EAED',
              borderTop: '3px solid #FF8F68',
              borderRadius: '50%',
              margin: '0 auto 12px',
              animation: 'spin 1s linear infinite'
            }"></div>
            <div :style="{ fontSize: '12px', color: '#6B7280' }">뉴스 분석 중...</div>
          </div>

          <!-- Issue Statistics -->
          <div v-else class="space-y-2">
            <div
              v-for="(issue, idx) in issueStatistics"
              :key="idx"
              @click="filterByIssue(issue.issue)"
              :style="{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px',
                background: selectedIssue === issue.issue ? '#FFF5F0' : '#F9FAFB',
                borderRadius: '8px',
                cursor: 'pointer',
                border: selectedIssue === issue.issue ? '1px solid #FF8F68' : '1px solid transparent',
                transition: 'all 0.2s'
              }"
            >
              <div :style="{
                width: '28px',
                height: '28px',
                borderRadius: '6px',
                background: getCategoryColor(issue.esg_category) + '20',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '11px',
                fontWeight: 700,
                color: getCategoryColor(issue.esg_category)
              }">
                {{ issue.esg_category }}
              </div>
              <div :style="{ flex: 1 }">
                <div :style="{ fontSize: '13px', fontWeight: 500, color: '#1A1F2E' }">
                  {{ issue.issue }}
                </div>
              </div>
              <div :style="{ display: 'flex', alignItems: 'center', gap: '8px' }">
                <div :style="{
                  width: '100px',
                  height: '8px',
                  background: '#E8EAED',
                  borderRadius: '4px',
                  overflow: 'hidden'
                }">
                  <div :style="{
                    width: issue.percentage + '%',
                    height: '100%',
                    background: getCategoryColor(issue.esg_category),
                    borderRadius: '4px'
                  }"></div>
                </div>
                <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', width: '40px', textAlign: 'right' }">
                  {{ issue.count }}건
                </div>
              </div>
            </div>
          </div>

          <!-- Clear Filter Button -->
          <button
            v-if="selectedIssue"
            @click="selectedIssue = ''"
            :style="{
              width: '100%',
              marginTop: '16px',
              padding: '10px',
              background: '#F3F4F6',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 500,
              color: '#6B7280'
            }"
          >
            필터 초기화
          </button>
        </div>

        <!-- Right Column: Recent News -->
        <div :style="{ flex: 1, padding: '24px' }">
          <div :style="{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }">
            <h4 :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E' }">
              {{ selectedIssue ? `'${selectedIssue}' 관련 기사` : '최근 주요 기사' }}
            </h4>
            <span v-if="selectedIssue" :style="{ fontSize: '12px', color: '#6B7280' }">
              {{ filteredArticles.length }}건
            </span>
          </div>

          <!-- Loading State -->
          <div v-if="isLoading" :style="{ textAlign: 'center', padding: '40px' }">
            <div :style="{ fontSize: '12px', color: '#6B7280' }">기사 로딩 중...</div>
          </div>

          <!-- No Results -->
          <div v-else-if="filteredArticles.length === 0" :style="{
            textAlign: 'center',
            padding: '60px 20px',
            color: '#9CA3AF'
          }">
            <Search class="w-12 h-12 mx-auto mb-4" :style="{ opacity: 0.5 }" />
            <div :style="{ fontSize: '14px', marginBottom: '8px' }">
              {{ totalArticles === 0 ? '키워드를 입력하고 뉴스 분석을 시작하세요' : '해당 조건의 기사가 없습니다' }}
            </div>
            <div :style="{ fontSize: '12px' }">
              검색 키워드: SK ESG, 삼성 탄소중립, 현대차 친환경 등
            </div>
          </div>

          <!-- Articles List -->
          <div v-else class="space-y-3" :style="{ maxHeight: '500px', overflowY: 'auto' }">
            <div
              v-for="(article, idx) in filteredArticles"
              :key="idx"
              :style="{
                padding: '16px',
                background: '#FFFFFF',
                border: '1px solid #E8EAED',
                borderRadius: '12px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }"
              @click="openArticle(article.link)"
              @mouseenter="($event.target as HTMLElement).style.borderColor = '#FF8F68'"
              @mouseleave="($event.target as HTMLElement).style.borderColor = '#E8EAED'"
            >
              <div :style="{ display: 'flex', alignItems: 'flex-start', gap: '12px' }">
                <div :style="{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: 600,
                  ...getSentimentStyle(article.sentiment)
                }">
                  {{ article.sentiment }}
                </div>
                <div :style="{ flex: 1 }">
                  <div :style="{ fontSize: '13px', fontWeight: 500, color: '#1A1F2E', marginBottom: '4px', lineHeight: '1.5' }">
                    {{ article.clean_title || article.title }}
                  </div>
                  <div :style="{ fontSize: '11px', color: '#6B7280', marginBottom: '8px' }">
                    {{ (article.clean_description || article.description || '').substring(0, 100) }}...
                  </div>
                  <div :style="{ display: 'flex', alignItems: 'center', gap: '12px' }">
                    <div :style="{ display: 'flex', flexWrap: 'wrap', gap: '4px' }">
                      <span
                        v-for="(issue, issueIdx) in (article.esg_issues || []).slice(0, 2)"
                        :key="issueIdx"
                        :style="{
                          padding: '2px 8px',
                          background: '#F3F4F6',
                          borderRadius: '4px',
                          fontSize: '10px',
                          color: '#6B7280'
                        }"
                      >
                        {{ issue }}
                      </span>
                    </div>
                    <div :style="{ fontSize: '10px', color: '#9CA3AF' }">
                      {{ formatDate(article.pubDate) }}
                    </div>
                  </div>
                </div>
                <ExternalLink class="w-4 h-4" :style="{ color: '#9CA3AF', flexShrink: 0 }" />
              </div>
            </div>
          </div>

          <button
            v-if="filteredArticles.length > 0 && filteredArticles.length < allArticles.length"
            @click="showAllArticles"
            :style="{
              width: '100%',
              marginTop: '16px',
              padding: '12px',
              background: '#F3F4F6',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 500,
              color: '#6B7280'
            }"
          >
            전체 기사 보기 ({{ allArticles.length }}건)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, RefreshCw, ExternalLink, AlertCircle, X } from 'lucide-vue-next'
import apiClient from '@/api/axios.config'

interface Article {
  title: string
  clean_title?: string
  description: string
  clean_description?: string
  link: string
  originallink?: string
  pubDate: string
  sentiment: '긍정' | '부정' | '중립'
  sentiment_score: number
  esg_issues: string[]
  esg_categories?: string[]
  positive_count?: number
  negative_count?: number
}

interface IssueStatistic {
  issue: string
  count: number
  percentage: number
  esg_category: string
}

// TODO: AnalysisStatistics interface removed - restore when needed for API integration
// interface AnalysisStatistics { ... }

const searchKeyword = ref('SK ESG')
const isLoading = ref(false)
const errorMessage = ref('')
const selectedIssue = ref('')

// Data from API
const totalArticles = ref(0)
const positiveCount = ref(0)
const negativeCount = ref(0)
const neutralCount = ref(0)
const avgScore = ref('0.00')
const issueStatistics = ref<IssueStatistic[]>([])
const allArticles = ref<Article[]>([])

// Filtered articles based on selected issue
const filteredArticles = computed(() => {
  if (!selectedIssue.value) {
    return allArticles.value.slice(0, 10)
  }
  return allArticles.value.filter(article =>
    article.esg_issues?.includes(selectedIssue.value)
  )
})

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'E': return '#10B981'
    case 'S': return '#3B82F6'
    case 'G': return '#8B5CF6'
    default: return '#6B7280'
  }
}

const getSentimentStyle = (sentiment: string) => {
  switch (sentiment) {
    case '긍정':
      return { background: '#D1FAE5', color: '#047857' }
    case '부정':
      return { background: '#FEE2E2', color: '#B91C1C' }
    case '중립':
      return { background: '#F3F4F6', color: '#6B7280' }
    default:
      return { background: '#F3F4F6', color: '#6B7280' }
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch {
    return dateStr
  }
}

const handleAnalyze = async () => {
  if (!searchKeyword.value) return

  isLoading.value = true
  errorMessage.value = ''
  selectedIssue.value = ''

  try {
    const response = await apiClient.post('/internal/v1/media/analyze', {
      keywords: searchKeyword.value.split(',').map(k => k.trim()).filter(k => k),
      max_pages: 3
    })

    if (response.data.success) {
      const data = response.data.data

      // Update statistics
      totalArticles.value = data.unique_articles || 0
      allArticles.value = data.articles || []

      // Sentiment statistics
      const sentimentStats = data.statistics?.sentiment_statistics || {}
      positiveCount.value = sentimentStats['긍정'] || 0
      negativeCount.value = sentimentStats['부정'] || 0
      neutralCount.value = sentimentStats['중립'] || 0
      avgScore.value = (sentimentStats.avg_score || 0).toFixed(2)

      // Issue statistics - filter out empty and sort
      const rawIssueStats = data.statistics?.issue_statistics || []
      issueStatistics.value = rawIssueStats
        .filter((issue: IssueStatistic) => issue.count > 0 && issue.issue !== '기타')
        .sort((a: IssueStatistic, b: IssueStatistic) => b.count - a.count)
        .slice(0, 10)
    } else {
      errorMessage.value = response.data.error?.message || '분석 중 오류가 발생했습니다.'
    }
  } catch (error: any) {
    console.error('Media analysis error:', error)
    errorMessage.value = error.response?.data?.error?.message ||
                         error.message ||
                         '서버 연결에 실패했습니다. API 서버가 실행 중인지 확인하세요.'
  } finally {
    isLoading.value = false
  }
}

const filterByIssue = (issue: string) => {
  selectedIssue.value = selectedIssue.value === issue ? '' : issue
}

const showAllArticles = () => {
  selectedIssue.value = ''
}

const openArticle = (link: string) => {
  if (link) {
    window.open(link, '_blank')
  }
}
</script>

<style>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
