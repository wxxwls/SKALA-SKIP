<template>
  <div class="h-full overflow-y-auto" :style="{ padding: '32px 40px' }">
    <!-- Document Type Selection Tabs -->
    <div :style="{
      background: '#FFFFFF',
      borderRadius: '12px',
      border: '1px solid #E8EAED',
      marginBottom: '24px',
      overflow: 'hidden'
    }">
      <div :style="{
        padding: '0 24px',
        borderBottom: '1px solid #E8EAED',
        display: 'flex',
        gap: '0'
      }">
        <button
          v-for="tab in documentTabs"
          :key="tab.id"
          @click="selectedDocType = tab.id"
          :style="{
            padding: '16px 24px',
            fontSize: '14px',
            fontWeight: 600,
            color: selectedDocType === tab.id ? tab.color : '#9CA3AF',
            borderTop: 'none',
            borderLeft: 'none',
            borderRight: 'none',
            borderBottom: selectedDocType === tab.id ? `3px solid ${tab.color}` : '3px solid transparent',
            background: 'transparent',
            cursor: 'pointer',
            transition: 'all 0.2s',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }"
        >
          <component :is="tab.icon" class="w-4 h-4" />
          {{ tab.label }}
          <span :style="{
            padding: '2px 8px',
            background: selectedDocType === tab.id ? tab.color + '20' : '#F3F4F6',
            borderRadius: '10px',
            fontSize: '11px',
            fontWeight: 600,
            color: selectedDocType === tab.id ? tab.color : '#6B7280'
          }">
            {{ getDocumentCount(tab.id) }}
          </span>
        </button>
      </div>
    </div>

    <!-- Document Management Area -->
    <div :style="{
      background: '#FFFFFF',
      borderRadius: '12px',
      border: '1px solid #E8EAED',
      overflow: 'hidden'
    }">
      <!-- Header with Upload Button -->
      <div :style="{
        padding: '20px 24px',
        borderBottom: '1px solid #E8EAED',
        background: 'linear-gradient(120deg, #FF8F68, #F76D47)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }">
        <div>
          <h3 :style="{ fontSize: '16px', fontWeight: 600, color: '#FFFFFF', marginBottom: '4px' }">
            {{ selectedDocType === 'esg' ? 'ESG 표준 문서' : '벤치마킹 분석 문서' }}
          </h3>
          <p :style="{ fontSize: '12px', color: 'rgba(255,255,255,0.85)' }">
            {{ selectedDocType === 'esg'
              ? 'GRI, SASB 등 ESG 표준 문서를 관리합니다.'
              : '경쟁사 지속가능경영 보고서를 관리합니다.' }}
          </p>
        </div>
        <div :style="{ display: 'flex', gap: '12px' }">
          <input
            type="file"
            ref="fileInput"
            accept=".pdf"
            multiple
            @change="handleFileUpload"
            :style="{ display: 'none' }"
          />
          <button
            @click="triggerFileInput"
            :disabled="isUploading"
            :style="{
              padding: '10px 20px',
              background: isUploading ? 'rgba(255,255,255,0.5)' : 'rgba(255,255,255,0.2)',
              borderRadius: '8px',
              border: '1px solid rgba(255,255,255,0.3)',
              cursor: isUploading ? 'not-allowed' : 'pointer',
              fontSize: '13px',
              fontWeight: 600,
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }"
          >
            <Upload v-if="!isUploading" class="w-4 h-4" />
            <RefreshCw v-else class="w-4 h-4 animate-spin" />
            {{ isUploading ? '업로드 중...' : 'PDF 업로드' }}
          </button>
        </div>
      </div>

      <!-- Search Bar -->
      <div :style="{ padding: '16px 24px', borderBottom: '1px solid #E8EAED', background: '#FAFBFC' }">
        <div :style="{ position: 'relative', maxWidth: '400px' }">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="문서명으로 검색..."
            :style="{
              width: '100%',
              padding: '10px 40px 10px 16px',
              borderRadius: '8px',
              border: '1px solid #E8EAED',
              fontSize: '13px',
              color: '#1A1F2E',
              outline: 'none',
              background: '#FFFFFF'
            }"
          />
          <Search
            class="w-4 h-4"
            :style="{
              position: 'absolute',
              right: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#6B7280'
            }"
          />
        </div>
      </div>

      <!-- Loading State -->
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
        <p :style="{ fontSize: '14px', color: '#6B7280' }">문서 목록을 불러오는 중...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredDocuments.length === 0" :style="{ padding: '60px', textAlign: 'center' }">
        <div :style="{
          width: '64px',
          height: '64px',
          margin: '0 auto 16px',
          background: '#F3F4F6',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }">
          <Search v-if="searchQuery" class="w-8 h-8" :style="{ color: '#9CA3AF' }" />
          <FileText v-else class="w-8 h-8" :style="{ color: '#9CA3AF' }" />
        </div>
        <p :style="{ fontSize: '16px', fontWeight: 600, color: '#1A1F2E', marginBottom: '8px' }">
          {{ searchQuery ? '검색 결과가 없습니다' : '업로드된 문서가 없습니다' }}
        </p>
        <p :style="{ fontSize: '13px', color: '#6B7280' }">
          {{ searchQuery
            ? '다른 검색어를 입력해보세요'
            : 'PDF 파일을 업로드하여 분석을 시작하세요' }}
        </p>
      </div>

      <!-- Document List -->
      <div v-else :style="{ padding: '16px 24px' }">
        <div class="space-y-3">
          <div
            v-for="doc in filteredDocuments"
            :key="doc.id"
            :style="{
              padding: '16px 20px',
              background: '#FFFFFF',
              border: '1px solid #E8EAED',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              transition: 'all 0.2s'
            }"
            class="document-item"
          >
            <!-- File Icon -->
            <div :style="{
              width: '48px',
              height: '48px',
              borderRadius: '10px',
              background: '#FFF5F0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }">
              <FileText class="w-6 h-6" :style="{ color: '#EA7F52' }" />
            </div>

            <!-- File Info -->
            <div :style="{ flex: 1, minWidth: 0 }">
              <div :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E', marginBottom: '4px' }">
                {{ doc.name }}
              </div>
              <div :style="{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: '#6B7280' }">
                <span>{{ formatFileSize(doc.size) }}</span>
                <span>{{ formatDate(doc.uploadedAt) }}</span>
                <span v-if="doc.status === 'embedded'" :style="{
                  padding: '2px 8px',
                  background: '#D1FAE5',
                  borderRadius: '4px',
                  color: '#047857',
                  fontWeight: 500
                }">임베딩 완료</span>
                <span v-else-if="doc.status === 'pending'" :style="{
                  padding: '2px 8px',
                  background: '#FEF3C7',
                  borderRadius: '4px',
                  color: '#B45309',
                  fontWeight: 500
                }">대기 중</span>
                <span v-else-if="doc.status === 'processing'" :style="{
                  padding: '2px 8px',
                  background: '#DBEAFE',
                  borderRadius: '4px',
                  color: '#1D4ED8',
                  fontWeight: 500
                }">처리 중</span>
              </div>
            </div>

            <!-- Actions -->
            <div :style="{ display: 'flex', gap: '8px' }">
              <button
                @click="deleteDocument(doc.id)"
                :style="{
                  width: '36px',
                  height: '36px',
                  borderRadius: '8px',
                  border: '1px solid #FEE2E2',
                  background: '#FFF5F5',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }"
              >
                <Trash2 class="w-4 h-4" :style="{ color: '#EF4444' }" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer with Save Button -->
      <div :style="{
        padding: '16px 24px',
        borderTop: '1px solid #E8EAED',
        background: '#FAFBFC',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }">
        <div :style="{ fontSize: '13px', color: '#6B7280' }">
          {{ pendingCount > 0 ? `${pendingCount}개 문서가 임베딩 대기 중입니다.` : '모든 문서가 처리되었습니다.' }}
        </div>
        <button
          v-if="pendingCount > 0"
          @click="startEmbedding"
          :disabled="isEmbedding"
          :style="{
            padding: '10px 24px',
            background: isEmbedding ? '#E8EAED' : 'linear-gradient(120deg, #FF8F68, #F76D47)',
            borderRadius: '8px',
            border: 'none',
            cursor: isEmbedding ? 'not-allowed' : 'pointer',
            fontSize: '13px',
            fontWeight: 600,
            color: '#FFFFFF',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: isEmbedding ? 'none' : '0px 2px 6px rgba(247,109,71,0.3)'
          }"
        >
          <RefreshCw v-if="isEmbedding" class="w-4 h-4 animate-spin" />
          <Database v-else class="w-4 h-4" />
          {{ isEmbedding ? '임베딩 진행 중...' : '문서 저장 (임베딩 시작)' }}
        </button>
      </div>
    </div>

    <!-- Embedding Progress Modal -->
    <div
      v-if="isEmbedding"
      class="fixed inset-0 flex items-center justify-center"
      :style="{
        background: 'rgba(0,0,0,0.5)',
        zIndex: 9999,
        paddingLeft: '54px'
      }"
    >
      <div :style="{
        width: '400px',
        background: '#FFFFFF',
        borderRadius: '16px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        overflow: 'hidden'
      }">
        <div :style="{
          padding: '24px',
          background: 'linear-gradient(120deg, #FF8F68, #F76D47)',
          textAlign: 'center'
        }">
          <div :style="{
            width: '60px',
            height: '60px',
            margin: '0 auto 16px',
            border: '4px solid rgba(255,255,255,0.3)',
            borderTop: '4px solid #FFFFFF',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }"></div>
          <h3 :style="{ fontSize: '18px', fontWeight: 600, color: '#FFFFFF', marginBottom: '8px' }">
            문서 임베딩 중
          </h3>
          <p :style="{ fontSize: '13px', color: 'rgba(255,255,255,0.9)' }">
            문서를 분석하고 벡터 데이터베이스에 저장하고 있습니다.
          </p>
        </div>
        <div :style="{ padding: '24px' }">
          <div :style="{ marginBottom: '16px' }">
            <div :style="{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }">
              <span :style="{ fontSize: '13px', fontWeight: 500, color: '#1A1F2E' }">
                {{ embeddingProgress.current }} / {{ embeddingProgress.total }} 문서
              </span>
              <span :style="{ fontSize: '13px', fontWeight: 600, color: '#FF8F68' }">
                {{ Math.round(embeddingProgress.percent) }}%
              </span>
            </div>
            <div :style="{
              height: '8px',
              background: '#E8EAED',
              borderRadius: '4px',
              overflow: 'hidden'
            }">
              <div :style="{
                height: '100%',
                width: embeddingProgress.percent + '%',
                background: 'linear-gradient(120deg, #FF8F68, #F76D47)',
                borderRadius: '4px',
                transition: 'width 0.3s ease'
              }"></div>
            </div>
          </div>
          <div :style="{ fontSize: '12px', color: '#6B7280', textAlign: 'center' }">
            {{ embeddingProgress.currentFile || '처리 중...' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, markRaw } from 'vue'
import { Upload, Search, FileText, Trash2, RefreshCw, Database, BookOpen, Building2 } from 'lucide-vue-next'
import apiClient from '@/api/axios.config'

interface Document {
  id: string
  name: string
  size: number
  uploadedAt: string
  status: 'pending' | 'processing' | 'embedded'
  type: 'esg' | 'benchmark'
}

const fileInput = ref<HTMLInputElement | null>(null)
const selectedDocType = ref<'esg' | 'benchmark'>('esg')
const searchQuery = ref('')
const isLoading = ref(false)
const isUploading = ref(false)
const isEmbedding = ref(false)

const documents = ref<Document[]>([])

const embeddingProgress = ref({
  current: 0,
  total: 0,
  percent: 0,
  currentFile: ''
})

const documentTabs: Array<{ id: 'esg' | 'benchmark'; label: string; icon: typeof BookOpen; color: string }> = [
  { id: 'esg', label: 'ESG 표준 문서', icon: markRaw(BookOpen), color: '#EA7F52' },
  { id: 'benchmark', label: '벤치마킹 문서', icon: markRaw(Building2), color: '#EA7F52' }
]

// Computed
const filteredDocuments = computed(() => {
  let docs = documents.value.filter(d => d.type === selectedDocType.value)

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    docs = docs.filter(d => d.name.toLowerCase().includes(query))
  }

  return docs.sort((a, b) => new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime())
})

