<template>
  <div
    class="w-full h-full flex flex-col"
    :style="{
      background: '#F7F8FA',
      paddingLeft: '54px'
    }"
  >
    <!-- Search Bar -->
    <div
:style="{
      background: '#FFFFFF',
      borderBottom: '1px solid #E8EAED',
      padding: '16px 40px'
    }">
      <div class="flex items-center gap-3">
        <!-- Search Input -->
        <div :style="{ flex: 1, position: 'relative', maxWidth: '500px' }">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Untied search text"
            :style="{
              width: '100%',
              padding: '10px 40px 10px 16px',
              borderRadius: '8px',
              border: '1px solid #E8EAED',
              fontSize: '14px',
              color: '#1A1F2E',
              outline: 'none'
            }"
            @keypress="handleKeyPress"
          />
          <button
            :style="{
              position: 'absolute',
              right: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              padding: '4px'
            }"
            @click="handleSearch"
          >
            <Search class="w-4 h-4" :style="{ color: '#6B7280' }" />
          </button>
        </div>

        <!-- Date Range Selector -->
        <div :style="{ position: 'relative' }">
          <select
            v-model="dateRange"
            :style="{
              padding: '10px 36px 10px 16px',
              borderRadius: '8px',
              border: '1px solid #E8EAED',
              fontSize: '14px',
              color: '#1A1F2E',
              background: '#FFFFFF',
              cursor: 'pointer',
              appearance: 'none',
              outline: 'none'
            }"
          >
            <option value="1일">1일</option>
            <option value="1주">1주</option>
            <option value="1개월">1개월</option>
            <option value="3개월">3개월</option>
            <option value="6개월">6개월</option>
            <option value="1년">1년</option>
          </select>
          <ChevronDown
            class="w-4 h-4"
            :style="{
              position: 'absolute',
              right: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#6B7280',
              pointerEvents: 'none'
            }"
          />
        </div>
      </div>
    </div>

    <!-- Category Tabs -->
    <div
:style="{
      background: '#FFFFFF',
      borderBottom: '1px solid #E8EAED',
      padding: '0 40px'
    }">
      <div class="flex gap-0">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :style="{
            padding: '16px 32px',
            fontSize: '14px',
            fontWeight: 600,
            color: selectedCategory === tab.id ? '#1A1F2E' : '#9CA3AF',
            borderTop: 'none',
            borderLeft: 'none',
            borderRight: 'none',
            borderBottom: selectedCategory === tab.id ? '3px solid #EA7F52' : '3px solid transparent',
            background: 'transparent',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }"
          @click="selectedCategory = tab.id as 'company' | 'competitor' | 'regulation'"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-y-auto" :style="{ padding: '24px 40px' }">
      <div
v-if="loading" :style="{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '200px',
        fontSize: '14px',
        color: '#6B7280'
      }">
        뉴스를 불러오는 중...
      </div>

      <template v-else>
        <!-- News Cards Grid -->
        <div class="grid grid-cols-3 gap-4 mb-8">
          <a
            v-for="item in news"
            :key="item.id"
            :href="item.url"
            target="_blank"
            rel="noopener noreferrer"
            :style="{
              background: '#FFFFFF',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid #E8EAED',
              textDecoration: 'none',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }"
            class="hover:shadow-lg"
          >
            <div
:style="{
              width: '48px',
              height: '48px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              fontSize: '18px',
              fontWeight: 700
            }">
              {{ item.source.substring(0, 2) }}
            </div>
            <div
:style="{
              fontSize: '14px',
              fontWeight: 600,
              color: '#1A1F2E',
              lineHeight: '1.4',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }">
              {{ item.title }}
            </div>
            <div
:style="{
              fontSize: '12px',
              color: '#6B7280',
              lineHeight: '1.5',
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }">
              {{ item.description }}
            </div>
          </a>
        </div>

        <!-- Headline News Section -->
        <div :style="{ marginTop: '40px' }">
          <div
:style="{
            fontSize: '18px',
            fontWeight: 700,
            color: '#1A1F2E',
            marginBottom: '20px',
            paddingBottom: '12px',
            borderBottom: '2px solid #E8EAED'
          }">
            헤드라인 뉴스
          </div>

          <div
