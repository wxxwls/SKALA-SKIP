<template>
  <div class="document-list-container">
    <!-- Header Section -->
    <div class="header-section">
      <div class="header-top">
        <h2 class="page-title">
          문서 라이브러리
          <span class="subtitle">ESG 및 벤치마킹 문서 관리</span>
        </h2>
        <button
          class="upload-btn"
          @click="triggerFileInput"
          :disabled="isUploading"
        >
          <div class="btn-content">
            <Upload v-if="!isUploading" class="icon" />
            <RefreshCw v-else class="icon animate-spin" />
            <span>{{ isUploading ? '업로드 중...' : 'PDF 업로드' }}</span>
          </div>
          <div class="btn-glow"></div>
        </button>
        <input
          type="file"
          ref="fileInput"
          accept=".pdf"
          multiple
          @change="handleFileUpload"
          class="hidden-input"
        />
      </div>

      <!-- Controls Bar -->
      <div class="controls-bar">
        <!-- Tabs -->
        <div class="tabs-container">
          <button
            v-for="tab in documentTabs"
            :key="tab.id"
            @click="selectedDocType = tab.id"
            class="tab-btn"
            :class="{ active: selectedDocType === tab.id }"
          >
            <component :is="tab.icon" class="tab-icon" />
            {{ tab.label }}
            <span class="count-badge">{{ getDocumentCount(tab.id) }}</span>
          </button>
        </div>

        <!-- Search -->
        <div class="search-container">
          <Search class="search-icon" />
          <input
            type="text"
            v-model="searchQuery"
            placeholder="문서 검색..."
            class="search-input"
          />
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="content-area">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>문서 불러오는 중...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredDocuments.length === 0" class="empty-state">
        <div class="empty-illustration">
          <FileText class="empty-icon" />
          <div class="empty-circle"></div>
        </div>
        <h3>문서가 없습니다</h3>
        <p>{{ searchQuery ? '다른 검색어로 시도해 보세요' : '시작하려면 PDF를 업로드하세요' }}</p>
      </div>

      <!-- Document Grid -->
      <div v-else class="document-grid">
        <div
          v-for="doc in filteredDocuments"
          :key="doc.id"
          class="document-card"
        >
          <div class="card-header">
            <div class="file-icon-wrapper" :class="doc.type">
              <FileText class="file-icon" />
            </div>
            <div class="card-actions">
              <button class="action-btn delete" @click.stop="deleteDocument(doc.id)">
                <Trash2 class="icon" />
              </button>
            </div>
          </div>

          <div class="card-body">
            <h3 class="doc-title" :title="doc.name">{{ doc.name }}</h3>
            <div class="doc-meta">
              <span class="file-size">{{ formatFileSize(doc.size) }}</span>
              <span class="separator">•</span>
              <span class="upload-date">{{ formatDate(doc.uploadedAt) }}</span>
            </div>
          </div>

          <div class="card-footer">
            <div class="status-badge" :class="doc.status">
              <div class="status-dot"></div>
              {{ getStatusLabel(doc.status) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Action Bar -->
    <div class="footer-bar" :class="{ visible: pendingCount > 0 }">
      <div class="footer-content">
        <span class="pending-info">
          <span class="count">{{ pendingCount }}</span>개 문서 분석 대기 중
        </span>
        <button
          @click="startEmbedding"
          :disabled="isEmbedding"
          class="process-btn"
        >
          <Database v-if="!isEmbedding" class="icon" />
          <RefreshCw v-else class="icon animate-spin" />
          {{ isEmbedding ? '처리 중...' : '분석 시작' }}
        </button>
      </div>
    </div>

    <!-- Progress Modal -->
    <Transition name="fade">
      <div v-if="isEmbedding" class="modal-overlay">
        <div class="progress-modal">
          <div class="modal-header">
            <div class="spinner-ring"></div>
            <h3>문서 분석 중</h3>
            <p>벡터 데이터베이스에 처리 및 임베딩 중</p>
          </div>
          <div class="modal-body">
            <div class="progress-info">
              <span>{{ embeddingProgress.current }} / {{ embeddingProgress.total }}</span>
              <span class="percent">{{ Math.round(embeddingProgress.percent) }}%</span>
            </div>
            <div class="progress-bar-bg">
              <div 
                class="progress-bar-fill"
                :style="{ width: `${embeddingProgress.percent}%` }"
              ></div>
            </div>
            <p class="current-file">{{ embeddingProgress.currentFile }}</p>
          </div>
        </div>
      </div>
    </Transition>
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

const documentTabs: Array<{ id: 'esg' | 'benchmark'; label: string; icon: typeof BookOpen }> = [
  { id: 'esg', label: 'ESG 표준', icon: markRaw(BookOpen) },
  { id: 'benchmark', label: '벤치마킹 보고서', icon: markRaw(Building2) }
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

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'embedded': return '분석 완료';
    case 'processing': return '처리 중';
    case 'pending': return '대기 중';
    default: return status;
  }
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
    month: 'long',
    day: 'numeric'
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

      const docIndex = documents.value.findIndex(d => d.id === doc.id)
      if (docIndex !== -1) {
        documents.value[docIndex].status = 'processing'
      }

      try {
        await apiClient.post(endpoint, {
          document_id: doc.id,
          document_name: doc.name
        })

        if (docIndex !== -1) {
          documents.value[docIndex].status = 'embedded'
        }
      } catch (error) {
        console.error(`Failed to embed ${doc.name}:`, error)
        if (docIndex !== -1) {
          documents.value[docIndex].status = 'embedded'
        }
      }

      await new Promise(resolve => setTimeout(resolve, 500))
    }
  } finally {
    isEmbedding.value = false
  }
}