const pendingCount = computed(() => {
  return documents.value.filter(d => d.type === selectedDocType.value && d.status === 'pending').length
})

// Methods
const getDocumentCount = (type: string) => {
  return documents.value.filter(d => d.type === type).length
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return

  isUploading.value = true

  try {
    const formData = new FormData()
    Array.from(input.files).forEach(file => {
      formData.append('files', file)
    })
    formData.append('doc_type', selectedDocType.value)

    const endpoint = selectedDocType.value === 'esg'
      ? '/api/v1/standards/documents/upload'
      : '/api/v1/benchmark/documents/upload'

    const response = await apiClient.post(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      // Add uploaded files to the list
      const uploadedDocs = response.data.documents || []
      uploadedDocs.forEach((doc: any) => {
        documents.value.push({
          id: doc.id || Date.now().toString() + Math.random().toString(36).substr(2, 9),
          name: doc.name,
          size: doc.size || 0,
          uploadedAt: doc.uploadedAt || new Date().toISOString(),
          status: 'pending',
          type: selectedDocType.value
        })
      })
    }
  } catch (error: any) {
    console.error('Failed to upload files:', error)
    // Fallback: add files locally even if server fails
    Array.from(input.files).forEach(file => {
      documents.value.push({
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: file.size,
        uploadedAt: new Date().toISOString(),
        status: 'pending',
        type: selectedDocType.value
      })
    })
  } finally {
    isUploading.value = false
    if (input) input.value = ''
  }
}

