<template>
  <div
    class="w-full h-screen flex overflow-hidden"
    :style="{
      background: '#F7F8FA',
      paddingLeft: '0px',
      boxSizing: 'border-box'
    }"
  >
    <!-- Main Content -->
    <div class="flex-1 overflow-hidden min-w-0" :style="{ padding: '12px 16px' }">
      <!-- Top Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-2" :style="{ width: '100%', overflowX: 'hidden' }">
        <div
          v-for="(stat, index) in stats"
          :key="index"
          :style="{
            background: '#FFFFFF',
            borderRadius: '12px',
            padding: '16px 20px',
            border: '1px solid #E8EAED'
          }"
        >
          <div :style="{ fontSize: '11px', color: '#6B7280', marginBottom: '6px' }">
            {{ stat.label }}
          </div>
          <div :style="{ fontSize: '20px', fontWeight: 700, color: '#1A1F2E' }">
            {{ stat.value }}
          </div>
        </div>
      </div>

      <!-- Top Split Charts: Emissions vs Carbon Credit -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-3 mb-2" :style="{ width: '100%', overflowX: 'hidden' }">
        <!-- Emissions Trend -->
        <div
          :style="{
            background: '#FFFFFF',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid #E8EAED',
            maxWidth: '100%'
          }"
        >
          <div class="flex items-center justify-between mb-4">
            <div>
              <div :style="{ fontSize: '11px', color: '#6B7280', marginBottom: '2px' }">
                Statistics
              </div>
              <div :style="{ fontSize: '15px', fontWeight: 600, color: '#1A1F2E' }">
                탄소 배출 추이
              </div>
            </div>
            <div class="flex gap-2">
              <button
                v-for="period in periods"
                :key="period"
                :style="{
                  padding: '5px 14px',
                  borderRadius: '20px',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '11px',
                  fontWeight: 500,
                  background: selectedPeriod === period ? '#2D3142' : 'transparent',
                  color: selectedPeriod === period ? '#FFFFFF' : '#6B7280',
                  transition: 'all 0.2s'
                }"
                @click="selectedPeriod = period"
              >
                {{ period }}
              </button>
            </div>
          </div>

          <!-- Emissions Chart -->
          <div :style="{ height: '180px', paddingTop: '6px' }">
            <div ref="emissionsChartRef" :style="{ width: '100%', height: '100%' }" />
          </div>
        </div>

        <!-- Carbon Credit Trend -->
        <div
          :style="{
            background: '#FFFFFF',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid #E8EAED'
          }"
        >
          <div class="flex items-center justify-between mb-4">
            <div>
              <div :style="{ fontSize: '11px', color: '#6B7280', marginBottom: '2px' }">
                Statistics
              </div>
              <div :style="{ fontSize: '15px', fontWeight: 600, color: '#1A1F2E' }">
                탄소 배출권 추이
              </div>
            </div>
            <div class="flex gap-2">
              <button
                v-for="period in periods"
                :key="period"
                :style="{
                  padding: '5px 14px',
                  borderRadius: '20px',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '11px',
                  fontWeight: 500,
                  background: selectedPeriod === period ? '#2D3142' : 'transparent',
                  color: selectedPeriod === period ? '#FFFFFF' : '#6B7280',
                  transition: 'all 0.2s'
                }"
                @click="selectedPeriod = period"
              >
                {{ period }}
              </button>
            </div>
          </div>

          <div :style="{ height: '180px', paddingTop: '6px' }">
            <div ref="carbonCandleChartRef" :style="{ width: '100%', height: '100%' }" />
          </div>
        </div>
      </div>

      <!-- Bottom Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-3" :style="{ width: '100%', overflowX: 'hidden' }">
        <!-- Account Reached -->
        <div
          :style="{
            background: '#FFFFFF',
            borderRadius: '12px',
            padding: '20px',
            border: '1px solid #E8EAED'
          }"
        >
          <div :style="{ fontSize: '11px', color: '#6B7280', marginBottom: '2px' }">
            Statistics
          </div>
          <div :style="{ fontSize: '15px', fontWeight: 600, color: '#1A1F2E', marginBottom: '12px' }">
            탄소 절감 현황
          </div>
          <div :style="{ fontSize: '28px', fontWeight: 700, color: '#1A1F2E', marginBottom: '4px' }">
            11,756 <span :style="{ fontSize: '13px', color: '#10B981', fontWeight: 600 }">+23%</span>
          </div>

          <!-- Simple Area Chart -->
          <div :style="{ height: '90px', display: 'flex', alignItems: 'flex-end', gap: '12px', marginTop: '12px' }">
            <div
              v-for="(data, index) in accountData"
              :key="index"
              :style="{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '8px'
              }"
            >
              <div
                :style="{
                  width: '100%',
                  height: `${data.value}px`,
                  background: 'linear-gradient(180deg, #597EFF 0%, rgba(89, 126, 255, 0.1) 100%)',
                  borderRadius: '4px 4px 0 0'
                }"
              />
              <div :style="{ fontSize: '10px', color: '#9CA3AF' }">
                {{ data.name }}
              </div>
            </div>
          </div>
        </div>

        <!-- Small Charts + Total Income -->
        <div class="flex flex-col gap-4">
          <!-- Small Charts Row -->
          <div class="grid grid-cols-2 gap-3">
            <!-- Realtime -->
            <div
              :style="{
                background: '#FFFFFF',
                borderRadius: '12px',
                padding: '14px',
                border: '1px solid #E8EAED'
              }"
            >
              <div :style="{ fontSize: '10px', color: '#6B7280', marginBottom: '2px' }">
                Statistics
              </div>
              <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '6px' }">
                실시간 배출량
              </div>
              <div :style="{ fontSize: '16px', fontWeight: 700, color: '#1A1F2E', marginBottom: '4px' }">
                628
              </div>
              <div :style="{ fontSize: '10px', color: '#10B981', marginBottom: '8px' }">
                +21%
              </div>

              <!-- Mini Line Chart -->
              <div :style="{ height: '50px', display: 'flex', alignItems: 'flex-end', gap: '4px' }">
                <div
                  v-for="(data, index) in realtimeData"
                  :key="index"
                  :style="{
                    flex: 1,
                    height: `${data.value}px`,
                    background: '#597EFF',
                    borderRadius: '2px'
                  }"
                />
              </div>
            </div>

            <!-- Total Visits -->
            <div
              :style="{
                background: '#FFFFFF',
                borderRadius: '12px',
                padding: '14px',
                border: '1px solid #E8EAED'
              }"
            >
              <div :style="{ fontSize: '10px', color: '#6B7280', marginBottom: '2px' }">
                Statistics
              </div>
              <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '6px' }">
                총 절감량
              </div>
              <div :style="{ fontSize: '16px', fontWeight: 700, color: '#1A1F2E', marginBottom: '4px' }">
                1.2M
              </div>
              <div :style="{ fontSize: '10px', color: '#10B981', marginBottom: '8px' }">
                +3%
              </div>

              <!-- Mini Line Chart -->
              <div :style="{ height: '50px', display: 'flex', alignItems: 'flex-end', gap: '4px' }">
                <div
                  v-for="(data, index) in visitsData"
                  :key="index"
                  :style="{
                    flex: 1,
                    height: `${data.value}px`,
                    background: '#10B981',
                    borderRadius: '2px'
                  }"
                />
              </div>
            </div>
          </div>

          <!-- Total Income -->
          <div
            :style="{
              background: '#FFFFFF',
              borderRadius: '12px',
              padding: '16px',
              border: '1px solid #E8EAED',
              flex: 1
            }"
          >
            <div :style="{ fontSize: '10px', color: '#6B7280', marginBottom: '2px' }">
              Statistics
            </div>
            <div :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E', marginBottom: '12px' }">
              탄소 크레딧 거래량
            </div>

            <!-- Simple Line Chart -->
            <div :style="{ height: '80px', display: 'flex', alignItems: 'flex-end', gap: '10px' }">
              <div
                v-for="(data, index) in incomeData"
                :key="index"
                :style="{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '8px'
                }"
              >
                <div :style="{ display: 'flex', gap: '4px', alignItems: 'flex-end', height: '70px' }">
                  <div
                    :style="{
                      width: '8px',
                      height: `${data.product}px`,
                      background: '#FF6B9D',
                      borderRadius: '2px'
                    }"
                  />
                  <div
                    :style="{
                      width: '8px',
                      height: `${data.subscription}px`,
                      background: '#597EFF',
                      borderRadius: '2px'
                    }"
                  />
                </div>
                <div :style="{ fontSize: '9px', color: '#9CA3AF' }">
                  {{ data.name }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Sidebar - Calendar -->
    <div
      class="hidden xl:flex shrink-0"
      :style="{
        width: '320px',
        background: '#FFFFFF',
        borderLeft: '1px solid #E8EAED',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }"
    >
      <!-- Profit Rate Cards -->
      <div class="grid grid-cols-2 gap-3 mb-5">
        <div
          :style="{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '12px',
            padding: '14px',
            color: '#FFFFFF'
          }"
        >
          <div :style="{ fontSize: '10px', opacity: 0.9, marginBottom: '4px' }">
            수익률
          </div>
          <div :style="{ fontSize: '20px', fontWeight: 700 }">
            +18.5%
          </div>
          <div :style="{ fontSize: '9px', opacity: 0.8, marginTop: '2px' }">
            이번 달
          </div>
        </div>

        <div
          :style="{
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            borderRadius: '12px',
            padding: '14px',
            color: '#FFFFFF'
          }"
        >
          <div :style="{ fontSize: '10px', opacity: 0.9, marginBottom: '4px' }">
            연간 수익률
          </div>
          <div :style="{ fontSize: '20px', fontWeight: 700 }">
            +42.3%
          </div>
          <div :style="{ fontSize: '9px', opacity: 0.8, marginTop: '2px' }">
            2022년
          </div>
        </div>
      </div>

      <!-- Calendar Header -->
      <div class="flex items-center justify-between mb-5">
        <span :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E' }">
          {{ currentMonth }}
        </span>
        <div class="flex gap-2">
          <button
            :style="{
              width: '26px',
              height: '26px',
              borderRadius: '6px',
              border: '1px solid #E8EAED',
              background: '#FFFFFF',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }"
          >
            <ChevronLeft class="w-4 h-4" :style="{ color: '#6B7280' }" />
          </button>
          <button
            :style="{
              width: '26px',
              height: '26px',
              borderRadius: '6px',
              border: '1px solid #E8EAED',
              background: '#FFFFFF',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }"
          >
            <ChevronRight class="w-4 h-4" :style="{ color: '#6B7280' }" />
          </button>
        </div>
      </div>

      <!-- Calendar Grid -->
      <div :style="{ marginBottom: '20px' }">
        <!-- Day Headers -->
        <div class="grid grid-cols-7 gap-1 mb-2">
          <div
            v-for="day in daysOfWeek"
            :key="day"
            :style="{
              textAlign: 'center',
              fontSize: '10px',
              color: '#9CA3AF',
              fontWeight: 500
            }"
          >
            {{ day }}
          </div>
        </div>

        <!-- Calendar Days -->
        <div
          v-for="(week, weekIndex) in calendarDays"
          :key="weekIndex"
          class="grid grid-cols-7 gap-1 mb-1"
        >
          <div
            v-for="(day, dayIndex) in week"
            :key="dayIndex"
            :style="{
              width: '34px',
              height: '34px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              fontWeight: 500,
              borderRadius: '8px',
              cursor: day ? 'pointer' : 'default',
              background: selectedDate === day ? '#597EFF' : 'transparent',
              color: selectedDate === day ? '#FFFFFF' : (day === 31 && weekIndex === 0 ? '#D1D5DB' : '#1A1F2E'),
              position: 'relative'
            }"
            @click="day && (selectedDate = day)"
          >
            {{ day || '' }}
            <div
              v-if="day && selectedDate === day"
              :style="{
                position: 'absolute',
                bottom: '3px',
                width: '3px',
                height: '3px',
                borderRadius: '50%',
                background: '#FFFFFF'
              }"
            />
          </div>
        </div>
      </div>

      <!-- Schedule List -->
      <div v-if="selectedDate" :style="{ flex: 1, overflowY: 'auto' }">
        <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '12px' }">
          일정
        </div>
        <div
          v-for="schedule in schedules"
          :key="schedule.id"
          :style="{
            padding: '10px',
            borderRadius: '8px',
            background: '#F9FAFB',
            marginBottom: '6px',
            borderLeft: schedule.color !== 'transparent' ? `3px solid ${schedule.color}` : 'none'
          }"
        >
          <div :style="{ fontSize: '10px', color: '#6B7280', marginBottom: '3px' }">
            {{ schedule.date }}
          </div>
          <div :style="{ fontSize: '11px', color: '#1A1F2E', fontWeight: 500 }">
            {{ schedule.title }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

interface Schedule {
  id: string
  date: string
  title: string
  color: string
}

const selectedDate = ref<number | null>(new Date().getDate())
const currentYear = ref<number>(new Date().getFullYear())
const currentMonthIndex = ref<number>(new Date().getMonth())

function formatMonthYear(monthIndex: number, year: number): string {
  const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December']
  return `${monthNames[monthIndex]} ${year}`
}

const currentMonth = ref(formatMonthYear(currentMonthIndex.value, currentYear.value))
const selectedPeriod = ref('Month')

const periods = ['Day', 'Week', 'Month', 'Year']

const stats = [
  { label: 'CO₂ 배출량', value: '592k' },
  { label: '탄소 절감량', value: '3.5k' },
  { label: '탄소 크레딧', value: '2.9k' },
  { label: '예측 정확도', value: '9.5k' },
]

const emissionsChartRef = ref<HTMLElement | null>(null)
let emissionsChart: any = null
let echartsMod: any = null

function getEmissionsOption(): any {
  const categories = getCategoriesForPeriod(selectedPeriod.value)
  const { wire, mobile } = getEmissionsSeriesForPeriod(selectedPeriod.value)

  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: categories },
    yAxis: { type: 'value' },
    series: [
      {
        name: 'Direct',
        type: 'line',
        stack: 'total',
        smooth: true,
        areaStyle: {},
        emphasis: { focus: 'series' },
        data: wire
      },
      {
        name: 'Indirect',
        type: 'line',
        stack: 'total',
        smooth: true,
        areaStyle: {},
        emphasis: { focus: 'series' },
        data: mobile
      }
    ]
  }
}