const loadDocuments = async () => {
  isLoading.value = true

  try {
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
.document-list-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #F8F9FB;
  font-family: 'Inter', sans-serif;
  position: relative;
}

/* Header Section */
.header-section {
  padding: 32px 48px;
  background: white;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 800;
  color: #1a1a1a;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.subtitle {
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.upload-btn {
  position: relative;
  padding: 10px 24px;
  background: #FFFFFF;
  border-radius: 10px;
  border: 1px solid #E5E7EB;
  color: #1a1a1a;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  gap: 10px;
}

.upload-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
  background: #FAFAFA;
  border-color: #FF6B35;
}

.upload-btn:active {
  transform: translateY(0);
}

.btn-content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-btn .icon {
  color: #FF6B35; /* Orange accent */
  transition: transform 0.3s ease;
}

.upload-btn:hover .icon {
  transform: scale(1.1);
}

.btn-glow {
  display: none;
}

.hidden-input {
  display: none;
}

/* Controls Bar */
.controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tabs-container {
  display: flex;
  gap: 8px;
  background: #F3F4F6;
  padding: 4px;
  border-radius: 12px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: white;
  color: var(--color-primary, #FF6B35);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.count-badge {
  background: rgba(0,0,0,0.05);
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 11px;
}

.tab-btn.active .count-badge {
  background: rgba(255, 107, 53, 0.1);
  color: var(--color-primary, #FF6B35);
}

.search-container {
  position: relative;
  width: 300px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #999;
}

.search-input {
  width: 100%;
  padding: 10px 16px 10px 40px;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary, #FF6B35);
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

/* Content Area */
.content-area {
  flex: 1;
  padding: 32px 48px;
  overflow-y: auto;
}

.document-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.document-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(0,0,0,0.03);
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  overflow: hidden;
}

.document-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.06);
  border-color: rgba(255, 107, 53, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.file-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F3F4F6;
  color: #666;
}

.file-icon-wrapper.esg {
  background: rgba(255, 107, 53, 0.1);
  color: #FF6B35;
}

.file-icon-wrapper.benchmark {
  background: rgba(59, 130, 246, 0.1);
  color: #3B82F6;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #FEE2E2;
  color: #EF4444;
}

.card-body {
  flex: 1;
}

.doc-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.doc-meta {
  font-size: 12px;
  color: #888;
  display: flex;
  align-items: center;
  gap: 6px;
}

.separator {
  color: #DDD;
}

.card-footer {
  padding-top: 16px;
  border-top: 1px solid #F3F4F6;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.embedded {
  background: #ECFDF5;
  color: #059669;
}

.status-badge.pending {
  background: #FFFBEB;
  color: #D97706;
}

.status-badge.processing {
  background: #EFF6FF;
  color: #2563EB;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #666;
}

.empty-illustration {
  width: 120px;
  height: 120px;
  background: #F3F4F6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  position: relative;
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: #9CA3AF;
  z-index: 2;
}

.empty-circle {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px dashed #E5E7EB;
  animation: spin 10s linear infinite;
}

/* Footer Bar */
.footer-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: white;
  padding: 16px 48px;
  border-top: 1px solid rgba(0,0,0,0.05);
  transform: translateY(100%);
  transition: transform 0.3s ease;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.05);
}

.footer-bar.visible {
  transform: translateY(0);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.pending-info {
  font-size: 14px;
  color: #666;
}

.pending-info .count {
  font-weight: 700;
  color: var(--color-primary, #FF6B35);
}

.process-btn {
  padding: 10px 24px;
  background: #FFFFFF;
  color: #1a1a1a;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.process-btn .icon {
  color: #FF6B35;
}

.process-btn:hover {
  background: #FAFAFA;
  border-color: #FF6B35;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.progress-modal {
  background: white;
  width: 400px;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  text-align: center;
}

.modal-header {
  margin-bottom: 24px;
}

.spinner-ring {
  width: 60px;
  height: 60px;
  border: 4px solid #F3F4F6;
  border-top-color: var(--color-primary, #FF6B35);
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 1s linear infinite;
}

.progress-bar-bg {
  height: 8px;
  background: #F3F4F6;
  border-radius: 4px;
  overflow: hidden;
  margin: 16px 0;
}

.progress-bar-fill {
  height: 100%;
  background: var(--color-primary, #FF6B35);
  transition: width 0.3s ease;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
