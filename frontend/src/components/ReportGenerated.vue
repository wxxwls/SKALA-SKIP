<template>
  <div class="report-editor">
    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <h3>보고서를 불러오고 있습니다</h3>
        <p>SK 지속가능경영보고서 스타일로 렌더링 중...</p>
      </div>
    </div>

    <!-- Main Layout -->
    <div class="main-layout">
      <!-- Left Sidebar: TOC -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h2>목차</h2>
          <span class="section-count">{{ tocItems.length }}개 섹션</span>
        </div>

        <nav class="toc-nav">
          <div
            v-for="(item, index) in tocItems"
            :key="index"
            class="toc-item"
            :class="{ active: activeSection === item.id, [`level-${item.level}`]: true }"
            @click="scrollToSection(item.id)"
          >
            <span class="toc-badge" :class="item.category">{{ item.category }}</span>
            <span class="toc-title">{{ item.title }}</span>
          </div>
        </nav>

        <!-- Action Buttons -->
        <div class="sidebar-actions">
          <button
            class="btn btn-ai"
            @click="generateAIReport"
            :disabled="isGenerating"
          >
            <Sparkles class="icon" />
            {{ isGenerating ? 'AI 생성 중...' : 'AI 보고서 생성' }}
          </button>
          <button v-if="generatedHTML" class="btn btn-secondary" @click="handleDownloadWord">
            <FileText class="icon" /> Word 다운로드
          </button>
          <button v-if="generatedHTML" class="btn btn-outline" @click="handlePrint">
            <Printer class="icon" /> 인쇄 / PDF
          </button>
        </div>
      </aside>

      <!-- Main Content Area -->
      <main class="content-area">
        <!-- Edit Mode (WYSIWYG) -->
        <div v-if="isEditMode" class="edit-container">
          <div class="edit-header">
            <span>보고서 편집</span>
            <div class="edit-toolbar">
              <button class="toolbar-btn" @click="execCommand('bold')" title="굵게">
                <strong>B</strong>
              </button>
              <button class="toolbar-btn" @click="execCommand('italic')" title="기울임">
                <em>I</em>
              </button>
              <button class="toolbar-btn" @click="execCommand('underline')" title="밑줄">
                <u>U</u>
              </button>
              <span class="toolbar-divider"></span>
              <button class="toolbar-btn" @click="execCommand('insertUnorderedList')" title="목록">
                •
              </button>
              <button class="toolbar-btn" @click="execCommand('insertOrderedList')" title="번호 목록">
                1.
              </button>
              <span class="toolbar-divider"></span>
              <select class="toolbar-select" @change="execHeading($event)">
                <option value="">제목 스타일</option>
                <option value="h1">제목 1</option>
                <option value="h2">제목 2</option>
                <option value="h3">제목 3</option>
                <option value="p">본문</option>
              </select>
            </div>
            <div class="edit-actions">
              <button class="btn btn-primary btn-sm" @click="saveEdit">저장</button>
              <button class="btn btn-outline btn-sm" @click="cancelEdit">취소</button>
            </div>
          </div>
          <div
            ref="wysiwygEditor"
            class="wysiwyg-editor"
            :style="contentStyles"
            contenteditable="true"
            @input="onWysiwygInput"
            v-html="editableHTML"
          ></div>
        </div>

        <!-- AI 생성 중 로딩 -->
        <div v-else-if="isGenerating" class="generating-overlay">
          <div class="generating-content">
            <div class="generating-spinner"></div>
            <h3>AI가 보고서를 작성하고 있습니다</h3>
            <p class="generating-status">{{ generatingStatus }}</p>
            <p class="generating-time">영향 중대성 5개 + 재무 중대성 5개 = 총 10개 이슈 기준 약 3~5분 소요됩니다</p>
            <div class="generating-progress">
              <div class="progress-bar" :style="{ width: generatingProgress + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="!generatedHTML && !markdownContent" class="empty-state">
          <div class="empty-content">
            <Sparkles :size="64" :style="{ color: '#8B5CF6', marginBottom: '24px' }" />
            <h3>AI 보고서를 생성해보세요</h3>
            <p>왼쪽 사이드바의 'AI 보고서 생성' 버튼을 클릭하면</p>
            <p>중대성 평가 결과를 바탕으로 보고서가 자동 생성됩니다</p>
          </div>
        </div>

        <!-- Preview Mode -->
        <div
          v-else
          ref="reportContent"
          class="report-content"
          :style="contentStyles"
          v-html="renderedHTML"
        ></div>
      </main>

      <!-- Right Panel: AI Chat -->
      <aside class="chat-panel">
        <div class="chat-header">
          <h3>AI 보고서 편집</h3>
          <p>자연어로 보고서를 수정하세요</p>
        </div>

        <div class="chat-messages" ref="chatMessages">
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="message"
            :class="msg.type"
          >
            <div class="message-bubble">{{ msg.text }}</div>
            <span class="message-time">{{ msg.time }}</span>
          </div>

          <div v-if="isProcessing" class="message bot">
            <div class="message-bubble typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <div class="quick-actions">
          <button
            v-for="action in quickActions"
            :key="action"
            class="quick-btn"
            @click="sendQuickAction(action)"
          >
            {{ action }}
          </button>
        </div>

        <div class="chat-input">
          <input
            v-model="chatInput"
            type="text"
            placeholder="수정 요청을 입력하세요..."
            @keypress.enter="sendMessage"
            :disabled="isProcessing"
          />
          <button class="send-btn" @click="sendMessage" :disabled="!chatInput.trim() || isProcessing">
            <Send class="icon" />
          </button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import { Send, Printer, FileText, Sparkles } from 'lucide-vue-next'
import { reportApi, type AIReportGenerationRequest } from '@/api/report.api'

// Types
interface Message {
  id: string
  type: 'user' | 'bot'
  text: string
  time: string
}

interface TocItem {
  id: string
  title: string
  category: string
  level: number
}

interface Styles {
  fontFamily: string
  fontSize: string
  headingColor: string
  accentColor: string
  bgColor: string
  lineHeight: string
}

// State
const isLoading = ref(true)
const isEditMode = ref(false)
const isProcessing = ref(false)
const isGenerating = ref(false)
const generatingStatus = ref('SK 지속가능경영보고서 스타일로 생성 준비 중...')
const generatingProgress = ref(0)
const activeSection = ref('')
const markdownContent = ref('')
const chatInput = ref('')
const reportContent = ref<HTMLElement | null>(null)
const chatMessages = ref<HTMLElement | null>(null)
const wysiwygEditor = ref<HTMLElement | null>(null)
const generatedHTML = ref('')
const editableHTML = ref('')

const styles = ref<Styles>({
  fontFamily: "'Noto Sans KR', sans-serif",
  fontSize: '16px',
  headingColor: '#FF7A00',
  accentColor: '#FF7A00',
  bgColor: '#FFFFFF',
  lineHeight: '1.8'
})

const messages = ref<Message[]>([
  {
    id: '1',
    type: 'bot',
    text: '안녕하세요! AI 보고서 편집 도우미입니다. 보고서 수정을 원하시면 말씀해주세요. 예: "기후변화 대응 섹션의 대응 전략을 더 구체적으로 작성해줘"',
    time: formatTime(new Date())
  }
])

const quickActions = ['더 전문적으로', '내용 추가', '요약해줘', 'KPI 추가', '표로 정리']

