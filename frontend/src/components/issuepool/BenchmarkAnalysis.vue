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
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }">
        <div>
          <h3 :style="{ fontSize: '20px', fontWeight: 600, color: '#FFFFFF', marginBottom: '8px' }">
            SK 17개 이슈 기반 벤치마킹 분석
          </h3>
          <p :style="{ fontSize: '13px', color: 'rgba(255,255,255,0.9)' }">
            경쟁사 지속가능경영 보고서를 SK Inc. 17개 ESG 이슈 기준으로 분석합니다.
          </p>
        </div>
        <div :style="{ display: 'flex', gap: '12px' }">
          <button
            @click="loadCachedData"
            :disabled="isLoading"
            :style="{
              padding: '10px 20px',
              background: 'rgba(255,255,255,0.2)',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.3)',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              fontSize: '13px',
              fontWeight: 600,
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }"
          >
            <RefreshCw :class="{ 'animate-spin': isLoading }" class="w-4 h-4" />
            데이터 새로고침
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="isLoading" :style="{ padding: '60px', textAlign: 'center' }">
        <div :style="{
          width: '48px',
          height: '48px',
          border: '4px solid #F3F4F6',
          borderTop: '4px solid #FF8F68',
          borderRadius: '50%',
          margin: '0 auto 16px',
          animation: 'spin 1s linear infinite'
        }"></div>
        <p :style="{ fontSize: '14px', color: '#6B7280' }">데이터를 불러오는 중...</p>
      </div>

      <!-- Error Message -->
      <div v-else-if="errorMessage" :style="{ padding: '40px', textAlign: 'center' }">
        <div :style="{
          padding: '20px',
          background: '#FEE2E2',
          borderRadius: '12px',
          color: '#B91C1C',
          fontSize: '14px'
        }">
          {{ errorMessage }}
        </div>
        <button
          @click="loadCachedData"
          :style="{
            marginTop: '16px',
            padding: '12px 24px',
            background: 'linear-gradient(120deg, #FF8F68, #F76D47)',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: 600,
            color: '#FFFFFF'
          }"
        >
          다시 시도
        </button>
      </div>

      <!-- No Data Message -->
      <div v-else-if="companies.length === 0" :style="{ padding: '60px', textAlign: 'center' }">
        <div :style="{ fontSize: '48px', marginBottom: '16px' }">📊</div>
        <p :style="{ fontSize: '16px', fontWeight: 600, color: '#1A1F2E', marginBottom: '8px' }">
          분석된 데이터가 없습니다
        </p>
        <p :style="{ fontSize: '13px', color: '#6B7280', marginBottom: '24px' }">
          PDF를 업로드하여 벤치마킹 분석을 시작하세요
        </p>

        <!-- Upload Section -->
        <div :style="{
          maxWidth: '500px',
          margin: '0 auto',
          border: '2px dashed #E8EAED',
          borderRadius: '12px',
          padding: '32px',
          background: '#FAFBFC'
        }">
          <input
            type="file"
            ref="fileInput"
            accept=".pdf"
            multiple
            @change="handleFileUpload"
            :style="{ display: 'none' }"
          />
          <button
            @click="($refs.fileInput as HTMLInputElement).click()"
            :style="{
              padding: '12px 24px',
              background: 'linear-gradient(120deg, #667eea, #764ba2)',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 600,
              color: '#FFFFFF',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px'
            }"
          >
            <Upload class="w-4 h-4" />
            지속가능경영 보고서 업로드
          </button>
          <p :style="{ marginTop: '12px', fontSize: '12px', color: '#6B7280' }">
            여러 회사의 PDF를 선택하세요 (파일명이 회사명으로 인식됩니다)
          </p>
        </div>
      </div>

      <!-- Main Content: SK 17 Issues Table -->
      <div v-else :style="{ padding: '24px' }">
        <!-- Top 5 Issues Summary -->
        <div :style="{ marginBottom: '24px' }">
          <div :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E', marginBottom: '16px' }">
            📊 경쟁사 중요 이슈 TOP 5
          </div>
          <div :style="{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px' }">
            <div
              v-for="(issue, index) in top5Issues"
              :key="issue.name"
              :style="{
                padding: '16px',
                background: index === 0 ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#F8F9FA',
                borderRadius: '12px',
                border: index === 0 ? 'none' : '1px solid #E8EAED'
              }"
            >
              <div :style="{
                fontSize: '24px',
                fontWeight: 700,
                color: index === 0 ? '#FFFFFF' : '#667eea',
                marginBottom: '8px'
              }">
                #{{ index + 1 }}
              </div>
              <div :style="{
                fontSize: '13px',
                fontWeight: 600,
                color: index === 0 ? '#FFFFFF' : '#1A1F2E',
                marginBottom: '4px',
                lineHeight: '1.4'
              }">
                {{ issue.name }}
              </div>
              <div :style="{
                fontSize: '12px',
                color: index === 0 ? 'rgba(255,255,255,0.8)' : '#6B7280'
              }">
                {{ issue.count }}개사 / 점수: {{ issue.score.toFixed(1) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Issues Table -->
        <div :style="{
          border: '1px solid #E8EAED',
          borderRadius: '12px',
          overflow: 'hidden'
        }">
          <div :style="{ overflowX: 'auto' }">
            <table :style="{ width: '100%', borderCollapse: 'collapse', minWidth: '1200px' }">
              <thead>
                <tr :style="{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }">
                  <th :style="{ padding: '14px 12px', textAlign: 'left', color: '#FFFFFF', fontSize: '12px', fontWeight: 600, position: 'sticky', left: 0, background: '#667eea', minWidth: '200px' }">
                    SK 17개 이슈
                  </th>
                  <th
                    v-for="company in companies"
                    :key="company"
                    :style="{ padding: '14px 12px', textAlign: 'center', color: '#FFFFFF', fontSize: '12px', fontWeight: 600, minWidth: '100px' }"
                  >
                    {{ company }}
                  </th>
                  <th :style="{ padding: '14px 12px', textAlign: 'center', color: '#FFFFFF', fontSize: '12px', fontWeight: 600, minWidth: '80px' }">COUNT</th>
                  <th :style="{ padding: '14px 12px', textAlign: 'center', color: '#FFFFFF', fontSize: '12px', fontWeight: 600, minWidth: '80px' }">점수</th>
                  <th :style="{ padding: '14px 12px', textAlign: 'center', color: '#FFFFFF', fontSize: '12px', fontWeight: 600, minWidth: '60px' }">순위</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(issue, idx) in sk17Issues"
                  :key="issue"
                  :style="{
                    borderBottom: '1px solid #E8EAED',
                    background: idx % 2 === 0 ? '#FFFFFF' : '#FAFBFC'
                  }"
                >
                  <td :style="{
                    padding: '12px',
                    fontSize: '12px',
                    fontWeight: 500,
                    color: '#1A1F2E',
                    position: 'sticky',
                    left: 0,
                    background: idx % 2 === 0 ? '#FFFFFF' : '#FAFBFC',
                    borderRight: '1px solid #E8EAED'
                  }">
                    <span :style="{ color: '#667eea', fontWeight: 600, marginRight: '8px' }">{{ idx + 1 }}.</span>
                    {{ issue }}
                  </td>
                  <td
                    v-for="company in companies"
                    :key="`${issue}-${company}`"
                    :style="{ padding: '12px', textAlign: 'center' }"
                  >
                    <span
                      @click="showDetail(company, issue)"
                      :style="{
                        display: 'inline-block',
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 600,
                        cursor: 'pointer',
                        ...getCoverageBadgeStyle(getCoverage(company, issue))
                      }"
                    >
                      {{ getCoverageText(getCoverage(company, issue)) }}
                    </span>
                  </td>
                  <td :style="{ padding: '12px', textAlign: 'center', fontSize: '14px', fontWeight: 600, color: '#667eea' }">
                    {{ getIssueCount(issue) }}
                  </td>
                  <td :style="{ padding: '12px', textAlign: 'center', fontSize: '14px', fontWeight: 600, color: '#1A1F2E' }">
                    {{ getIssueScore(issue).toFixed(1) }}
                  </td>
                  <td :style="{ padding: '12px', textAlign: 'center', fontSize: '14px', fontWeight: 700, color: '#F59E0B' }">
                    {{ getIssueRank(issue) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Legend -->
        <div :style="{ marginTop: '16px', display: 'flex', justifyContent: 'center', gap: '24px' }">
          <div :style="{ display: 'flex', alignItems: 'center', gap: '6px' }">
            <span :style="{ width: '12px', height: '12px', borderRadius: '50%', background: '#D1FAE5' }"></span>
            <span :style="{ fontSize: '12px', color: '#6B7280' }">Yes (완전 커버)</span>
          </div>
          <div :style="{ display: 'flex', alignItems: 'center', gap: '6px' }">
            <span :style="{ width: '12px', height: '12px', borderRadius: '50%', background: '#FEF3C7' }"></span>
            <span :style="{ fontSize: '12px', color: '#6B7280' }">Partially (부분 커버)</span>
          </div>
          <div :style="{ display: 'flex', alignItems: 'center', gap: '6px' }">
            <span :style="{ width: '12px', height: '12px', borderRadius: '50%', background: '#FEE2E2' }"></span>
            <span :style="{ fontSize: '12px', color: '#6B7280' }">No (미커버)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div
      v-if="showDetailModal"
      class="fixed inset-0 flex items-center justify-center"
      :style="{
        background: 'rgba(0,0,0,0.5)',
        zIndex: 9999,
        paddingLeft: '54px'
      }"
      @click="showDetailModal = false"
    >
      <div
        class="relative"
        :style="{
          width: '600px',
          maxHeight: '80vh',
          background: '#FFFFFF',
          borderRadius: '16px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }"
        @click.stop
      >
        <!-- Modal Header -->
        <div :style="{
          padding: '20px 24px',
          borderBottom: '1px solid #E8EAED',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
        }">
          <div :style="{ fontSize: '16px', fontWeight: 600, color: '#FFFFFF' }">
            {{ selectedDetail?.company }} - {{ selectedDetail?.issue }}
          </div>
        </div>

        <!-- Modal Content -->
        <div :style="{ flex: 1, overflowY: 'auto', padding: '24px' }">
          <div :style="{ marginBottom: '16px' }">
            <span :style="{
              padding: '6px 16px',
              borderRadius: '20px',
              fontSize: '13px',
              fontWeight: 600,
              ...getCoverageBadgeStyle(selectedDetail?.coverage || '')
            }">
              {{ getCoverageText(selectedDetail?.coverage || '') }}
            </span>
          </div>

          <div :style="{ marginBottom: '20px' }">
            <div :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E', marginBottom: '8px' }">
              매칭된 이슈명
            </div>
            <div :style="{ fontSize: '14px', color: '#4A5568', padding: '12px', background: '#F8F9FA', borderRadius: '8px' }">
              {{ selectedDetail?.matched_issue || '-' }}
            </div>
          </div>

          <div :style="{ marginBottom: '20px' }">
            <div :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E', marginBottom: '8px' }">
              분석 내용
            </div>
            <div :style="{ fontSize: '14px', color: '#4A5568', lineHeight: '1.7', padding: '12px', background: '#F8F9FA', borderRadius: '8px' }">
              {{ selectedDetail?.response || '-' }}
            </div>
          </div>

          <div v-if="selectedDetail?.source_pages?.length">
            <div :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E', marginBottom: '8px' }">
              참조 페이지
            </div>
            <div :style="{ display: 'flex', gap: '8px', flexWrap: 'wrap' }">
              <span
                v-for="page in selectedDetail.source_pages"
                :key="page"
                :style="{
                  padding: '4px 12px',
                  background: '#E8EAED',
                  borderRadius: '12px',
                  fontSize: '12px',
                  color: '#4A5568'
                }"
              >
                p. {{ page }}
              </span>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div :style="{
          padding: '16px 24px',
          borderTop: '1px solid #E8EAED',
          textAlign: 'right'
        }">
          <button
            @click="showDetailModal = false"
            :style="{
              padding: '10px 24px',
              background: '#F3F4F6',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 600,
              color: '#6B7280'
            }"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Upload, RefreshCw } from 'lucide-vue-next'
