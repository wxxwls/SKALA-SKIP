<template>
  <div
    class="w-full h-full flex"
    :style="{
      background: 'var(--background-secondary)',
      paddingLeft: '64px'
    }"
  >
    <!-- Main Content Area -->
    <div class="flex-1 overflow-y-auto" :style="{ padding: 'var(--spacing-2xl) var(--spacing-2xl) var(--spacing-2xl) var(--spacing-3xl)' }">
      <!-- Top - RE100 달성현황 (3 boxes) -->
      <div :style="{ marginBottom: 'var(--spacing-2xl)' }">
        <h2 :style="{ fontSize: '24px', fontWeight: 'var(--font-weight-semibold)', color: 'var(--foreground)', marginBottom: 'var(--spacing-xl)' }">
          국내외 RE100 달성현황
        </h2>
        <div class="grid grid-cols-3 gap-6">
          <div
:style="{
            background: 'var(--card)',
            borderRadius: 'var(--radius-xl)',
            padding: 'var(--spacing-2xl)',
            border: '1px solid var(--border)',
            boxShadow: 'var(--shadow-sm)',
            transition: 'all 0.2s'
          }"
          class="hover:shadow-md"
>
            <div :style="{ fontSize: '13px', color: 'var(--foreground-secondary)', marginBottom: 'var(--spacing-md)', fontWeight: 'var(--font-weight-medium)' }">
              국내 RE100 달성률
            </div>
            <div :style="{ fontSize: '40px', fontWeight: 'var(--font-weight-bold)', marginBottom: 'var(--spacing-md)', color: 'var(--primary)' }">
              68%
            </div>
            <div class="flex items-center gap-1" :style="{ fontSize: '13px', color: 'var(--color-success)', fontWeight: 'var(--font-weight-medium)' }">
              <TrendingUp :size="16" />
              <span>+12% 전년 대비</span>
            </div>
          </div>

          <div
:style="{
            background: 'var(--card)',
            borderRadius: 'var(--radius-xl)',
            padding: 'var(--spacing-2xl)',
            border: '1px solid var(--border)',
            boxShadow: 'var(--shadow-sm)',
            transition: 'all 0.2s'
          }"
          class="hover:shadow-md"
>
            <div :style="{ fontSize: '13px', color: 'var(--foreground-secondary)', marginBottom: 'var(--spacing-md)', fontWeight: 'var(--font-weight-medium)' }">
              글로벌 RE100 평균
            </div>
            <div :style="{ fontSize: '40px', fontWeight: 'var(--font-weight-bold)', marginBottom: 'var(--spacing-md)', color: 'var(--color-info)' }">
              82%
            </div>
            <div class="flex items-center gap-1" :style="{ fontSize: '13px', color: 'var(--color-success)', fontWeight: 'var(--font-weight-medium)' }">
              <TrendingUp :size="16" />
              <span>+8% 전년 대비</span>
            </div>
          </div>

          <div
:style="{
            background: 'var(--card)',
            borderRadius: 'var(--radius-xl)',
            padding: 'var(--spacing-2xl)',
            border: '1px solid var(--border)',
            boxShadow: 'var(--shadow-sm)',
            transition: 'all 0.2s'
          }"
          class="hover:shadow-md"
>
            <div :style="{ fontSize: '13px', color: 'var(--foreground-secondary)', marginBottom: 'var(--spacing-md)', fontWeight: 'var(--font-weight-medium)' }">
              SK 그룹 달성률
            </div>
            <div :style="{ fontSize: '40px', fontWeight: 'var(--font-weight-bold)', marginBottom: 'var(--spacing-md)', color: 'var(--color-success)' }">
              76%
            </div>
            <div class="flex items-center gap-1" :style="{ fontSize: '13px', color: 'var(--color-success)', fontWeight: 'var(--font-weight-medium)' }">
              <TrendingUp :size="16" />
              <span>+15% 전년 대비</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Middle - 탄소배출량 & 탄소배출권 그래프 -->
      <div class="grid grid-cols-2 gap-6" :style="{ marginBottom: '24px' }">
        <!-- 탄소배출량 -->
        <div