// HTML 문서에서 body 내용만 추출하는 함수
const extractBodyContent = (html: string): string => {
  // 완전한 HTML 문서인 경우 body 내용만 추출
  if (html.includes('<!DOCTYPE') || html.includes('<html')) {
    // body 태그 내용 추출
    const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i)
    if (bodyMatch) {
      return bodyMatch[1]
    }
    // body 태그가 없으면 html 태그 내용에서 head 제거 후 반환
    const htmlMatch = html.match(/<html[^>]*>([\s\S]*?)<\/html>/i)
    if (htmlMatch) {
      let content = htmlMatch[1]
      // head 태그 제거
      content = content.replace(/<head[^>]*>[\s\S]*?<\/head>/i, '')
      return content.trim()
    }
  }
  return html
}

// Computed
const renderedHTML = computed(() => {
  // AI 생성 HTML이 있으면 우선 표시
  if (generatedHTML.value) {
    return extractBodyContent(generatedHTML.value)
  }

  if (!markdownContent.value) return ''

  marked.setOptions({
    breaks: true,
    gfm: true
  })

  return marked.parse(markdownContent.value) as string
})

const contentStyles = computed(() => ({
  fontFamily: styles.value.fontFamily,
  fontSize: styles.value.fontSize,
  backgroundColor: styles.value.bgColor,
  lineHeight: styles.value.lineHeight,
  '--heading-color': styles.value.headingColor,
  '--accent-color': styles.value.accentColor
}))

// AI 보고서 섹션 저장용
const aiReportSections = ref<Array<{
  issue_id: string
  issue_name: string
  category: string
  materiality_type: 'impact' | 'financial'
  priority_rank: number
}>>([])

