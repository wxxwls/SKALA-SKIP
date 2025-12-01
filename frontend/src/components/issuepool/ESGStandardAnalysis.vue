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
              ESG 표준 분석 결과
            </h3>
            <p :style="{ fontSize: '13px', color: '#6B7280' }">
              GRI, SASB 등 ESG 표준에서 추출한 공시 요구사항과 한국 중대성 항목 매핑 결과입니다.
            </p>
          </div>
          <div :style="{ display: 'flex', gap: '12px' }">
            <button
              @click="handleAnalyze"
              :disabled="isLoading"
              :style="{
                padding: '10px 20px',
                background: isLoading ? '#E8EAED' : 'linear-gradient(120deg, #FF8F68, #F76D47)',
                borderRadius: '8px',
                border: 'none',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                fontSize: '13px',
                fontWeight: 600,
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }"
            >
              <RefreshCw v-if="isLoading" class="w-4 h-4 animate-spin" />
              <FileSearch v-else class="w-4 h-4" />
              {{ isLoading ? '분석 중...' : '분석 실행' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Summary Cards -->
      <div :style="{ padding: '24px', borderBottom: '1px solid #E8EAED' }">
        <div :style="{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }">
          <div
            v-for="(stat, idx) in summaryStats"
            :key="idx"
            :style="{
              padding: '20px',
              background: stat.bgColor,
              borderRadius: '12px',
              textAlign: 'center'
            }"
          >
            <div :style="{ fontSize: '28px', fontWeight: 700, color: stat.color, marginBottom: '4px' }">
              {{ stat.value }}
            </div>
            <div :style="{ fontSize: '12px', color: '#6B7280' }">{{ stat.label }}</div>
          </div>
        </div>
      </div>

      <!-- Grouped Results by Korean Materiality -->
      <div :style="{ padding: '24px' }">
        <h4 :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E', marginBottom: '16px' }">
          한국 중대성 항목별 GRI/SASB 매핑
        </h4>

        <div class="space-y-4">
          <div
            v-for="(group, idx) in groupedResults"
            :key="idx"
            :style="{
              background: '#FFFFFF',
              border: '1px solid #E8EAED',
              borderRadius: '12px',
              overflow: 'hidden'
            }"
          >
            <!-- Group Header -->
            <div
              @click="toggleGroup(idx)"
              :style="{
                padding: '16px 20px',
                background: '#F9FAFB',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }"
            >
              <div :style="{ display: 'flex', alignItems: 'center', gap: '12px' }">
                <div :style="{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  background: getCategoryColor(group.esg_category) + '20',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                  fontWeight: 700,
                  color: getCategoryColor(group.esg_category)
                }">
                  {{ group.esg_category }}
                </div>
                <div>
                  <div :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E' }">
                    {{ group.issue_title }}
                  </div>
                  <div :style="{ fontSize: '12px', color: '#6B7280' }">
                    {{ group.disclosures.length }}개 공시 요구사항
                  </div>
                </div>
              </div>
              <ChevronDown
                :class="{ 'rotate-180': expandedGroups.includes(idx) }"
                class="w-5 h-5 transition-transform"
                :style="{ color: '#6B7280' }"
              />
            </div>

            <!-- Group Content -->
            <div
              v-if="expandedGroups.includes(idx)"
              :style="{ padding: '16px 20px' }"
            >
              <div class="space-y-3">
                <div
                  v-for="(disclosure, dIdx) in group.disclosures"
                  :key="dIdx"
                  :style="{
                    padding: '12px 16px',
                    background: '#FFF9F5',
                    borderRadius: '8px',
                    border: '1px solid #FFE5D6'
                  }"
                >
                  <div :style="{ display: 'flex', alignItems: 'flex-start', gap: '12px' }">
                    <div :style="{
                      padding: '4px 8px',
                      background: '#FF8F68',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: 600,
                      color: '#FFFFFF',
                      whiteSpace: 'nowrap'
                    }">
                      {{ disclosure.disclosure_id }}
                    </div>
                    <div>
                      <div :style="{ fontSize: '13px', fontWeight: 500, color: '#1A1F2E', marginBottom: '4px' }">
                        {{ disclosure.disclosure_title }}
                      </div>
                      <div :style="{ fontSize: '11px', color: '#6B7280' }">
                        {{ disclosure.standard }} | 신뢰도: {{ (disclosure.confidence * 100).toFixed(0) }}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { FileSearch, RefreshCw, ChevronDown } from 'lucide-vue-next'

interface Disclosure {
  disclosure_id: string
  disclosure_title: string
  standard: string
  confidence: number
}

interface GroupedResult {
  issue_title: string
  esg_category: string
  disclosures: Disclosure[]
}

const isLoading = ref(false)
const expandedGroups = ref<number[]>([0, 1, 2])