:style="{
          background: '#FFFFFF',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #E8EAED'
        }">
          <div :style="{ marginBottom: '20px' }">
            <div :style="{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }">
              Carbon Emissions
            </div>
            <div :style="{ fontSize: '16px', fontWeight: 600, color: '#1A1F2E' }">
              탄소배출량 추이
            </div>
            <div :style="{ fontSize: '28px', fontWeight: 700, color: '#1A1F2E', marginTop: '8px' }">
              350t <span :style="{ fontSize: '14px', color: '#10B981', fontWeight: 600 }">▼ 5.4%</span>
            </div>
          </div>
          <!-- Simple Chart -->
          <div :style="{ height: '200px', display: 'flex', alignItems: 'flex-end', gap: '8px', paddingTop: '20px' }">
            <div v-for="(item, index) in emissionData" :key="index" :style="{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }">
              <div :style="{ width: '100%', background: 'linear-gradient(to top, #FF6B9D20, #FF6B9D)', borderRadius: '4px', height: `${item.value / 5}px` }"></div>
              <span :style="{ fontSize: '11px', color: '#9CA3AF' }">{{ item.month }}</span>
            </div>
          </div>
        </div>

        <!-- 탄소배출권 -->
        <div
:style="{
          background: '#FFFFFF',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #E8EAED'
        }">
          <div :style="{ marginBottom: '20px' }">
            <div :style="{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }">
              Carbon Credits
            </div>
            <div :style="{ fontSize: '16px', fontWeight: 600, color: '#1A1F2E' }">
              탄소배출권 거래량
            </div>
            <div :style="{ fontSize: '28px', fontWeight: 700, color: '#1A1F2E', marginTop: '8px' }">
              190K <span :style="{ fontSize: '14px', color: '#10B981', fontWeight: 600 }">▲ 8.2%</span>
            </div>
          </div>
          <!-- Simple Chart -->
          <div :style="{ height: '200px', display: 'flex', alignItems: 'flex-end', gap: '8px', paddingTop: '20px' }">
            <div v-for="(item, index) in creditData" :key="index" :style="{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }">
              <div :style="{ width: '100%', background: 'linear-gradient(to top, #10B98120, #10B981)', borderRadius: '4px', height: `${item.value}px` }"></div>
              <span :style="{ fontSize: '11px', color: '#9CA3AF' }">{{ item.month }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom - 키워드 트렌드 분석 (전체 너비) -->
      <div
        :style="{
          background: '#FFFFFF',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #E8EAED',
          marginBottom: '24px'
        }"
      >
        <div class="flex items-center justify-between" :style="{ marginBottom: '20px' }">
          <div class="flex items-center gap-3">
            <div :style="{ fontSize: '18px', fontWeight: 600, color: '#1A1F2E' }">
              키워드 트렌드 분석
            </div>
            <div
              v-if="totalNewsCount > 0"
              :style="{
                padding: '4px 10px',
                borderRadius: '12px',
                background: '#FF8F6815',
                fontSize: '12px',
                color: '#FF8F68',
                fontWeight: 500
              }"
            >
              {{ totalNewsCount }}건 분석
            </div>
          </div>
          <button
            class="flex items-center gap-1 transition-all hover:bg-gray-100"
            :style="{
              padding: '8px 16px',
              borderRadius: '8px',
              border: '1px solid #E8EAED',
              background: '#FFFFFF',
              fontSize: '13px',
              color: '#6B7280',
              cursor: 'pointer'
            }"
            :disabled="isLoadingKeywords"
            @click="refreshKeywordData"
          >
            <RefreshCw :size="16" :class="{ 'animate-spin': isLoadingKeywords }" />
            <span>{{ isLoadingKeywords ? '분석 중...' : '새로고침' }}</span>
          </button>
        </div>

        <!-- 관계도 & 연관어 분석 가로 배치 -->
        <div class="grid grid-cols-2 gap-6">
          <!-- 관계도 분석 -->
          <div
            :style="{
              background: '#F7F8FA',
              borderRadius: '12px',
              padding: '16px',
              height: '380px'
            }"
          >
            <div class="flex items-center gap-2 mb-3" :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E' }">
              <span>🔗</span>
              <span>관계도 분석</span>
            </div>
            <KeywordGraph :keywords="keywordGraphData" height="330px" />
          </div>

          <!-- 연관어 분석 -->
          <div
            :style="{
              background: '#F7F8FA',
              borderRadius: '12px',
              padding: '16px',
              height: '380px'
            }"
          >
            <div class="flex items-center gap-2 mb-3" :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E' }">
              <span>📊</span>
              <span>연관어 분석</span>
            </div>
            <WordCloud :words="wordCloudData" height="330px" />
          </div>
        </div>
      </div>

      <!-- 오늘의 ESG 뉴스 -->
      <div
        :style="{
          background: '#FFFFFF',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #E8EAED'
        }"
      >
        <div class="flex items-center gap-2 mb-4">
          <Newspaper class="w-5 h-5" :style="{ color: '#FF8F68' }" />
          <div :style="{ fontSize: '16px', fontWeight: 600, color: '#1A1F2E' }">
            오늘의 ESG 뉴스
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="item in news"
            :key="item.id"
            class="p-3 rounded-lg transition-all hover:bg-gray-50 cursor-pointer"
            :style="{ border: '1px solid #F3F4F6' }"
          >
            <div class="flex items-start gap-2 mb-2">
              <div
                :style="{
                  padding: '2px 8px',
                  borderRadius: '4px',
                  fontSize: '10px',
                  fontWeight: 600,
                  color: '#FFFFFF',
                  background: getCategoryColor(item.category),
                  flexShrink: 0
                }"
              >
                {{ getCategoryLabel(item.category) }}
              </div>
              <div :style="{ fontSize: '10px', color: '#9CA3AF' }">
                {{ item.time }}
              </div>
            </div>
            <div :style="{ fontSize: '13px', fontWeight: 500, color: '#1A1F2E', marginBottom: '4px', lineHeight: '1.5' }">
              {{ item.title }}
            </div>
            <div :style="{ fontSize: '11px', color: '#6B7280' }">
              {{ item.source }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Sidebar - 업무일정 -->
    <div
:style="{
      width: '340px',
      background: '#FFFFFF',
      borderLeft: '1px solid #E8EAED',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
      height: '100%'
    }">
      <!-- Header -->
      <div