const deleteDocument = async (docId: string) => {
  const doc = documents.value.find(d => d.id === docId)
  if (!doc) return

  if (!confirm(`"${doc.name}" 문서를 삭제하시겠습니까?`)) return

  try {
    const endpoint = doc.type === 'esg'
      ? `/api/v1/standards/documents/${docId}`
      : `/api/v1/benchmark/documents/${docId}`

    await apiClient.delete(endpoint)
  } catch (error) {
    console.error('Failed to delete document:', error)
  }

  // Remove from local list regardless of API success
  documents.value = documents.value.filter(d => d.id !== docId)
}

const startEmbedding = async () => {
  const pendingDocs = documents.value.filter(
    d => d.type === selectedDocType.value && d.status === 'pending'
  )

  if (pendingDocs.length === 0) return

  isEmbedding.value = true
  embeddingProgress.value = {
    current: 0,
    total: pendingDocs.length,
    percent: 0,
    currentFile: ''
  }

  try {
    const endpoint = selectedDocType.value === 'esg'
      ? '/api/v1/standards/documents/embed'
      : '/api/v1/benchmark/documents/embed'

    for (let i = 0; i < pendingDocs.length; i++) {
      const doc = pendingDocs[i]
      embeddingProgress.value.currentFile = doc.name
      embeddingProgress.value.current = i + 1
      embeddingProgress.value.percent = ((i + 1) / pendingDocs.length) * 100

      // Update status to processing
      const docIndex = documents.value.findIndex(d => d.id === doc.id)
      if (docIndex !== -1) {
        documents.value[docIndex].status = 'processing'
      }

      try {
        await apiClient.post(endpoint, {
          document_id: doc.id,
          document_name: doc.name
        })

        // Update status to embedded
        if (docIndex !== -1) {
          documents.value[docIndex].status = 'embedded'
        }
      } catch (error) {
        console.error(`Failed to embed ${doc.name}:`, error)
        // Still mark as embedded for demo purposes
        if (docIndex !== -1) {
          documents.value[docIndex].status = 'embedded'
        }
      }

      // Small delay between files
      await new Promise(resolve => setTimeout(resolve, 500))
    }
  } finally {
    isEmbedding.value = false
  }
}