const tocItems = computed<TocItem[]>(() => {
  // AI 보고서 섹션이 있으면 해당 섹션 기반 TOC 생성
  if (aiReportSections.value.length > 0) {
    const items: TocItem[] = []

    // 영향 중대성 헤더
    const impactSections = aiReportSections.value.filter(s => s.materiality_type === 'impact')
    if (impactSections.length > 0) {
      items.push({
        id: 'impact-section',
        title: 'I. 영향 중대성 (Impact)',
        category: 'ESG',
        level: 1
      })
      impactSections.forEach((section) => {
        items.push({
          id: `impact-${section.issue_id}`,
          title: `${section.priority_rank}. ${section.issue_name}`,
          category: section.category,
          level: 2
        })
      })
    }

    // 재무 중대성 헤더
    const financialSections = aiReportSections.value.filter(s => s.materiality_type === 'financial')
    if (financialSections.length > 0) {
      items.push({
        id: 'financial-section',
        title: 'II. 재무 중대성 (Financial)',
        category: 'ESG',
        level: 1
      })
      financialSections.forEach((section) => {
        items.push({
          id: `financial-${section.issue_id}`,
          title: `${section.priority_rank}. ${section.issue_name}`,
          category: section.category,
          level: 2
        })
      })
    }

    return items
  }

  // 기존 마크다운 기반 TOC
  if (!markdownContent.value) return []

  const items: TocItem[] = []
  const lines = markdownContent.value.split('\n')
  let idx = 0

  for (const line of lines) {
    const h1 = line.match(/^# (.+)$/)
    const h2 = line.match(/^## (.+)$/)

    if (h1 && h1[1] !== '목차') {
      items.push({
        id: `section-${idx++}`,
        title: h1[1],
        category: getCategory(h1[1]),
        level: 1
      })
    } else if (h2) {
      items.push({
        id: `section-${idx++}`,
        title: h2[1],
        category: getCategory(h2[1]),
        level: 2
      })
    }
  }

  return items
})

// Functions
function formatTime(date: Date): string {
  return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

function getCategory(title: string): string {
  if (['환경', '기후', '에너지', 'Environmental'].some(k => title.includes(k))) return 'E'
  if (['사회', '인재', '안전', '서비스', '정보보안', 'Social'].some(k => title.includes(k))) return 'S'
  if (['거버넌스', '지배구조', '윤리', '이사회', '리스크', 'Governance'].some(k => title.includes(k))) return 'G'
  return 'ESG'
}

function scrollToSection(sectionId: string) {
  activeSection.value = sectionId

  // AI 보고서인 경우 - 섹션 ID나 data-issue-id로 찾기
  if (aiReportSections.value.length > 0) {
    // 먼저 id로 찾기
    let element = reportContent.value?.querySelector(`#${sectionId}`)

    // id로 못 찾으면 data-issue-id로 찾기
    if (!element) {
      const issueId = sectionId.replace('impact-', '').replace('financial-', '')
      element = reportContent.value?.querySelector(`[data-issue-id="${issueId}"]`)
    }

    // 섹션 헤더로 찾기
    if (!element && (sectionId === 'impact-section' || sectionId === 'financial-section')) {
      element = reportContent.value?.querySelector(`#${sectionId}`)
    }

    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      return
    }
  }

  // 기존 마크다운 기반 스크롤
  const idx = parseInt(sectionId.replace('section-', ''))
  const headings = reportContent.value?.querySelectorAll('h1, h2')
  if (headings && headings[idx]) {
    headings[idx].scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// TODO: toggleEditMode - restore when edit button is implemented in template
/* function toggleEditMode() {
  if (isEditMode.value) {
    saveEdit()
  } else {
    // WYSIWYG 편집 모드로 전환
    if (generatedHTML.value) {
      editableHTML.value = generatedHTML.value
      addBotMessage('편집 모드입니다. 텍스트를 직접 선택하여 수정할 수 있습니다.')
    } else if (markdownContent.value) {
      // 마크다운을 HTML로 변환하여 WYSIWYG 편집
      editableHTML.value = renderedHTML.value
      addBotMessage('편집 모드입니다. 텍스트를 직접 선택하여 수정할 수 있습니다.')
    } else {
      editableHTML.value = '<p>여기에 내용을 입력하세요...</p>'
    }
    isEditMode.value = true
  }
} */

// WYSIWYG 편집기 관련 함수들
function execCommand(command: string, value?: string) {
  document.execCommand(command, false, value)
  wysiwygEditor.value?.focus()
}

function execHeading(event: Event) {
  const select = event.target as HTMLSelectElement
  const value = select.value
  if (value) {
    document.execCommand('formatBlock', false, value)
    wysiwygEditor.value?.focus()
  }
  select.value = ''
}

function onWysiwygInput() {
  // 편집 내용이 변경될 때마다 실시간으로 저장
  if (wysiwygEditor.value) {
    editableHTML.value = wysiwygEditor.value.innerHTML
  }
}

function saveEdit() {
  // WYSIWYG 편집기의 최신 내용 가져오기
  if (wysiwygEditor.value) {
    editableHTML.value = wysiwygEditor.value.innerHTML
  }

  // HTML로 저장
  generatedHTML.value = editableHTML.value
  // 마크다운 내용 초기화 (HTML 모드 사용)
  markdownContent.value = ''

  addBotMessage('보고서가 저장되었습니다.')
  isEditMode.value = false
}

function cancelEdit() {
  isEditMode.value = false
}

// TODO: applyStyles - styles are applied reactively via computed contentStyles
// function applyStyles() { }

function addBotMessage(text: string) {
  messages.value.push({
    id: Date.now().toString(),
    type: 'bot',
    text,
    time: formatTime(new Date())
  })
  scrollChat()
}

async function sendMessage() {
  if (!chatInput.value.trim() || isProcessing.value) return

  const userText = chatInput.value.trim()
  chatInput.value = ''

  messages.value.push({
    id: Date.now().toString(),
    type: 'user',
    text: userText,
    time: formatTime(new Date())
  })

  scrollChat()
  isProcessing.value = true

  // Simulate AI response
  setTimeout(() => {
    let response = `"${userText}" 요청을 처리했습니다. 직접 편집 모드에서 세부 내용을 확인하실 수 있습니다.`

    if (userText.includes('전문적') || userText.includes('formal')) {
      response = '보고서 어조를 더 전문적으로 수정하였습니다.'
    } else if (userText.includes('추가') || userText.includes('상세')) {
      response = '요청하신 내용을 추가하였습니다.'
    } else if (userText.includes('요약')) {
      response = '해당 섹션을 요약하였습니다.'
    }

    addBotMessage(response)
    isProcessing.value = false
  }, 1500)
}

function sendQuickAction(action: string) {
  chatInput.value = action
  sendMessage()
}

async function scrollChat() {
  await nextTick()
  if (chatMessages.value) {
    chatMessages.value.scrollTop = chatMessages.value.scrollHeight
  }
}

// TODO: handleDownloadHTML - restore when HTML download button is implemented
// function handleDownloadHTML() { ... see SKIP 2 version for full implementation }

// TODO: handleDownloadMarkdown - restore when markdown download button is implemented
// function handleDownloadMarkdown() { ... }

// TODO: downloadFile - restore when download functions are implemented
// function downloadFile(content: string, filename: string, type: string) {
//   const blob = new Blob([content], { type: `${type};charset=utf-8` })
//   const url = URL.createObjectURL(blob)
//   const a = document.createElement('a')
//   a.href = url
//   a.download = filename
//   document.body.appendChild(a)
//   a.click()
//   document.body.removeChild(a)
//   URL.revokeObjectURL(url)
// }

function handleDownloadWord() {
  if (!renderedHTML.value) return

  // HTML을 Word 호환 형식으로 변환
  const wordHTML = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office'
          xmlns:w='urn:schemas-microsoft-com:office:word'
          xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
      <meta charset='utf-8'>
      <title>ESG 중대성 이슈 보고서</title>
      <style>
        body {
          font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
          line-height: 1.8;
          padding: 40px;
        }
        h1 {
          color: ${styles.value.headingColor};
          border-bottom: 3px solid ${styles.value.headingColor};
          padding-bottom: 16px;
          margin: 48px 0 24px;
          font-size: 24pt;
        }
        h2 {
          border-left: 4px solid ${styles.value.accentColor};
          padding-left: 16px;
          margin: 40px 0 20px;
          font-size: 18pt;
        }
        h3 {
          font-size: 14pt;
          margin: 32px 0 16px;
        }
        p { margin: 16px 0; }
        table {
          width: 100%;
          border-collapse: collapse;
          margin: 24px 0;
        }
        th, td {
          padding: 12px;
          border: 1px solid #ddd;
          text-align: left;
        }
        th {
          background: #f5f5f5;
          font-weight: bold;
        }
        ul, ol { margin: 16px 0; padding-left: 24px; }
        li { margin: 8px 0; }
      </style>
    </head>
    <body>
      ${renderedHTML.value}
    </body>
    </html>
  `

  const blob = new Blob(['\ufeff', wordHTML], {
    type: 'application/msword;charset=utf-8'
  })

  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'ESG_중대성_이슈_보고서_2025.doc'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  addBotMessage('Word 문서가 다운로드되었습니다.')
}

function handlePrint() {
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>SK AX 2025 지속가능경영보고서</title>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
          body { font-family: 'Noto Sans KR', sans-serif; line-height: 1.8; padding: 40px; }
          h1 { color: ${styles.value.headingColor}; border-bottom: 2px solid ${styles.value.headingColor}; padding-bottom: 12px; }
          h2 { border-left: 3px solid ${styles.value.accentColor}; padding-left: 12px; }
          table { width: 100%; border-collapse: collapse; margin: 20px 0; }
          th, td { padding: 12px; border: 1px solid #ddd; }
          th { background: #f5f5f5; }
          @media print { body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
        </style>
      </head>
      <body>${renderedHTML.value}</body>
      </html>
    `)
    printWindow.document.close()
    printWindow.print()
  }
}

async function loadReport() {
  isLoading.value = true

  // 초기에는 빈 보고서로 시작
  markdownContent.value = ''
  generatedHTML.value = ''

  isLoading.value = false
}

// AI 보고서 생성 함수
// 영향 중대성 상위 5개 + 재무 중대성 상위 5개 = 총 10개 이슈 처리
async function generateAIReport() {
  isGenerating.value = true
  generatingProgress.value = 0
  generatingStatus.value = 'API 서버에 요청 전송 중...'

  // 기존 내용 비우기
  markdownContent.value = ''
  generatedHTML.value = ''

  addBotMessage('AI 보고서를 생성하고 있습니다... 영향 중대성 5개 + 재무 중대성 5개 = 총 10개 이슈 기준 약 3~5분 소요됩니다.')

  // 로컬 스토리지에서 중대성 평가 결과 가져오기
  const assessmentDataStr = localStorage.getItem('materialityAssessment')
  if (!assessmentDataStr) {
    addBotMessage('중대성 평가 결과를 찾을 수 없습니다. 먼저 중대성 평가를 완료해주세요.')
    isGenerating.value = false
    return
  }

  const assessmentData = JSON.parse(assessmentDataStr)
  const allIssues = assessmentData.issues || assessmentData.topIssues || []

  if (allIssues.length === 0) {
    addBotMessage('이슈 데이터가 없습니다.')
    isGenerating.value = false
    return
  }

  // 영향 중대성 기준 상위 5개 이슈 (averageImpact 기준 정렬)
  const impactTop5 = [...allIssues]
    .sort((a: any, b: any) => (b.averageImpact || 0) - (a.averageImpact || 0))
    .slice(0, 5)

  // 재무 중대성 기준 상위 5개 이슈 (averageFinancial 기준 정렬)
  const financialTop5 = [...allIssues]
    .sort((a: any, b: any) => (b.averageFinancial || 0) - (a.averageFinancial || 0))
    .slice(0, 5)

  // 중복 제거한 전체 이슈 목록
  const uniqueIssueIds = new Set([
    ...impactTop5.map((i: any) => i.id),
    ...financialTop5.map((i: any) => i.id)
  ])
  const uniqueIssues = allIssues.filter((i: any) => uniqueIssueIds.has(i.id))

  const totalIssues = 10 // 영향 5개 + 재무 5개

  // 진행률 시뮬레이션
  const progressInterval = setInterval(() => {
    if (generatingProgress.value < 90) {
      generatingProgress.value += 1
      const currentIssue = Math.min(totalIssues, Math.floor(generatingProgress.value / 9) + 1)
      if (currentIssue <= 5) {
        const issue = impactTop5[currentIssue - 1]
        generatingStatus.value = `[영향 중대성] ${currentIssue}/5 생성 중... (${issue?.name || ''})`
      } else {
        const issue = financialTop5[currentIssue - 6]
        generatingStatus.value = `[재무 중대성] ${currentIssue - 5}/5 생성 중... (${issue?.name || ''})`
      }
    }
  }, 3000)

  try {
    // 중대성 평가 결과 기반 요청 데이터 생성
    // 회사명은 SK AX로 고정
    const request: AIReportGenerationRequest = {
      company_context: {
        company_id: 'sk-ax',
        company_name: 'SK AX',
        industry: assessmentData.industry || 'IT 서비스/AI/클라우드',
        year: assessmentData.reportYear || 2025
      },
      issues: uniqueIssues.map((issue: any) => {
        // 카테고리 변환: environment/social/governance -> E/S/G
        let category: 'E' | 'S' | 'G' | 'Cross' = 'E'
        if (issue.category === 'environment' || issue.category === 'E') category = 'E'
        else if (issue.category === 'social' || issue.category === 'S') category = 'S'
        else if (issue.category === 'governance' || issue.category === 'G') category = 'G'

        return {
          id: issue.id,
          name: issue.name,
          category: category,
          impact_score: issue.averageImpact || 0,
          financial_score: issue.averageFinancial || 0,
          is_priority: true
        }
      }),
      // 영향 중대성 상위 5개 이슈 ID
      impact_priority_issue_ids: impactTop5.map((issue: any) => issue.id),
      // 재무 중대성 상위 5개 이슈 ID
      financial_priority_issue_ids: financialTop5.map((issue: any) => issue.id),
      // KPI 데이터 (내부 데이터 없으면 빈칸 처리됨)
      kpi_data_by_issue: {},
      language: 'ko'
    }

    const response = await reportApi.generateReportDirect(request)

    clearInterval(progressInterval)

    if (response.success && response.report_html) {
      generatingProgress.value = 100
      generatingStatus.value = '보고서 생성 완료!'
      generatedHTML.value = response.report_html

      // HTML을 마크다운으로 간단히 변환하여 표시
      if (response.report_markdown) {
        markdownContent.value = response.report_markdown
      }

      // AI 보고서 섹션 정보 저장 (사이드바 목차 표시용)
      if (response.sections && response.sections.length > 0) {
        aiReportSections.value = response.sections.map(s => ({
          issue_id: s.issue_id,
          issue_name: s.issue_name,
          category: s.category,
          materiality_type: s.materiality_type,
          priority_rank: s.priority_rank
        }))
      }

      // 섹션 카운트
      const impactCount = response.sections?.filter(s => s.materiality_type === 'impact').length || 0
      const financialCount = response.sections?.filter(s => s.materiality_type === 'financial').length || 0

      addBotMessage(
        `AI 보고서가 성공적으로 생성되었습니다!\n` +
        `- 영향 중대성: ${impactCount}개 이슈\n` +
        `- 재무 중대성: ${financialCount}개 이슈\n` +
        `총 ${response.sections?.length || 0}개 이슈에 대한 분석이 포함되어 있습니다.\n` +
        `왼쪽 목차에서 각 이슈를 클릭하여 이동할 수 있습니다.`
      )
    } else {
      addBotMessage(`보고서 생성 실패: ${response.error?.message || '알 수 없는 오류'}`)
    }
  } catch (error: any) {
    clearInterval(progressInterval)
    console.error('AI 보고서 생성 오류:', error)
    addBotMessage(`보고서 생성 중 오류가 발생했습니다: ${error.message || '네트워크 오류'}`)
  } finally {
    isGenerating.value = false
  }
}

// TODO: getEmbeddedReport - default report template, restore when needed
// function getEmbeddedReport(): string { return `...embedded report markdown template...` }

// Lifecycle
onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.report-editor {
  width: 100%;
  height: 100vh;
  background: #f7f8fa;
  overflow: hidden;
}

/* Loading */
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading-content {
  background: white;
  padding: 48px;
  border-radius: 16px;
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #FF7A00;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 24px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-content h3 {
  font-size: 18px;
  color: #1a1f2e;
  margin-bottom: 8px;
}

.loading-content p {
  font-size: 14px;
  color: #6b7280;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  min-height: 400px;
  margin: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.empty-content {
  text-align: center;
  padding: 48px;
  max-width: 500px;
}

.empty-content h3 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1f2e;
  margin-bottom: 16px;
}

.empty-content p {
  font-size: 15px;
  color: #6b7280;
  line-height: 1.6;
  margin: 4px 0;
}

/* AI 생성 중 오버레이 */
.generating-overlay {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  min-height: 400px;
}

.generating-content {
  text-align: center;
  padding: 48px;
}

.generating-spinner {
  width: 64px;
  height: 64px;
  border: 5px solid #e8eaed;
  border-top: 5px solid #8B5CF6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 32px;
}

.generating-content h3 {
  font-size: 20px;
  font-weight: 700;
  color: #1a1f2e;
  margin-bottom: 12px;
}

.generating-status {
  font-size: 15px;
  color: #8B5CF6;
  font-weight: 600;
  margin-bottom: 8px;
}

.generating-time {
  font-size: 13px;
  color: #9ca3af;
  margin-bottom: 24px;
}

.generating-progress {
  width: 280px;
  height: 8px;
  background: #e8eaed;
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #8B5CF6, #6366F1);
  border-radius: 4px;
  transition: width 0.5s ease-out;
}

/* Main Layout */
.main-layout {
  display: flex;
  height: 100%;
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e8eaed;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid #e8eaed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1f2e;
}

.section-count {
  font-size: 12px;
  color: #FF7A00;
  background: #fff5f0;
  padding: 4px 10px;
  border-radius: 12px;
}

.toc-nav {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.toc-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.toc-item:hover {
  background: #f7f8fa;
}

.toc-item.active {
  background: #fff5f0;
  border-left: 3px solid #FF7A00;
}

.toc-item.level-2 {
  padding-left: 24px;
}

.toc-badge {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.toc-badge.E { background: #10b981; }
.toc-badge.S { background: #3b82f6; }
.toc-badge.G { background: #8b5cf6; }
.toc-badge.ESG { background: #FF7A00; }

.toc-title {
  font-size: 13px;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-actions {
  padding: 16px;
  border-top: 1px solid #e8eaed;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Buttons */
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn .icon {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255,122,0,0.3);
}

.btn-secondary {
  background: #6366f1;
  color: white;
}

.btn-secondary:hover {
  background: #5558e3;
}

.btn-outline {
  background: white;
  border: 1px solid #e5e7eb;
  color: #374151;
}

.btn-outline:hover {
  background: #f7f8fa;
}

.btn-sm {
  padding: 8px 14px;
  font-size: 12px;
}

.btn-ai {
  background: linear-gradient(135deg, #8B5CF6, #6366F1);
  color: white;
}

.btn-ai:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-ai:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Content Area */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Formatting Toolbar */
.formatting-toolbar {
  background: white;
  border-bottom: 1px solid #e8eaed;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-group label {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.toolbar-group select,
.toolbar-group input[type="color"] {
  padding: 6px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 12px;
  background: white;
  cursor: pointer;
}

.toolbar-group input[type="color"] {
  width: 36px;
  height: 32px;
  padding: 2px;
}

/* Edit Mode */
.edit-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  margin: 24px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid #e8eaed;
  font-weight: 600;
  color: #374151;
  flex-wrap: wrap;
  gap: 12px;
}

.edit-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  margin: 0 16px;
}

.toolbar-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.toolbar-btn:active {
  background: #e5e7eb;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: #e5e7eb;
  margin: 0 8px;
}

.toolbar-select {
  padding: 6px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 12px;
  background: white;
  cursor: pointer;
  color: #374151;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.wysiwyg-editor {
  flex: 1;
  padding: 40px;
  border: none;
  outline: none;
  overflow-y: auto;
  min-height: 400px;
}

.wysiwyg-editor:focus {
  outline: none;
}

/* WYSIWYG 에디터 내부 스타일 */
.wysiwyg-editor h1 {
  color: var(--heading-color, #FF7A00);
  font-size: 1.8em;
  font-weight: 700;
  border-bottom: 3px solid var(--heading-color, #FF7A00);
  padding-bottom: 16px;
  margin: 48px 0 24px;
}

.wysiwyg-editor h1:first-child {
  margin-top: 0;
}

.wysiwyg-editor h2 {
  color: #1a1f2e;
  font-size: 1.4em;
  font-weight: 600;
  border-left: 4px solid var(--accent-color, #FF7A00);
  padding-left: 16px;
  margin: 40px 0 20px;
}

.wysiwyg-editor h3 {
  color: #374151;
  font-size: 1.15em;
  font-weight: 600;
  margin: 32px 0 16px;
}

.wysiwyg-editor p {
  margin: 16px 0;
  color: #374151;
}

.wysiwyg-editor table {
  width: 100%;
  border-collapse: collapse;
  margin: 24px 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.wysiwyg-editor th,
.wysiwyg-editor td {
  padding: 14px 18px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.wysiwyg-editor th {
  background: linear-gradient(135deg, var(--heading-color, #FF7A00), var(--accent-color, #FF7A00));
  color: white;
  font-weight: 600;
}

.wysiwyg-editor ul,
.wysiwyg-editor ol {
  margin: 16px 0;
  padding-left: 24px;
}

.wysiwyg-editor li {
  margin: 8px 0;
  color: #374151;
}

.wysiwyg-editor strong {
  color: var(--accent-color, #FF7A00);
}

.markdown-editor {
  flex: 1;
  padding: 20px;
  border: none;
  resize: none;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.8;
  outline: none;
}

/* Report Content */
.report-content {
  flex: 1;
  overflow-y: auto;
  padding: 40px;
  background: white;
  margin: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.report-content :deep(h1) {
  color: var(--heading-color, #FF7A00);
  font-size: 1.8em;
  font-weight: 700;
  border-bottom: 3px solid var(--heading-color, #FF7A00);
  padding-bottom: 16px;
  margin: 48px 0 24px;
}

.report-content :deep(h1:first-child) {
  margin-top: 0;
}

.report-content :deep(h2) {
  color: #1a1f2e;
  font-size: 1.4em;
  font-weight: 600;
  border-left: 4px solid var(--accent-color, #FF7A00);
  padding-left: 16px;
  margin: 40px 0 20px;
}

.report-content :deep(h3) {
  color: #374151;
  font-size: 1.15em;
  font-weight: 600;
  margin: 32px 0 16px;
}

.report-content :deep(p) {
  margin: 16px 0;
  color: #374151;
}

.report-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 24px 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.report-content :deep(th),
.report-content :deep(td) {
  padding: 14px 18px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.report-content :deep(th) {
  background: linear-gradient(135deg, var(--heading-color, #FF7A00), var(--accent-color, #FF7A00));
  color: white;
  font-weight: 600;
}

.report-content :deep(tr:hover td) {
  background: #fff5f0;
}

.report-content :deep(pre) {
  background: #1a1f2e;
  color: #e8eaed;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
  margin: 20px 0;
}

.report-content :deep(code) {
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
}

.report-content :deep(pre code) {
  background: none;
  padding: 0;
}

.report-content :deep(hr) {
  border: none;
  height: 1px;
  background: linear-gradient(to right, var(--accent-color, #FF7A00), transparent);
  margin: 48px 0;
}

.report-content :deep(strong) {
  color: var(--accent-color, #FF7A00);
}

.report-content :deep(ul),
.report-content :deep(ol) {
  margin: 16px 0;
  padding-left: 24px;
}

.report-content :deep(li) {
  margin: 8px 0;
  color: #374151;
}

/* Chat Panel */
.chat-panel {
  width: 360px;
  background: white;
  border-left: 1px solid #e8eaed;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.chat-header {
  padding: 24px;
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
}

.chat-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.chat-header p {
  font-size: 12px;
  opacity: 0.9;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  max-width: 85%;
}

.message.user {
  align-self: flex-end;
}

.message.bot {
  align-self: flex-start;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 13px;
  line-height: 1.6;
}

.message.user .message-bubble {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.bot .message-bubble {
  background: #f7f8fa;
  color: #1a1f2e;
  border-bottom-left-radius: 4px;
}

.message-time {
  font-size: 10px;
  color: #9ca3af;
  margin-top: 4px;
  display: block;
}

.message.user .message-time {
  text-align: right;
}

/* Typing animation */
.typing {
  display: flex;
  gap: 4px;
  padding: 16px !important;
}

.typing span {
  width: 8px;
  height: 8px;
  background: #FF7A00;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}

.quick-actions {
  padding: 12px 16px;
  border-top: 1px solid #e8eaed;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  padding: 6px 14px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  font-size: 11px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #fff5f0;
  border-color: #FF7A00;
  color: #FF7A00;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #e8eaed;
  display: flex;
  gap: 12px;
}

.chat-input input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input input:focus {
  border-color: #FF7A00;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  background: #e5e7eb;
  cursor: not-allowed;
}

.send-btn .icon {
  width: 18px;
  height: 18px;
}

/* ==================== */
/* DIAGRAM STYLES */
/* ==================== */

/* Diagram Container */
.report-content :deep(.diagram-container) {
  margin: 32px 0;
  padding: 24px;
  background: #fafbfc;
  border-radius: 16px;
  border: 1px solid #e8eaed;
}

.report-content :deep(.diagram-title) {
  font-size: 16px;
  font-weight: 700;
  color: #1a1f2e;
  text-align: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--accent-color, #FF7A00);
}

/* Business Portfolio Grid */
.report-content :deep(.portfolio-grid) {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.report-content :deep(.portfolio-item) {
  background: white;
  border-radius: 12px;
  padding: 24px 16px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.report-content :deep(.portfolio-item:hover) {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.report-content :deep(.portfolio-icon) {
  font-size: 36px;
  margin-bottom: 12px;
}

.report-content :deep(.portfolio-name) {
  font-size: 14px;
  font-weight: 600;
  color: #1a1f2e;
  margin-bottom: 8px;
}

.report-content :deep(.portfolio-desc) {
  font-size: 12px;
  color: #6b7280;
}

/* Org Chart */
.report-content :deep(.org-structure) {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.report-content :deep(.org-level) {
  display: flex;
  justify-content: center;
  gap: 24px;
  width: 100%;
}

.report-content :deep(.org-box) {
  background: white;
  border-radius: 12px;
  padding: 16px 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  min-width: 180px;
}

.report-content :deep(.org-box.board) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
}

.report-content :deep(.org-box.management) {
  background: #1a1f2e;
  color: white;
}

.report-content :deep(.org-box.team) {
  background: white;
  border: 2px solid #e8eaed;
}

.report-content :deep(.org-title) {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 4px;
}

.report-content :deep(.org-subtitle) {
  font-size: 11px;
  opacity: 0.8;
}

.report-content :deep(.org-desc) {
  font-size: 11px;
  margin-top: 8px;
  opacity: 0.9;
}

.report-content :deep(.org-connector) {
  width: 2px;
  height: 24px;
  background: #d1d5db;
}

/* Process Flow */
.report-content :deep(.process-steps) {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  overflow-x: auto;
  padding: 16px 0;
}

.report-content :deep(.process-step) {
  flex: 1;
  min-width: 160px;
  background: white;
  border-radius: 12px;
  padding: 20px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.report-content :deep(.step-number) {
  display: inline-block;
  width: 32px;
  height: 32px;
  line-height: 32px;
  text-align: center;
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 12px;
}

.report-content :deep(.step-title) {
  font-size: 13px;
  font-weight: 700;
  color: #1a1f2e;
  margin-bottom: 12px;
}

.report-content :deep(.step-content) {
  font-size: 11px;
  color: #6b7280;
  line-height: 1.6;
}

.report-content :deep(.step-content p) {
  margin: 6px 0;
}

.report-content :deep(.process-arrow) {
  font-size: 24px;
  color: var(--accent-color, #FF7A00);
  padding-top: 40px;
  font-weight: bold;
}

/* Roadmap */
.report-content :deep(.roadmap-timeline) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 24px 0;
}

.report-content :deep(.roadmap-item) {
  text-align: center;
  min-width: 140px;
}

.report-content :deep(.roadmap-year) {
  font-size: 24px;
  font-weight: 800;
  color: var(--accent-color, #FF7A00);
  margin-bottom: 12px;
}

.report-content :deep(.roadmap-item.highlight .roadmap-year) {
  font-size: 28px;
}

.report-content :deep(.roadmap-content) {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.report-content :deep(.roadmap-item.highlight .roadmap-content) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
}

.report-content :deep(.roadmap-goal) {
  font-size: 13px;
  font-weight: 600;
}

.report-content :deep(.roadmap-arrow) {
  font-size: 28px;
  color: #d1d5db;
}

/* Materiality */
.report-content :deep(.materiality-box) {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.report-content :deep(.mission-box) {
  background: linear-gradient(135deg, #1a1f2e, #374151);
  color: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
}

.report-content :deep(.mission-title) {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 12px;
}

.report-content :deep(.mission-text) {
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.9;
}

.report-content :deep(.dual-materiality) {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.report-content :deep(.materiality-item) {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.report-content :deep(.materiality-item.impact) {
  border-top: 4px solid #10b981;
}

.report-content :deep(.materiality-item.financial) {
  border-top: 4px solid #3b82f6;
}

.report-content :deep(.materiality-label) {
  font-size: 16px;
  font-weight: 700;
  color: #1a1f2e;
}

.report-content :deep(.materiality-sub) {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 12px;
}

.report-content :deep(.materiality-desc) {
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
}

.report-content :deep(.result-box) {
  text-align: center;
}

.report-content :deep(.arrow-down) {
  font-size: 32px;
  color: var(--accent-color, #FF7A00);
  margin-bottom: 8px;
}

.report-content :deep(.result-text) {
  display: inline-block;
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
  padding: 12px 32px;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 700;
}

/* Assessment Result */
.report-content :deep(.result-columns) {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.report-content :deep(.result-column) {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.report-content :deep(.result-column.impact) {
  border-top: 4px solid #10b981;
}

.report-content :deep(.result-column.financial) {
  border-top: 4px solid #3b82f6;
}

.report-content :deep(.column-header) {
  font-size: 14px;
  font-weight: 700;
  color: #1a1f2e;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e8eaed;
}

.report-content :deep(.rank-item) {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
  font-size: 13px;
  color: #374151;
}

.report-content :deep(.rank-item:last-child) {
  border-bottom: none;
}

.report-content :deep(.rank) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--accent-color, #FF7A00);
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
}

/* Risk Management */
.report-content :deep(.risk-structure) {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.report-content :deep(.risk-level) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  width: 100%;
}

.report-content :deep(.risk-label) {
  font-size: 12px;
  color: #6b7280;
  font-weight: 600;
  padding: 4px 12px;
  background: #f3f4f6;
  border-radius: 12px;
}

.report-content :deep(.risk-box) {
  background: white;
  border-radius: 8px;
  padding: 12px 20px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.report-content :deep(.risk-box.highlight) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
}

.report-content :deep(.risk-box .sub) {
  font-size: 11px;
  font-weight: 400;
  opacity: 0.8;
}

.report-content :deep(.risk-connector) {
  width: 2px;
  height: 20px;
  background: #d1d5db;
}

.report-content :deep(.risk-teams) {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  justify-content: center;
}

.report-content :deep(.team-group) {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

.report-content :deep(.team-header) {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 8px;
}

.report-content :deep(.team-box) {
  display: inline-block;
  background: #f3f4f6;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  margin: 4px;
}

.report-content :deep(.team-list) {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.report-content :deep(.team-list span) {
  font-size: 11px;
  color: #374151;
  background: #f9fafb;
  padding: 4px 8px;
  border-radius: 4px;
}

/* Social Value */
.report-content :deep(.sv-structure) {
  display: flex;
  align-items: center;
  gap: 32px;
}

.report-content :deep(.sv-center) {
  flex-shrink: 0;
}

.report-content :deep(.sv-circle) {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
}

.report-content :deep(.sv-title) {
  font-size: 16px;
  font-weight: 700;
}

.report-content :deep(.sv-subtitle) {
  font-size: 12px;
  opacity: 0.9;
}

.report-content :deep(.sv-branches) {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-content :deep(.sv-branch) {
  display: flex;
  align-items: center;
  gap: 16px;
}

.report-content :deep(.branch-label) {
  width: 120px;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  flex-shrink: 0;
}

.report-content :deep(.branch-items) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
}

.report-content :deep(.branch-items .item) {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.report-content :deep(.branch-items .item.orange) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
}

.report-content :deep(.branch-items .item.white) {
  background: white;
  border: 1px solid #e8eaed;
  color: #374151;
}

.report-content :deep(.branch-items .item.beige) {
  background: #fef3c7;
  color: #92400e;
}

.report-content :deep(.branch-items.full) {
  flex: 1;
}

.report-content :deep(.branch-items.full .item) {
  width: 100%;
  text-align: center;
}

/* Value-up 다이어그램 */
.report-content :deep(.value-up) {
  background: linear-gradient(135deg, #fff5f0 0%, #ffffff 100%);
  border: 2px solid #FF8F68;
}

.report-content :deep(.value-up-structure) {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.report-content :deep(.value-row) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.report-content :deep(.value-row.main) {
  padding: 20px;
}

.report-content :deep(.value-box) {
  padding: 16px 24px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  text-align: center;
  min-width: 160px;
}

.report-content :deep(.value-box.primary) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
  box-shadow: 0 4px 12px rgba(247, 109, 71, 0.3);
}

.report-content :deep(.value-box.target) {
  background: linear-gradient(135deg, #1a1f2e, #2d3748);
  color: white;
  box-shadow: 0 4px 12px rgba(26, 31, 46, 0.3);
}

.report-content :deep(.value-plus) {
  font-size: 24px;
  font-weight: 700;
  color: #FF8F68;
}

.report-content :deep(.value-arrow) {
  font-size: 24px;
  font-weight: 700;
  color: #1a1f2e;
}

.report-content :deep(.value-details) {
  display: flex;
  gap: 40px;
  justify-content: center;
  margin-top: 16px;
}

.report-content :deep(.value-column) {
  flex: 1;
  max-width: 400px;
}

.report-content :deep(.value-column-title) {
  font-weight: 700;
  font-size: 15px;
  color: #F76D47;
  margin-bottom: 12px;
  text-align: center;
  padding-bottom: 8px;
  border-bottom: 2px solid #FF8F68;
}

.report-content :deep(.value-items) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.report-content :deep(.value-item) {
  background: white;
  border: 1px solid #e8eaed;
  border-left: 4px solid #FF8F68;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
}

/* 주주환원 다이어그램 */
.report-content :deep(.shareholder) {
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
  border: 2px solid #3b82f6;
}

.report-content :deep(.shareholder-structure) {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.report-content :deep(.shareholder-row) {
  display: flex;
  align-items: stretch;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
}

.report-content :deep(.shareholder-box) {
  padding: 20px 24px;
  border-radius: 12px;
  text-align: center;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.report-content :deep(.shareholder-box.main) {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.report-content :deep(.shareholder-box.sub) {
  background: white;
  border: 2px solid #3b82f6;
  color: #1e40af;
}

.report-content :deep(.shareholder-box .title) {
  font-weight: 700;
  font-size: 16px;
}

.report-content :deep(.shareholder-box .desc) {
  font-size: 13px;
  opacity: 0.9;
}

.report-content :deep(.shareholder-box .highlight) {
  font-size: 20px;
  font-weight: 800;
  color: #FF8F68;
}

.report-content :deep(.shareholder-connector) {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #3b82f6;
}

.report-content :deep(.shareholder-timeline) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.report-content :deep(.timeline-item) {
  padding: 12px 20px;
  border-radius: 8px;
  text-align: center;
  min-width: 120px;
}

.report-content :deep(.timeline-item.past) {
  background: #e2e8f0;
  color: #64748b;
}

.report-content :deep(.timeline-item.current) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
  font-weight: 700;
}

.report-content :deep(.timeline-item.future) {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.report-content :deep(.timeline-arrow) {
  font-size: 20px;
  color: #94a3b8;
}

/* KPI 카드 스타일 */
.report-content :deep(.kpi-grid) {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.report-content :deep(.kpi-card) {
  background: white;
  border: 1px solid #e8eaed;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  transition: all 0.2s ease;
}

.report-content :deep(.kpi-card:hover) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.report-content :deep(.kpi-card .kpi-label) {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
}

.report-content :deep(.kpi-card .kpi-value) {
  font-size: 28px;
  font-weight: 800;
  color: #FF8F68;
}

.report-content :deep(.kpi-card .kpi-unit) {
  font-size: 14px;
  color: #9ca3af;
  margin-left: 4px;
}

.report-content :deep(.kpi-card .kpi-change) {
  font-size: 12px;
  margin-top: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.report-content :deep(.kpi-card .kpi-change.positive) {
  background: #dcfce7;
  color: #16a34a;
}

.report-content :deep(.kpi-card .kpi-change.negative) {
  background: #fee2e2;
  color: #dc2626;
}

/* 핵심 이슈 분석 표 */
.report-content :deep(.issue-analysis-table) {
  margin: 32px 0;
  overflow-x: auto;
}

.report-content :deep(.analysis-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  overflow: hidden;
}

.report-content :deep(.analysis-table thead) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
}

.report-content :deep(.analysis-table th) {
  padding: 16px 12px;
  text-align: center;
  font-weight: 600;
  font-size: 12px;
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  vertical-align: middle;
}

.report-content :deep(.analysis-table th:last-child) {
  border-right: none;
}

.report-content :deep(.analysis-table tbody tr) {
  border-bottom: 1px solid #e8eaed;
}

.report-content :deep(.analysis-table tbody tr:nth-child(even)) {
  background: #fafbfc;
}

.report-content :deep(.analysis-table tbody tr:hover) {
  background: #fff5f0;
}

.report-content :deep(.analysis-table td) {
  padding: 16px 12px;
  vertical-align: top;
  border-right: 1px solid #e8eaed;
  line-height: 1.6;
}

.report-content :deep(.analysis-table td:last-child) {
  border-right: none;
}

.report-content :deep(.analysis-table .issue-name) {
  font-weight: 700;
  color: #1a1f2e;
  background: #fff9f6;
  min-width: 100px;
}

.report-content :deep(.analysis-table .impact-level) {
  text-align: center;
  font-size: 16px;
  letter-spacing: 2px;
}

.report-content :deep(.analysis-table .impact-level.high) {
  color: #FF8F68;
}

.report-content :deep(.analysis-table .impact-level.medium) {
  color: #3b82f6;
}

.report-content :deep(.analysis-table .impact-level.low) {
  color: #9ca3af;
}

.report-content :deep(.table-footnote) {
  margin-top: 12px;
  font-size: 12px;
  color: #6b7280;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
}

/* 이슈 상세 카드 */
.report-content :deep(.issue-detail-card) {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  margin: 24px 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8eaed;
}

.report-content :deep(.issue-section) {
  display: flex;
  border-bottom: 1px solid #e8eaed;
}

.report-content :deep(.issue-section:last-child) {
  border-bottom: none;
}

.report-content :deep(.section-label) {
  flex-shrink: 0;
  width: 140px;
  padding: 20px 24px;
  background: #f9fafb;
  font-weight: 700;
  font-size: 14px;
  color: #1a1f2e;
  border-right: 1px solid #e8eaed;
  display: flex;
  align-items: flex-start;
}

.report-content :deep(.section-content) {
  flex: 1;
  padding: 20px 24px;
}

.report-content :deep(.section-content p) {
  margin: 0 0 12px 0;
  line-height: 1.8;
  font-size: 14px;
  color: #374151;
}

.report-content :deep(.section-content p:last-child) {
  margin-bottom: 0;
}

.report-content :deep(.section-content ul) {
  margin: 8px 0;
  padding-left: 20px;
}

.report-content :deep(.section-content li) {
  margin: 6px 0;
  line-height: 1.6;
  font-size: 14px;
  color: #374151;
}

.report-content :deep(.impact-summary) {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e8eaed;
}

.report-content :deep(.impact-item) {
  font-size: 13px;
  color: #6b7280;
  margin: 6px 0;
}

.report-content :deep(.impact-item strong) {
  color: #FF8F68;
}

.report-content :deep(.detail-link) {
  display: inline-block;
  margin-top: 12px;
  color: #FF8F68;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.report-content :deep(.detail-link:hover) {
  color: #F76D47;
}

/* 발생 영향과 통제 타이틀 스타일 */
.report-content :deep(h2) {
  position: relative;
}

.report-content :deep(h2:has(+ .issue-detail-card)) {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 32px;
}

/* 번호 배지 스타일 */
.report-content :deep(.issue-number) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 700;
}

/* ========================================
   Backend Report Styles (AI Generated)
   ======================================== */

/* Report Container */
.report-content :deep(.report-container) {
  max-width: 100%;
  margin: 0 auto;
  padding: 0;
  background: #FFFFFF;
}

/* Report Header */
.report-content :deep(.report-header) {
  text-align: center;
  margin-bottom: 40px;
  border-bottom: 3px solid #FF7A00;
  padding-bottom: 24px;
}

.report-content :deep(.report-title) {
  font-size: 32px;
  font-weight: 700;
  color: #1A1F2E;
  margin: 0;
}

.report-content :deep(.report-subtitle) {
  font-size: 18px;
  color: #6B7280;
  margin-top: 12px;
}

/* TOC in Report (hidden since sidebar has TOC) */
.report-content :deep(.toc) {
  display: none;
}

/* Section Header */
.report-content :deep(.section-header) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
  padding: 24px 32px;
  border-radius: 12px;
  margin: 48px 0 32px 0;
}

.report-content :deep(.section-header.financial) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
}

.report-content :deep(.section-header h2) {
  margin: 0;
  font-size: 24px;
  color: white;
  border: none;
  padding: 0;
}

.report-content :deep(.section-header p) {
  margin: 8px 0 0 0;
  opacity: 0.9;
  font-size: 14px;
}

/* Analysis Section */
.report-content :deep(.analysis-section) {
  margin: 32px 0;
}

.report-content :deep(.analysis-section h3) {
  font-size: 18px;
  color: #1A1F2E;
  margin: 0 0 16px 0;
  border-left: 4px solid #FF7A00;
  padding-left: 12px;
}

.report-content :deep(.analysis-section.financial h3) {
  border-left-color: #FF7A00;
}

/* Analysis Table */
.report-content :deep(.analysis-table-container) {
  overflow-x: auto;
}

.report-content :deep(.analysis-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border-radius: 12px;
  overflow: hidden;
}

.report-content :deep(.analysis-table thead) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
}

.report-content :deep(.analysis-table.financial thead) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
}

.report-content :deep(.analysis-table th) {
  padding: 14px 10px;
  text-align: center;
  font-weight: 600;
  font-size: 11px;
  border-right: 1px solid rgba(255,255,255,0.2);
  color: white;
  background: inherit;
}

.report-content :deep(.analysis-table th:last-child) {
  border-right: none;
}

.report-content :deep(.analysis-table td) {
  padding: 12px 10px;
  vertical-align: middle;
  border-bottom: 1px solid #E8EAED;
  border-right: 1px solid #E8EAED;
  text-align: center;
  font-size: 12px;
}

.report-content :deep(.analysis-table td:last-child) {
  border-right: none;
}

.report-content :deep(.analysis-table td.issue-name) {
  font-weight: 600;
  color: #1A1F2E;
  text-align: left;
  background: #FFF9F6;
  min-width: 120px;
}

.report-content :deep(.analysis-table.financial td.issue-name) {
  background: #FFF9F6;
}

.report-content :deep(.analysis-table tbody tr:hover) {
  background: #FAFBFC;
}

.report-content :deep(.no-data) {
  color: #9CA3AF;
  font-style: italic;
  font-size: 10px;
}

/* Issue Detail Cards */
.report-content :deep(.impact-issue-detail),
.report-content :deep(.financial-issue-detail) {
  margin: 32px 0;
}

.report-content :deep(.issue-title) {
  font-size: 18px;
  font-weight: 700;
  color: #1A1F2E;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.report-content :deep(.priority-badge) {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #FF8F68, #F76D47);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.report-content :deep(.priority-badge.financial) {
  background: linear-gradient(135deg, #FF8F68, #F76D47);
}

.report-content :deep(.category-badge) {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
}

.report-content :deep(.category-E) {
  background: #D1FAE5;
  color: #059669;
}

.report-content :deep(.category-S) {
  background: #DBEAFE;
  color: #2563EB;
}

.report-content :deep(.category-G) {
  background: #EDE9FE;
  color: #7C3AED;
}

/* Issue Detail Card Structure */
.report-content :deep(.issue-detail-card) {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  border: 1px solid #E8EAED;
}

.report-content :deep(.issue-detail-card.impact) {
  border-left: 4px solid #FF7A00;
}

.report-content :deep(.issue-detail-card.financial) {
  border-left: 4px solid #FF7A00;
}

.report-content :deep(.issue-section) {
  display: flex;
  border-bottom: 1px solid #E8EAED;
}

.report-content :deep(.issue-section:last-child) {
  border-bottom: none;
}

.report-content :deep(.section-label) {
  flex-shrink: 0;
  width: 140px;
  padding: 20px 24px;
  background: #F9FAFB;
  font-weight: 700;
  font-size: 14px;
  color: #1A1F2E;
  border-right: 1px solid #E8EAED;
}

.report-content :deep(.section-content) {
  flex: 1;
  padding: 20px 24px;
}

.report-content :deep(.section-content p) {
  margin: 0 0 12px 0;
  line-height: 1.8;
  font-size: 14px;
  color: #374151;
}

.report-content :deep(.section-content p:last-child) {
  margin-bottom: 0;
}

.report-content :deep(.section-content ul),
.report-content :deep(.section-content ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.report-content :deep(.section-content li) {
  margin: 6px 0;
  line-height: 1.6;
  font-size: 14px;
  color: #374151;
}

/* Impact Summary */
.report-content :deep(.impact-summary) {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #E8EAED;
}

.report-content :deep(.impact-item) {
  font-size: 13px;
  color: #6B7280;
  margin: 6px 0;
}

.report-content :deep(.impact-item strong) {
  color: #FF7A00;
}

/* Risk/Opportunity Box */
.report-content :deep(.risk-opportunity-summary) {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 16px;
}

.report-content :deep(.risk-box) {
  padding: 16px;
  border-radius: 8px;
  background: #FEF2F2;
  border: 1px solid #FECACA;
}

.report-content :deep(.opportunity-box) {
  padding: 16px;
  border-radius: 8px;
  background: #F0FDF4;
  border: 1px solid #BBF7D0;
}

.report-content :deep(.risk-box h5) {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #DC2626;
}

.report-content :deep(.opportunity-box h5) {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #16A34A;
}

.report-content :deep(.risk-item),
.report-content :deep(.opp-item) {
  font-size: 12px;
  color: #374151;
  margin: 6px 0;
}

/* KPI List */
.report-content :deep(.kpi-list) {
  margin-top: 16px;
}

.report-content :deep(.kpi-list h4) {
  font-size: 14px;
  color: #374151;
  margin: 0 0 12px 0;
}

.report-content :deep(.kpi-list table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.report-content :deep(.kpi-list th),
.report-content :deep(.kpi-list td) {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #E8EAED;
}

.report-content :deep(.kpi-list th) {
  background: #F7F8FA;
  font-weight: 600;
  color: #374151;
}

/* Conclusion */
.report-content :deep(.conclusion) {
  background: linear-gradient(135deg, #FFF9F5, #FFFFFF);
  padding: 32px;
  border-radius: 12px;
  border: 1px solid #FFE5D6;
  margin-top: 48px;
}

.report-content :deep(.conclusion h3) {
  color: #FF7A00;
  margin: 0 0 16px 0;
  font-size: 20px;
}

.report-content :deep(.conclusion p) {
  margin: 0 0 12px 0;
  color: #374151;
  line-height: 1.8;
}

/* Print Styles */
@media print {
  .report-content :deep(.section-header),
  .report-content :deep(.issue-detail-card) {
    break-inside: avoid;
    page-break-inside: avoid;
  }
}
</style>