import apiClient from '@/api/axios.config'

interface IssueResult {
  coverage: 'Yes' | 'Partially' | 'No'
  response: string
  matched_issue: string
  source_pages: number[]
}

interface CompanyData {
  [issue: string]: IssueResult
}

interface BenchmarkData {
  [company: string]: CompanyData
}

interface DetailInfo {
  company: string
  issue: string
  coverage: string
  response: string
  matched_issue: string
  source_pages: number[]
}

const fileInput = ref<HTMLInputElement | null>(null)
const isLoading = ref(false)
const errorMessage = ref('')
const benchmarkData = ref<BenchmarkData>({})
const sk17Issues = ref<string[]>([])
const showDetailModal = ref(false)
const selectedDetail = ref<DetailInfo | null>(null)

// Computed properties
const companies = computed(() => Object.keys(benchmarkData.value))

const top5Issues = computed(() => {
  const issueStats = sk17Issues.value.map(issue => {
    const count = getIssueCount(issue)
    const score = getIssueScore(issue)
    return { name: issue, count, score }
  })

  return issueStats
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
})

// Methods
const loadCachedData = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    // Load SK 17 issues
    const issuesResponse = await apiClient.get('/api/v1/benchmark/issues')
    if (issuesResponse.data.success) {
      sk17Issues.value = issuesResponse.data.issues
    }

    // Load cached benchmark data
    const dataResponse = await apiClient.get('/api/v1/benchmark/data')
    if (dataResponse.data.success) {
      benchmarkData.value = dataResponse.data.data
    }
  } catch (error: any) {
    console.error('Failed to load benchmark data:', error)
    errorMessage.value = error.response?.data?.message || '데이터를 불러오는데 실패했습니다. 서버 연결을 확인해주세요.'
  } finally {
    isLoading.value = false
  }
}

const handleFileUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return

  isLoading.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()
    Array.from(input.files).forEach(file => {
      formData.append('files', file)
    })

    const response = await apiClient.post('/api/v1/benchmark/upload-and-analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 600000 // 10 minutes for analysis
    })

    if (response.data.success) {
      // Reload data after upload
      await loadCachedData()
    } else {
      errorMessage.value = response.data.message || '분석 중 오류가 발생했습니다.'
    }
  } catch (error: any) {
    console.error('Failed to upload and analyze:', error)
    errorMessage.value = error.response?.data?.message || '업로드 중 오류가 발생했습니다.'
  } finally {
    isLoading.value = false
    // Reset file input
    if (input) input.value = ''
  }
}

const getCoverage = (company: string, issue: string): string => {
  return benchmarkData.value[company]?.[issue]?.coverage || 'No'
}

const getIssueCount = (issue: string): number => {
  let count = 0
  for (const company of companies.value) {
    const coverage = getCoverage(company, issue)
    if (coverage === 'Yes' || coverage === 'Partially') {
      count++
    }
  }
  return count
}

const getIssueScore = (issue: string): number => {
  let score = 0
  for (const company of companies.value) {
    const coverage = getCoverage(company, issue)
    if (coverage === 'Yes') {
      score += 1
    } else if (coverage === 'Partially') {
      score += 0.5
    }
  }
  return score
}