// Mock data - will be replaced with API call
const groupedResults = ref<GroupedResult[]>([
  {
    issue_title: '기후변화 대응',
    esg_category: 'E',
    disclosures: [
      { disclosure_id: 'GRI 305-1', disclosure_title: '직접 온실가스 배출량 (Scope 1)', standard: 'GRI 305', confidence: 0.95 },
      { disclosure_id: 'GRI 305-2', disclosure_title: '간접 온실가스 배출량 (Scope 2)', standard: 'GRI 305', confidence: 0.93 },
      { disclosure_id: 'GRI 305-3', disclosure_title: '기타 간접 온실가스 배출량 (Scope 3)', standard: 'GRI 305', confidence: 0.91 },
      { disclosure_id: 'TC-SI-130a.1', disclosure_title: '총 에너지 사용량', standard: 'SASB', confidence: 0.88 }
    ]
  },
  {
    issue_title: '신재생에너지 확대 및 전력 효율화',
    esg_category: 'E',
    disclosures: [
      { disclosure_id: 'GRI 302-1', disclosure_title: '조직 내부의 에너지 소비', standard: 'GRI 302', confidence: 0.92 },
      { disclosure_id: 'GRI 302-4', disclosure_title: '에너지 소비 절감', standard: 'GRI 302', confidence: 0.89 },
      { disclosure_id: 'TC-SI-130a.2', disclosure_title: '재생에너지 비율', standard: 'SASB', confidence: 0.87 }
    ]
  },
  {
    issue_title: '인재양성 및 다양성',
    esg_category: 'S',
    disclosures: [
      { disclosure_id: 'GRI 405-1', disclosure_title: '거버넌스 기구 및 직원의 다양성', standard: 'GRI 405', confidence: 0.94 },
      { disclosure_id: 'GRI 404-1', disclosure_title: '직원 1인당 평균 교육시간', standard: 'GRI 404', confidence: 0.91 },
      { disclosure_id: 'TC-SI-330a.3', disclosure_title: '성별 및 인종/민족별 기술 직원 비율', standard: 'SASB', confidence: 0.86 }
    ]
  },
  {
    issue_title: '정보보안 및 프라이버시',
    esg_category: 'S',
    disclosures: [
      { disclosure_id: 'GRI 418-1', disclosure_title: '고객 개인정보 침해 및 고객 데이터 분실 관련 입증된 불만 건수', standard: 'GRI 418', confidence: 0.96 },
      { disclosure_id: 'TC-SI-220a.1', disclosure_title: '데이터 침해 관련 법적 조치 건수', standard: 'SASB', confidence: 0.93 }
    ]
  },
  {
    issue_title: '투명한 이사회 경영',
    esg_category: 'G',
    disclosures: [
      { disclosure_id: 'GRI 2-9', disclosure_title: '지배구조 및 구성', standard: 'GRI 2', confidence: 0.94 },
      { disclosure_id: 'GRI 2-10', disclosure_title: '최고의사결정기구의 후보 추천 및 선정', standard: 'GRI 2', confidence: 0.90 }
    ]
  },
  {
    issue_title: '윤리 및 컴플라이언스',
    esg_category: 'G',
    disclosures: [
      { disclosure_id: 'GRI 205-2', disclosure_title: '반부패 정책 및 절차에 대한 커뮤니케이션과 교육', standard: 'GRI 205', confidence: 0.92 },
      { disclosure_id: 'GRI 206-1', disclosure_title: '반경쟁 행위, 반독점 및 독점 관행 관련 법적 조치', standard: 'GRI 206', confidence: 0.88 }
    ]
  }
])

const summaryStats = computed(() => {
  const totalDisclosures = groupedResults.value.reduce((sum, g) => sum + g.disclosures.length, 0)
  const eCategories = groupedResults.value.filter(g => g.esg_category === 'E').length
  const sCategories = groupedResults.value.filter(g => g.esg_category === 'S').length
  const gCategories = groupedResults.value.filter(g => g.esg_category === 'G').length

  return [
    { label: '총 공시 요구사항', value: totalDisclosures, color: '#1A1F2E', bgColor: '#F3F4F6' },
    { label: 'Environment', value: eCategories, color: '#10B981', bgColor: '#D1FAE5' },
    { label: 'Social', value: sCategories, color: '#3B82F6', bgColor: '#DBEAFE' },
    { label: 'Governance', value: gCategories, color: '#8B5CF6', bgColor: '#EDE9FE' }
  ]
})

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'E': return '#10B981'
    case 'S': return '#3B82F6'
    case 'G': return '#8B5CF6'
    default: return '#6B7280'
  }
}

const toggleGroup = (idx: number) => {
  const index = expandedGroups.value.indexOf(idx)
  if (index > -1) {
    expandedGroups.value.splice(index, 1)
  } else {
    expandedGroups.value.push(idx)
  }
}

const handleAnalyze = async () => {
  isLoading.value = true
  // TODO: Call AI service API
  await new Promise(resolve => setTimeout(resolve, 2000))
  isLoading.value = false
}
</script>