:style="{
            background: '#E8EAED',
            borderRadius: '12px',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            gap: '20px'
          }">
            <a
              v-for="headline in headlines"
              :key="headline.id"
              :href="headline.url"
              target="_blank"
              rel="noopener noreferrer"
              :style="{
                background: '#FFFFFF',
                borderRadius: '12px',
                padding: '20px',
                display: 'flex',
                gap: '20px',
                textDecoration: 'none',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }"
              class="hover:shadow-lg"
            >
              <img
                v-if="headline.urlToImage"
                :src="headline.urlToImage"
                :alt="headline.title"
                :style="{
                  width: '200px',
                  height: '120px',
                  borderRadius: '8px',
                  objectFit: 'cover',
                  flexShrink: 0
                }"
              />
              <div :style="{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }">
                <div :style="{ display: 'inline-flex', alignItems: 'center', gap: '8px' }">
                  <div
:style="{
                    width: '32px',
                    height: '32px',
                    borderRadius: '6px',
                    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }">
                    <div :style="{ width: '20px', height: '20px', borderRadius: '4px', background: '#FFFFFF' }" />
                  </div>
                  <span :style="{ fontSize: '12px', color: '#6B7280', fontWeight: 500 }">
                    {{ headline.source }}
                  </span>
                </div>
                <div
:style="{
                  fontSize: '16px',
                  fontWeight: 600,
                  color: '#1A1F2E',
                  lineHeight: '1.4'
                }">
                  {{ headline.title }}
                </div>
                <div :style="{ fontSize: '13px', color: '#6B7280', lineHeight: '1.5' }">
                  {{ headline.description }}
                </div>
              </div>
            </a>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search, ChevronDown } from 'lucide-vue-next'

interface NewsItem {
  id: string
  title: string
  description: string
  url: string
  urlToImage: string | null
  publishedAt: string
  source: string
  category: 'company' | 'competitor' | 'regulation'
}

const selectedCategory = ref<'company' | 'competitor' | 'regulation'>('company')
const searchQuery = ref('')
const dateRange = ref('1개월')
const news = ref<NewsItem[]>([])
const headlines = ref<NewsItem[]>([])
const loading = ref(false)

const tabs = [
  { id: 'company', label: '자사' },
  { id: 'competitor', label: '타사' },
  { id: 'regulation', label: '규제' },
]

const fetchNews = async () => {
  loading.value = true
  try {
    // Mock data
    news.value = [
      {
        id: '1',
        title: '[단독] 삼성전자, \'경북 내년 2월 준공 예정...',
        description: 'SK 포기, 논란의 \'갈만별 5700억\' 성남바이오 완전한 연론, 학격 유출...',
        url: 'https://example.com/news1',
        urlToImage: null,
        publishedAt: new Date().toISOString(),
        source: '비즈니스포스트',
        category: selectedCategory.value
      },
      {
        id: '2',
        title: '[단독] 삼성전자, \'경북 내년 2월 준공 예정...',
        description: 'SK 포기, 논란의 \'갈만별 5700억\' 성남바이오 완전한 연론...',
        url: 'https://example.com/news2',
        urlToImage: null,
        publishedAt: new Date().toISOString(),
        source: '한국경제',
        category: selectedCategory.value
      },
      {
        id: '3',
        title: '[단독] 삼성전자, \'경북 내년 2월 준공 예정...',
        description: 'SK 포기, 논란의 \'갈만별 5700억\' 성남바이오 완전한 연론...',
        url: 'https://example.com/news3',
        urlToImage: null,
        publishedAt: new Date().toISOString(),
        source: '매일경제',
        category: selectedCategory.value
      }
    ]

    headlines.value = [
      {
        id: 'h1',
        title: '국내 CSP \'넥3\'·네이버·KT·NHN, AI 수혜 3분기 화장 성장…인프라 화장 \'속도\'...',
        description: '국내 클라우드서비스제공자(CSP) 3사인 네이버·KT·NHN가 올해 3분기에 사상 최대에...',
        url: 'https://example.com/headline1',
        urlToImage: 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&h=400&fit=crop',
        publishedAt: new Date().toISOString(),
        source: 'IT뉴스',
        category: 'company'
      },
      {
        id: 'h2',
        title: '"양조 전설 끝없이 이어지길"...최태원, \'톨드컵 3대째\' T1에 축전',
        description: '최태원 SK그룹 회장이 세계 최대 e스포츠 행사인 \'롤드컵\'에서 3년 첫 3연패를 자치한 T...',
        url: 'https://example.com/headline2',
        urlToImage: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&h=400&fit=crop',
        publishedAt: new Date().toISOString(),
        source: '한국일보',
        category: 'company'
      }
    ]
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchNews()
}

const handleKeyPress = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    handleSearch()
  }
}

watch(selectedCategory, () => {
  fetchNews()
}, { immediate: true })
</script>