:style="{
        padding: '24px 20px 16px',
        borderBottom: '1px solid #E8EAED'
      }">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <Calendar class="w-5 h-5" :style="{ color: '#FF8F68' }" />
            <div :style="{ fontSize: '16px', fontWeight: 600, color: '#1A1F2E' }">
              업무일정
            </div>
          </div>
          <button
            class="flex items-center justify-center transition-all hover:bg-gray-100"
            :style="{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: '#F7F8FA',
              border: 'none',
              cursor: 'pointer'
            }"
            @click="showAddSchedule = true"
          >
            <Plus :size="18" :style="{ color: '#FF8F68' }" :stroke-width="2.5" />
          </button>
        </div>

        <!-- View Selector -->
        <div class="flex gap-2">
          <button
            v-for="view in ['yearly', 'monthly', 'weekly']"
            :key="view"
            :style="{
              flex: 1,
              padding: '8px 12px',
              borderRadius: '6px',
              border: 'none',
              fontSize: '12px',
              fontWeight: 600,
              background: scheduleView === view ? 'linear-gradient(120deg, #FF8F68, #F76D47)' : '#F7F8FA',
              color: scheduleView === view ? '#FFFFFF' : '#6B7280',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }"
            @click="scheduleView = view as any"
          >
            {{ view === 'yearly' ? '연간' : view === 'monthly' ? '월간' : '주간' }}
          </button>
        </div>
      </div>

      <!-- Schedule List -->
      <div class="flex-1 overflow-y-auto" :style="{ padding: '16px 20px' }">
        <!-- Add Schedule Form -->
        <div
          v-if="showAddSchedule"
          :style="{
            padding: '16px',
            background: '#F7F8FA',
            borderRadius: '8px',
            marginBottom: '16px',
            border: '1px solid #E8EAED'
          }"
        >
          <div class="space-y-3">
            <input
              v-model="newSchedule.date"
              type="text"
              placeholder="날짜 (예: 3월 15일)"
              :style="{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #E8EAED',
                fontSize: '12px',
                color: '#1A1F2E',
                background: '#FFFFFF'
              }"
            />
            <input
              v-model="newSchedule.time"
              type="text"
              placeholder="시간 (예: 09:00)"
              :style="{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #E8EAED',
                fontSize: '12px',
                color: '#1A1F2E',
                background: '#FFFFFF'
              }"
            />
            <input
              v-model="newSchedule.title"
              type="text"
              placeholder="제목"
              :style="{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #E8EAED',
                fontSize: '12px',
                color: '#1A1F2E',
                background: '#FFFFFF'
              }"
            />
            <div class="flex gap-2">
              <button
                :style="{
                  flex: 1,
                  padding: '8px 12px',
                  borderRadius: '6px',
                  background: 'linear-gradient(120deg, #FF8F68, #F76D47)',
                  border: 'none',
                  color: '#FFFFFF',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }"
                @click="handleAddSchedule"
              >
                추가
              </button>
              <button
                :style="{
                  flex: 1,
                  padding: '8px 12px',
                  borderRadius: '6px',
                  background: '#F3F4F6',
                  border: 'none',
                  color: '#6B7280',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }"
                @click="showAddSchedule = false"
              >
                취소
              </button>
            </div>
          </div>
        </div>

        <div class="space-y-3">
          <div
            v-for="schedule in filteredSchedules"
            :key="schedule.id"
            class="transition-all hover:shadow-md"
            :style="{
              background: '#FFFFFF',
              border: '1px solid #E8EAED',
              borderRadius: '10px',
              padding: '14px',
              cursor: 'pointer'
            }"
          >
            <!-- Date & Time -->
            <div class="flex items-center justify-between mb-2">
              <div :style="{ fontSize: '11px', color: '#9CA3AF', fontWeight: 500 }">
                {{ schedule.date }}
              </div>
              <div
