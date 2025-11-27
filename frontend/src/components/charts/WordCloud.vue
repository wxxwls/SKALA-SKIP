<template>
  <div ref="chartRef" :style="{ width: '100%', height: props.height || '140px' }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'

interface WordItem {
  name: string
  value: number
  category?: string
}

const props = defineProps<{
  words: WordItem[]
  height?: string
}>()

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const categoryColors: Record<string, string> = {
  E: '#10B981',
  S: '#3B82F6',
  G: '#F59E0B',
  default: '#6B7280'
}

const getRandomColor = (category?: string) => {
  if (category && categoryColors[category]) {
    return categoryColors[category]
  }
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
  return colors[Math.floor(Math.random() * colors.length)]
}

const initChart = () => {
  if (!chartRef.value) return
  if (!props.words || props.words.length === 0) return

  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)

  const data = props.words.map(word => ({
    name: word.name,
    value: word.value,
    textStyle: {
      color: getRandomColor(word.category)
    }
  }))

  const option: echarts.EChartsOption = {
    tooltip: {
      show: true,
      formatter: (params: any) => {
        return `<strong>${params.name}</strong><br/>언급횟수: ${params.value}회`
      }
    },
    series: [
      {
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '95%',
        height: '95%',
        sizeRange: [14, 42],
        rotationRange: [-30, 30],
        rotationStep: 10,
        gridSize: 6,
        drawOutOfBound: false,
        layoutAnimation: true,
        textStyle: {
          fontFamily: 'Pretendard, -apple-system, BlinkMacSystemFont, sans-serif',
          fontWeight: 'bold'
        },
        emphasis: {
          textStyle: {
            shadowBlur: 15,
            shadowColor: 'rgba(0, 0, 0, 0.4)'
          }
        },
        data: data
      }
    ]
  }

  chartInstance.setOption(option)
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

watch(() => props.words, () => {
  initChart()
}, { deep: true })
</script>