async function initEmissionsChart() {
  if (!emissionsChartRef.value) return
  if (!echartsMod) {
    echartsMod = await import('echarts')
  }
  emissionsChart = echartsMod.init(emissionsChartRef.value)
  emissionsChart.setOption(getEmissionsOption())
}

function disposeEmissionsChart() {
  if (emissionsChart) {
    emissionsChart.dispose()
    emissionsChart = null
  }
}

function handleResize() {
  emissionsChart?.resize()
  carbonCandleChart?.resize()
}

onMounted(() => {
  initEmissionsChart()
  initCarbonCandleChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  disposeEmissionsChart()
  disposeCarbonCandleChart()
})

watch(() => selectedPeriod.value, () => {
  emissionsChart?.setOption(getEmissionsOption())
  carbonCandleChart?.setOption(getCarbonCandleOption())
})

// Carbon credit candlestick chart
const carbonCandleChartRef = ref<HTMLElement | null>(null)
let carbonCandleChart: any = null

function getCarbonCandleOption(): any {
  const categories = getCategoriesForPeriod(selectedPeriod.value)
  const ohlc = getCandleDataForPeriod(selectedPeriod.value)
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: true,
      axisLine: { onZero: false }
    },
    yAxis: { type: 'value', scale: true },
    series: [
      {
        type: 'candlestick',
        data: ohlc,
        itemStyle: {
          color: '#10B981',
          color0: '#EF4444',
          borderColor: '#10B981',
          borderColor0: '#EF4444'
        }
      }
    ]
  }
}