:style="{
                fontSize: '11px',
                fontWeight: 600,
                color: getStatusColor(schedule.status),
                padding: '2px 8px',
                borderRadius: '4px',
                background: `${getStatusColor(schedule.status)}15`
              }">
                {{ schedule.time }}
              </div>
            </div>

            <!-- Title -->
            <div
:style="{
              fontSize: '13px',
              fontWeight: 600,
              color: '#1A1F2E',
              marginBottom: '10px',
              lineHeight: '1.4'
            }">
              {{ schedule.title }}
            </div>

            <!-- Task List -->
            <div class="space-y-2">
              <div v-for="task in schedule.tasks" :key="task.id" class="flex items-center gap-2">
                <div
                  :style="{
                    width: '16px',
                    height: '16px',
                    borderRadius: '4px',
                    border: `2px solid ${task.completed ? getStatusColor(schedule.status) : '#E8EAED'}`,
                    background: task.completed ? getStatusColor(schedule.status) : '#FFFFFF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    transition: 'all 0.2s'
                  }"
                >
                  <svg v-if="task.completed" width="10" height="8" viewBox="0 0 10 8" fill="none">
                    <path d="M1 4L3.5 6.5L9 1" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div
:style="{
                  fontSize: '11px',
                  color: task.completed ? '#9CA3AF' : '#6B7280',
                  textDecoration: task.completed ? 'line-through' : 'none'
                }">
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

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Calendar, Newspaper, Plus, TrendingUp, RefreshCw } from 'lucide-vue-next'
import KeywordGraph from './charts/KeywordGraph.vue'
import WordCloud from './charts/WordCloud.vue'
import mediaApi, { EsgIssue } from '../api/media.api'

interface NewsItem {
  id: string
  title: string
  source: string
  time: string
  category: 'esg' | 'carbon' | 're100' | 'regulation'
}

interface TaskItem {
  id: string
  title: string
  completed: boolean
}

interface ScheduleItem {
  id: string
  date: string
  time: string
  title: string
  status: 'done' | 'progress' | 'pending'
  progress: number
  view: 'yearly' | 'monthly' | 'weekly'
  tasks: TaskItem[]
}

const emissionData = [
  { month: 'Jan', value: 420 },
  { month: 'Feb', value: 380 },
  { month: 'Mar', value: 440 },
  { month: 'Apr', value: 390 },
  { month: 'May', value: 370 },
  { month: 'Jun', value: 350 },
]

const creditData = [
  { month: 'Jan', value: 120 },
  { month: 'Feb', value: 145 },
  { month: 'Mar', value: 135 },
  { month: 'Apr', value: 160 },
  { month: 'May', value: 175 },
  { month: 'Jun', value: 190 },
]