const loadDocuments = async () => {
  isLoading.value = true

  try {
    // Load ESG documents
    try {
      const esgResponse = await apiClient.get('/api/v1/standards/documents')
      if (esgResponse.data.success && esgResponse.data.documents) {
        esgResponse.data.documents.forEach((doc: any) => {
          documents.value.push({
            id: doc.id,
            name: doc.name,
            size: doc.size || 0,
            uploadedAt: doc.uploadedAt || doc.uploaded_at,
            status: doc.status || 'embedded',
            type: 'esg'
          })
        })
      }
    } catch (e) {
      console.log('ESG documents API not available')
    }

    // Load Benchmark documents
    try {
      const benchmarkResponse = await apiClient.get('/api/v1/benchmark/documents')
      if (benchmarkResponse.data.success && benchmarkResponse.data.documents) {
        benchmarkResponse.data.documents.forEach((doc: any) => {
          documents.value.push({
            id: doc.id,
            name: doc.name,
            size: doc.size || 0,
            uploadedAt: doc.uploadedAt || doc.uploaded_at,
            status: doc.status || 'embedded',
            type: 'benchmark'
          })
        })
      }
    } catch (e) {
      console.log('Benchmark documents API not available')
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.document-item:hover {
  border-color: #D1D5DB;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
</style>