async function initCarbonCandleChart() {
  if (!carbonCandleChartRef.value) return
  if (!echartsMod) {
    echartsMod = await import('echarts')
  }
  carbonCandleChart = echartsMod.init(carbonCandleChartRef.value)
  carbonCandleChart.setOption(getCarbonCandleOption())
}

function disposeCarbonCandleChart() {
  if (carbonCandleChart) {
    carbonCandleChart.dispose()
    carbonCandleChart = null
  }
}

function getCategoriesForPeriod(period: string): string[] {
  if (period === 'Day') {
    return Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`)
  }
  if (period === 'Week') {
    return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  }
  if (period === 'Month') {
    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  }
  return ['2020', '2021', '2022', '2023', '2024']
}

function getEmissionsSeriesForPeriod(period: string): { wire: number[]; mobile: number[] } {
  const cats = getCategoriesForPeriod(period)
  const len = cats.length
  const wire = Array.from({ length: len }, (_, i) => 60 + Math.round(20 * Math.sin(i / 2) + (i % 5)))
  const mobile = Array.from({ length: len }, (_, i) => 40 + Math.round(15 * Math.cos(i / 3) + ((i + 2) % 4)))
  return { wire, mobile }
}

function getCandleDataForPeriod(period: string): number[][] {
  const cats = getCategoriesForPeriod(period)
  const len = cats.length
  let base = 75
  return Array.from({ length: len }, (_, i) => {
    const open = base + ((i % 2 === 0) ? 0 : -1)
    const close = open + (i % 3 === 0 ? 2 : -2 + (i % 2))
    const low = Math.min(open, close) - 2
    const high = Math.max(open, close) + 3
    base = close
    return [open, close, low, high]
  })
}

const accountData = [
  { name: 'Jan', value: 80 },
  { name: 'Feb', value: 95 },
  { name: 'Mar', value: 110 },
  { name: 'Apr', value: 85 },
  { name: 'May', value: 75 },
]

const realtimeData = [
  { value: 30 }, { value: 45 }, { value: 35 }, { value: 55 },
  { value: 48 }, { value: 60 }, { value: 52 }, { value: 45 }
]

const visitsData = [
  { value: 20 }, { value: 35 }, { value: 45 }, { value: 55 },
  { value: 48 }, { value: 60 }, { value: 70 }, { value: 65 }
]

const incomeData = [
  { name: 'Jan', product: 80, subscription: 70 },
  { name: 'Feb', product: 85, subscription: 75 },
  { name: 'Mar', product: 78, subscription: 82 },
  { name: 'Apr', product: 75, subscription: 78 },
  { name: 'May', product: 70, subscription: 72 },
  { name: 'Jun', product: 68, subscription: 70 },
]

const schedules: Schedule[] = [
  { id: '1', date: '11/17일', title: '매수 시기 - 탄소 크레딧 가격 하락 예상', color: '#FF4D4F' },
  { id: '2', date: '11/29일', title: '매도 시기 - 탄소 크레딧 가격 상승 예상', color: '#597EFF' },
  { id: '3', date: '13 페이지 - 11/29일', title: '9800 예산, 3층5회 예산 수립', color: 'transparent' },
  { id: '4', date: '2/1 페이지 - 11/29일', title: '9800 예산, 3층5회 예산 수립', color: 'transparent' },
  { id: '5', date: '1/1 페이지 - 12/14일', title: '12000 예산, 3층9회 수립', color: 'transparent' },
]

const daysOfWeek = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

const calendarDays = ref<(number | null)[][]>([])

function generateCalendarDays(year: number, monthIndex: number): (number | null)[][] {
  const result: (number | null)[][] = []
  const daysInMonth = new Date(year, monthIndex + 1, 0).getDate()
  const firstDay = new Date(year, monthIndex, 1)
  // JS: 0=Sun..6=Sat -> Monday-first index
  const startIdx = (firstDay.getDay() + 6) % 7

  const cells: (number | null)[] = []
  for (let i = 0; i < startIdx; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)
  while (cells.length % 7 !== 0) cells.push(null)

  for (let i = 0; i < cells.length; i += 7) {
    result.push(cells.slice(i, i + 7))
  }
  return result
}

onMounted(() => {
  calendarDays.value = generateCalendarDays(currentYear.value, currentMonthIndex.value)
})
</script>