const scheduleView = ref<'yearly' | 'monthly' | 'weekly'>('weekly')
const showAddSchedule = ref(false)
const schedules = ref<ScheduleItem[]>([
  {
    id: '1',
    date: '3월 15일',
    time: '09:00',
    title: 'ESG 위원회 회의',
    status: 'done',
    progress: 100,
    view: 'weekly',
    tasks: [
      { id: '1-1', title: '회의 자료 준비', completed: true },
      { id: '1-2', title: '참석자 확인', completed: true },
      { id: '1-3', title: '회의록 작성', completed: true }
    ]
  },
  {
    id: '2',
    date: '3월 16일',
    time: '14:00',
    title: '탄소배출권 거래 검토',
    status: 'progress',
    progress: 65,
    view: 'weekly',
    tasks: [
      { id: '2-1', title: '시장 동향 분석', completed: true },
      { id: '2-2', title: '거래 전략 수립', completed: true },
      { id: '2-3', title: '최종 승인 대기', completed: false }
    ]
  },
  {
    id: '3',
    date: '3월 18일',
    time: '10:00',
    title: '지속가능경영 보고서 발간',
    status: 'pending',
    progress: 30,
    view: 'weekly',
    tasks: [
      { id: '3-1', title: '데이터 수집', completed: true },
      { id: '3-2', title: '보고서 작성', completed: false },
      { id: '3-3', title: '검토 및 승인', completed: false }
    ]
  },
  {
    id: '6',
    date: '3월 1주',
    time: '전체',
    title: 'ESG 전략 수립',
    status: 'done',
    progress: 100,
    view: 'monthly',
    tasks: [
      { id: '6-1', title: '현황 분석', completed: true },
      { id: '6-2', title: '전략 수립', completed: true },
      { id: '6-3', title: '실행 계획 수립', completed: true }
    ]
  },
  {
    id: '10',
    date: '1분기',
    time: 'Q1',
    title: 'ESG 경영체계 구축',
    status: 'done',
    progress: 100,
    view: 'yearly',
    tasks: [
      { id: '10-1', title: '조직 구성', completed: true },
      { id: '10-2', title: '프로세스 수립', completed: true },
      { id: '10-3', title: '시스템 구축', completed: true }
    ]
  },
])

const newSchedule = ref({
  date: '',
  time: '',
  title: ''
})

const news: NewsItem[] = [
  { id: '1', title: 'SK, 2024년 탄소배출 30% 감축 목표 달성...친환경 투자 확대', source: '한국경제', time: '2시간 전', category: 'carbon' },
  { id: '2', title: 'EU 탄소국경세(CBAM) 본격 시행, 국내 수출기업 대응 시급', source: '매일경제', time: '5시간 전', category: 'regulation' },
  { id: '3', title: '삼성전자, RE100 이행 로드맵 발표...2030년까지 재생에너지 100% 전환', source: '조선일보', time: '1일 전', category: 're100' },
  { id: '4', title: '국내 ESG 공시 의무화 2025년 적용 예정, 대기업 준비 박차', source: '연합뉴스', time: '1일 전', category: 'esg' },
  { id: '5', title: 'CDP 한국위원회, 2024 기후변화 우수기업', source: '서울경제', time: '2일 전', category: 'esg' },
]

// 키워드 관계도 데이터
interface KeywordNode {
  name: string
  value: number
  category: string
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
  { name: '패리다임', value: 12, category: 'G' },
  { name: '검색어', value: 11, category: 'S' },
  { name: '정의선', value: 10, category: 'G' },
])

// 연관어 분석 워드클라우드 데이터
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
  { name: 'M15X', value: 14, category: 'G' },
  { name: '대통령', value: 13, category: 'S' },
  { name: '정의선', value: 12, category: 'G' },
  { name: '이재명', value: 11, category: 'S' },
  { name: '로보틱스', value: 10, category: 'E' },
  { name: '대경권', value: 9, category: 'S' },
  { name: 'SK텔레콤', value: 8, category: 'G' },
  { name: '100메가와트', value: 7, category: 'E' },
  { name: '한반도', value: 6, category: 'S' },
  { name: '엔비디아', value: 5, category: 'G' },
  { name: '애플', value: 4, category: 'G' },
  { name: '삼성동', value: 3, category: 'S' },
  { name: '조지아', value: 2, category: 'S' },
  { name: '용인반도체클러스터', value: 1, category: 'E' },
])

const isLoadingKeywords = ref(false)
const totalNewsCount = ref(0)