const getIssueRank = (issue: string): number => {
  const scores = sk17Issues.value.map(i => ({ issue: i, score: getIssueScore(i) }))
  scores.sort((a, b) => b.score - a.score)
  const rank = scores.findIndex(s => s.issue === issue) + 1
  return rank
}

const showDetail = (company: string, issue: string) => {
  const data = benchmarkData.value[company]?.[issue]
  if (data) {
    selectedDetail.value = {
      company,
      issue,
      coverage: data.coverage,
      response: data.response,
      matched_issue: data.matched_issue,
      source_pages: data.source_pages || []
    }
    showDetailModal.value = true
  }
}

const getCoverageBadgeStyle = (coverage: string) => {
  switch (coverage) {
    case 'Yes':
      return { background: '#D1FAE5', color: '#047857' }
    case 'Partially':
      return { background: '#FEF3C7', color: '#B45309' }
    case 'No':
      return { background: '#FEE2E2', color: '#B91C1C' }
    default:
      return { background: '#F3F4F6', color: '#6B7280' }
  }
}

const getCoverageText = (coverage: string) => {
  switch (coverage) {
    case 'Yes': return 'Yes'
    case 'Partially': return 'Partially'
    case 'No': return 'No'
    default: return '-'
  }
}

// Load data on mount
onMounted(() => {
  loadCachedData()
})
</script>

<style>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
