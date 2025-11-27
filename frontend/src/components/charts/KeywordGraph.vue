<template>
  <div ref="chartRef" :style="{ width: '100%', height: props.height || '180px' }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

interface KeywordNode {
  name: string
  value: number
  category: string
}

interface KeywordLink {
  source: string
  target: string
  value?: number
}

const props = defineProps<{
  keywords: KeywordNode[]
  links?: KeywordLink[]
  height?: string
}>()

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const categoryColors: Record<string, string> = {
  E: '#10B981',  // 환경 - 녹색
  S: '#3B82F6',  // 사회 - 파랑
  G: '#F59E0B',  // 지배구조 - 주황
  central: '#FF6B6B',  // 중심 키워드 - 빨강
  default: '#6B7280'
}

const initChart = () => {
  if (!chartRef.value) return
  if (!props.keywords || props.keywords.length === 0) return

  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)

  const categories = [
    { name: 'E', itemStyle: { color: categoryColors.E } },
    { name: 'S', itemStyle: { color: categoryColors.S } },
    { name: 'G', itemStyle: { color: categoryColors.G } },
    { name: 'central', itemStyle: { color: categoryColors.central } }
  ]

  // 노드 데이터 생성 - 크기 조정하여 더 많은 노드 표시
  const maxValue = Math.max(...props.keywords.map(k => k.value))
  const nodes = props.keywords.map((keyword, index) => {
    const normalizedValue = (keyword.value / maxValue) * 100
    const symbolSize = Math.min(Math.max(normalizedValue * 0.5 + 15, 18), 55)
    const fontSize = Math.min(Math.max(normalizedValue * 0.08 + 9, 9), 13)

    return {
      id: keyword.name,
      name: keyword.name,
      symbolSize,
      value: keyword.value,
      category: keyword.category === 'E' ? 0 : keyword.category === 'S' ? 1 : keyword.category === 'G' ? 2 : 3,
      itemStyle: {
        color: categoryColors[keyword.category] || categoryColors.default,
        shadowBlur: 5,
        shadowColor: 'rgba(0,0,0,0.15)'
      },
      label: {
        show: true,
        fontSize,
        color: '#333',
        fontWeight: index < 5 ? 'bold' : 'normal'
      },
      x: undefined,
      y: undefined
    }
  })

  // 링크 데이터 생성 (없으면 자동 생성)
  const links = props.links || generateLinks(props.keywords)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `<strong>${params.name}</strong><br/>언급횟수: ${params.value}회`
        }
        return ''
      }
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        animation: true,
        data: nodes,
        links: links,
        categories: categories,
        roam: false,
        draggable: true,
        force: {
          repulsion: 350,
          gravity: 0.15,
          edgeLength: [60, 180],
          layoutAnimation: true,
          friction: 0.6
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 3
          }
        },
        lineStyle: {
          color: '#E5E7EB',
          width: 1.5,
          curveness: 0.1
        },
        label: {
          show: true,
          position: 'inside',
          formatter: '{b}'
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 중심 키워드와 연결된 링크 자동 생성
const generateLinks = (keywords: KeywordNode[]): KeywordLink[] => {
  if (keywords.length === 0) return []

  const links: KeywordLink[] = []
  const centralKeyword = keywords[0]

  // 중심 키워드와 다른 키워드 연결
  for (let i = 1; i < keywords.length; i++) {
    links.push({
      source: centralKeyword.name,
      target: keywords[i].name,
      value: keywords[i].value
    })
  }

  // 같은 카테고리 키워드끼리 연결
  for (let i = 1; i < keywords.length; i++) {
    for (let j = i + 1; j < keywords.length; j++) {
      if (keywords[i].category === keywords[j].category && Math.random() > 0.5) {
        links.push({
          source: keywords[i].name,
          target: keywords[j].name,
          value: Math.min(keywords[i].value, keywords[j].value)
        })
      }
    }
  }

  return links
}

const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

watch(() => props.keywords, () => {
  initChart()
}, { deep: true })
</script>