// 뉴스 데이터 기반으로 키워드 갱신
const refreshKeywordData = async () => {
  isLoadingKeywords.value = true
  try {
    const response = await mediaApi.analyzeNews({
      keywords: ['SK하이닉스', 'ESG', '탄소중립', 'RE100', '친환경', '삼성전자', '현대자동차', '지속가능'],
      maxPages: 5
    })

    // 총 뉴스 수 업데이트
    totalNewsCount.value = response.totalArticles || 0

    if (response.statistics?.issueStatistics && response.statistics.issueStatistics.length > 0) {
      // issueStatistics를 키워드 그래프 데이터로 변환 - 더 많은 키워드 표시
      const newKeywords = response.statistics.issueStatistics.map((stat, index) => ({
        name: stat.issue,
        value: Math.max(stat.count * 5, 10),
        category: stat.esgCategory || (index === 0 ? 'central' : ['E', 'S', 'G'][index % 3])
      }))

      if (newKeywords.length > 0) {
        // 키워드 그래프에 더 많은 노드 표시 (최대 25개)
        keywordGraphData.value = newKeywords.slice(0, 25)

        // 워드클라우드 데이터도 업데이트 (최대 40개)
        wordCloudData.value = newKeywords.slice(0, 40).map(kw => ({
          name: kw.name,
          value: kw.value,
          category: kw.category
        }))
      }

      // 카테고리 통계도 워드클라우드에 추가
      if (response.statistics?.categoryStatistics) {
        const categoryKeywords = Object.entries(response.statistics.categoryStatistics).map(([name, count]) => ({
          name: name === 'E' ? '환경(E)' : name === 'S' ? '사회(S)' : '지배구조(G)',
          value: (count as number) * 3,
          category: name === 'E' ? 'E' : name === 'S' ? 'S' : 'G'
        }))
        wordCloudData.value = [...wordCloudData.value, ...categoryKeywords]
      }

      // 감성 통계도 추가
      if (response.statistics?.sentimentStatistics) {
        const sentimentKeywords = Object.entries(response.statistics.sentimentStatistics).map(([name, count]) => ({
          name: name === 'positive' ? '긍정' : name === 'negative' ? '부정' : '중립',
          value: (count as number) * 2,
          category: name === 'positive' ? 'E' : name === 'negative' ? 'S' : 'G'
        }))
        wordCloudData.value = [...wordCloudData.value, ...sentimentKeywords]
      }
    } else {
      // API 응답에 데이터가 없으면 ESG 이슈 정의 데이터 로드
      await loadEsgIssuesData()
    }
  } catch (error) {
    console.error('키워드 데이터 로드 실패, ESG 이슈 데이터로 대체:', error)
    // API 실패시 ESG 이슈 정의 데이터를 사용
    await loadEsgIssuesData()
  } finally {
    isLoadingKeywords.value = false
  }
}

// ESG 이슈 정의 데이터로 관계도 생성
const loadEsgIssuesData = async () => {
  try {
    const response = await mediaApi.getEsgIssues()
    if (response?.data?.issues) {
      const issues: EsgIssue[] = response.data.issues

      // 이슈를 그래프 데이터로 변환 (중앙 노드 + ESG 이슈들)
      const graphKeywords: KeywordNode[] = [
        { name: 'ESG', value: 50, category: 'central' }
      ]

      issues.forEach((issue, index) => {
        graphKeywords.push({
          name: issue.name,
          value: 35 - index * 1.5,
          category: issue.category
        })
      })

      keywordGraphData.value = graphKeywords.slice(0, 15)

      // 워드클라우드는 ESG 이슈 키워드들로 생성
      const cloudWords: { name: string; value: number; category?: string }[] = []
      issues.forEach((issue) => {
        issue.keywords.forEach((keyword, idx) => {
          cloudWords.push({
            name: keyword,
            value: 30 - idx * 5,
            category: issue.category
          })
        })
      })

      wordCloudData.value = cloudWords.slice(0, 30)
    }
  } catch (esgError) {
    console.error('ESG 이슈 데이터 로드 실패:', esgError)
  }
}

onMounted(() => {
  // 페이지 로드 시 키워드 데이터 갱신
  refreshKeywordData()
})

const filteredSchedules = computed(() => schedules.value.filter(s => s.view === scheduleView.value))

const handleAddSchedule = () => {
  if (!newSchedule.value.date || !newSchedule.value.time || !newSchedule.value.title) return

  const schedule: ScheduleItem = {
    id: Date.now().toString(),
    date: newSchedule.value.date,
    time: newSchedule.value.time,
    title: newSchedule.value.title,
    status: 'pending',
    progress: 0,
    view: scheduleView.value,
    tasks: []
  }

  schedules.value.push(schedule)
  newSchedule.value = { date: '', time: '', title: '' }
  showAddSchedule.value = false
}

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'esg': return '#597EFF'
    case 'carbon': return '#10B981'
    case 're100': return '#F59E0B'
    case 'regulation': return '#EF4444'
    default: return '#6B7280'
  }
}

const getCategoryLabel = (category: string) => {
  switch (category) {
    case 'esg': return 'ESG'
    case 'carbon': return '탄소'
    case 're100': return 'RE100'
    case 'regulation': return '규제'
    default: return ''
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'done': return '#10B981'
    case 'progress': return '#F59E0B'
    case 'pending': return '#6B7280'
    default: return '#6B7280'
  }
}
</script>
