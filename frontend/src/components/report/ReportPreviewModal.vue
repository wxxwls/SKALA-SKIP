<script setup lang="ts">
/**
 * ReportPreviewModal - ESG 보고서 미리보기 모달
 *
 * 기능:
 * - AI 생성 ESG 보고서 미리보기
 * - 챗봇 기반 보고서 수정
 * - 편집 모드
 * - 다운로드/인쇄
 *
 * TODO: CLAUDE.md 규칙에 따라 apiClient 직접 호출을 Store Action으로 리팩토링 필요
 */
import { ref, computed, watch, nextTick } from 'vue';
import { X, Download, RefreshCw, Printer, CheckCircle, AlertCircle, Send, MessageSquare } from 'lucide-vue-next';
import apiClient from '@/api/axios.config';

// Props
const props = defineProps<{
  isOpen: boolean;
  reportHtml: string;
  reportMarkdown?: string;
  isLoading: boolean;
  metadata?: {
    issueCount: number;
    priorityIssueIds: string[];
    processingTimeMs: number;
    aiModel: string;
  } | null;
  generationStatus?: {
    status: string;
    message: string;
  } | null;
  companyName?: string;
}>();

// Emits
const emit = defineEmits<{
  'close': [];
  'regenerate': [];
  'download': [];
  'update:reportHtml': [html: string];
  'update:reportMarkdown': [markdown: string];
}>();

// Local state
const iframeRef = ref<HTMLIFrameElement | null>(null);
const showChatbot = ref(true);
const chatInput = ref('');
const chatMessages = ref<Array<{ role: 'user' | 'assistant'; message: string }>>([
  { role: 'assistant', message: '보고서를 생성한 후 아래 명령으로 수정할 수 있습니다.' }
]);
const isChatLoading = ref(false);
const currentMarkdown = ref('');

// Example commands
const exampleCommands = [
  'ESG Letter를 더 전문적인 어조로 수정해줘',
  '환경 섹션에 탄소배출 저감 목표를 2030년 50% 감축으로 수정해줘',
  '거버넌스 섹션에 이사회 독립성 강화 내용 추가해줘',
  '기후변화 대응 섹션의 KPI 테이블을 더 상세하게 작성해줘'
];

// Computed
const statusColor = computed(() => {
  if (!props.generationStatus) return '#6B7280';
  switch (props.generationStatus.status) {
    case 'COMPLETED': return '#10B981';
    case 'FAILED': return '#EF4444';
    case 'GENERATING': return '#F59E0B';
    default: return '#6B7280';
  }
});

const statusIcon = computed(() => {
  if (!props.generationStatus) return null;
  return props.generationStatus.status === 'COMPLETED' ? CheckCircle : AlertCircle;
});

// Methods
function handleClose() {
  emit('close');
}

function handleRegenerate() {
  emit('regenerate');
}

function handleDownload() {
  emit('download');
}

function handlePrint() {
  if (iframeRef.value?.contentWindow) {
    iframeRef.value.contentWindow.print();
  }
}

function toggleChatbot() {
  showChatbot.value = !showChatbot.value;
}

function useExample(command: string) {
  chatInput.value = command;
}

// TODO: CLAUDE.md - 이 함수는 Store Action으로 이동 필요
async function sendChatMessage() {
  const instruction = chatInput.value.trim();
  if (!instruction || !currentMarkdown.value) return;

  // Add user message
  chatMessages.value.push({ role: 'user', message: instruction });
  chatInput.value = '';
  isChatLoading.value = true;

  try {
    // Call AI service to modify report
    const response = await apiClient.post('/internal/v1/reports/modify', {
      instruction,
      current_report: currentMarkdown.value,
      company_name: props.companyName
    });

    if (response.data.success && response.data.modified_report) {
      // Update report
      currentMarkdown.value = response.data.modified_report;
      emit('update:reportMarkdown', response.data.modified_report);

      if (response.data.modified_html) {
        emit('update:reportHtml', response.data.modified_html);
        updateIframe(response.data.modified_html);
      }

      chatMessages.value.push({
        role: 'assistant',
        message: '보고서가 수정되었습니다. 변경사항이 실시간으로 반영되었습니다.'
      });
    } else {
      chatMessages.value.push({
        role: 'assistant',
        message: `오류: ${response.data.message || '수정 실패'}`
      });
    }
  } catch (error) {
    console.error('Report modification failed:', error);
    chatMessages.value.push({
      role: 'assistant',
      message: `오류: ${error instanceof Error ? error.message : '보고서 수정 중 오류가 발생했습니다'}`
    });
  } finally {
    isChatLoading.value = false;
    await nextTick();
    scrollChatToBottom();
  }
}

function scrollChatToBottom() {
  const chatContainer = document.getElementById('chatMessagesContainer');
  if (chatContainer) {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
}

function updateIframe(html: string) {
  if (iframeRef.value) {
    const doc = iframeRef.value.contentDocument;
    if (doc) {
      doc.open();
      doc.write(html);
      doc.close();
    }
  }
}

// Watch for HTML changes to update iframe
watch(() => props.reportHtml, (newHtml) => {
  if (newHtml) {
    updateIframe(newHtml);
  }
}, { immediate: true });

// Watch for markdown changes
watch(() => props.reportMarkdown, (newMarkdown) => {
  if (newMarkdown) {
    currentMarkdown.value = newMarkdown;
  }
}, { immediate: true });

// Handle enter key in chat input
function handleChatKeypress(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendChatMessage();
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50 backdrop-blur-sm"
          @click="handleClose"
        />

        <!-- Modal Content -->
        <div
          :style="{
            position: 'relative',
            width: '95vw',
            maxWidth: '1600px',
            height: '92vh',
            background: '#FFFFFF',
            borderRadius: '16px',
            boxShadow: '0 25px 50px rgba(0, 0, 0, 0.25)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }"
        >
          <!-- Header -->
          <div
            :style="{
              padding: '16px 24px',
              borderBottom: '1px solid #E8EAED',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: '#FFFFFF',
              flexShrink: 0
            }"
          >
            <div>
              <h2 :style="{ fontSize: '20px', fontWeight: 600, color: '#1A1F2E', margin: 0 }">
                ESG 보고서 미리보기
              </h2>
              <div
                v-if="metadata"
                :style="{ fontSize: '13px', color: '#6B7280', marginTop: '4px', display: 'flex', gap: '16px' }"
              >
                <span>이슈 {{ metadata.issueCount }}개</span>
                <span>처리시간 {{ (metadata.processingTimeMs / 1000).toFixed(1) }}초</span>
                <span>AI: {{ metadata.aiModel }}</span>
              </div>
            </div>

            <div :style="{ display: 'flex', alignItems: 'center', gap: '12px' }">
              <!-- Status Badge -->
              <div
                v-if="generationStatus"
                :style="{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  borderRadius: '20px',
                  background: `${statusColor}15`,
                  color: statusColor,
                  fontSize: '13px',
                  fontWeight: 500
                }"
              >
                <component :is="statusIcon" class="w-4 h-4" />
                {{ generationStatus.message }}
              </div>

              <!-- Chatbot Toggle -->
              <button
                @click="toggleChatbot"
                :style="{
                  padding: '8px 16px',
                  background: showChatbot ? '#FF7A00' : '#F3F4F6',
                  borderRadius: '8px',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500,
                  color: showChatbot ? '#FFFFFF' : '#374151',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }"
              >
                <MessageSquare class="w-4 h-4" />
                수정 챗봇
              </button>

              <!-- Action Buttons -->
              <button
                @click="handleRegenerate"
                :disabled="isLoading"
                :style="{
                  padding: '8px 16px',
                  background: '#F3F4F6',
                  borderRadius: '8px',
                  border: 'none',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  fontSize: '13px',
                  fontWeight: 500,
                  color: '#374151',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  opacity: isLoading ? 0.5 : 1
                }"
              >
                <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': isLoading }" />
                재생성
              </button>

              <button
                @click="handlePrint"
                :style="{
                  padding: '8px 16px',
                  background: '#F3F4F6',
                  borderRadius: '8px',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500,
                  color: '#374151',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }"
              >
                <Printer class="w-4 h-4" />
                인쇄
              </button>

              <button
                @click="handleDownload"
                :style="{
                  padding: '8px 16px',
                  background: 'linear-gradient(120deg, #FF8F68, #F76D47)',
                  borderRadius: '8px',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#FFFFFF',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }"
              >
                <Download class="w-4 h-4" />
                다운로드
              </button>

              <!-- Close Button -->
              <button
                @click="handleClose"
                :style="{
                  padding: '8px',
                  background: 'transparent',
                  borderRadius: '8px',
                  border: 'none',
                  cursor: 'pointer',
                  color: '#6B7280'
                }"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Main Content Area -->
          <div :style="{ flex: 1, display: 'flex', overflow: 'hidden' }">
            <!-- Report Preview -->
            <div :style="{ flex: 1, overflow: 'hidden', background: '#F7F8FA' }">
              <!-- Loading State -->
              <div
                v-if="isLoading"
                :style="{
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '16px'
                }"
              >
                <div
                  :style="{
                    width: '48px',
                    height: '48px',
                    border: '4px solid #E8EAED',
                    borderTopColor: '#FF7A00',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }"
                />
                <p :style="{ fontSize: '16px', color: '#6B7280' }">
                  AI가 보고서를 생성하고 있습니다...
                </p>
                <p :style="{ fontSize: '13px', color: '#9CA3AF' }">
                  내부 데이터를 기반으로 SK 지속가능경영보고서 스타일로 작성 중
                </p>
              </div>

              <!-- Report Preview (iframe) -->
              <iframe
                v-else
                ref="iframeRef"
                :style="{
                  width: '100%',
                  height: '100%',
                  border: 'none'
                }"
                title="ESG Report Preview"
              />
            </div>

            <!-- Chatbot Panel -->
            <div
              v-if="showChatbot"
              :style="{
                width: '380px',
                borderLeft: '1px solid #E8EAED',
                background: '#FFFFFF',
                display: 'flex',
                flexDirection: 'column',
                flexShrink: 0
              }"
            >
              <!-- Chatbot Header -->
              <div
                :style="{
                  padding: '16px 20px',
                  borderBottom: '2px solid #FF7A00',
                  fontWeight: 600,
                  fontSize: '15px',
                  color: '#1A1F2E'
                }"
              >
                보고서 수정 챗봇
              </div>

              <!-- Chat Messages -->
              <div
                id="chatMessagesContainer"
                :style="{
                  flex: 1,
                  overflowY: 'auto',
                  padding: '16px',
                  background: '#F7F8FA'
                }"
              >
                <div
                  v-for="(msg, index) in chatMessages"
                  :key="index"
                  :style="{
                    marginBottom: '12px',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    fontSize: '13px',
                    lineHeight: '1.5',
                    background: msg.role === 'user' ? '#FFFFFF' : '#FFF5ED',
                    border: msg.role === 'user' ? '1px solid #E8EAED' : '1px solid #FF7A00',
                    marginLeft: msg.role === 'user' ? '20px' : '0',
                    marginRight: msg.role === 'assistant' ? '20px' : '0'
                  }"
                >
                  <div
                    :style="{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: '#6B7280',
                      marginBottom: '6px',
                      textTransform: 'uppercase'
                    }"
                  >
                    {{ msg.role === 'user' ? 'You' : 'Assistant' }}
                  </div>
                  {{ msg.message }}
                </div>

                <!-- Loading indicator -->
                <div
                  v-if="isChatLoading"
                  :style="{
                    padding: '12px 16px',
                    borderRadius: '8px',
                    background: '#FFF5ED',
                    border: '1px solid #FF7A00',
                    marginRight: '20px'
                  }"
                >
                  <div :style="{ fontSize: '13px', color: '#6B7280' }">
                    수정 중...
                  </div>
                </div>
              </div>

              <!-- Chat Input -->
              <div
                :style="{
                  padding: '16px',
                  borderTop: '1px solid #E8EAED',
                  background: '#FFFFFF'
                }"
              >
                <div :style="{ fontSize: '11px', color: '#6B7280', marginBottom: '8px' }">
                  예시 명령어를 클릭하거나 직접 입력하세요
                </div>

                <div :style="{ display: 'flex', gap: '8px', marginBottom: '12px' }">
                  <input
                    v-model="chatInput"
                    type="text"
                    placeholder="예: 기후변화 주제를 더 자세히 작성해줘"
                    :style="{
                      flex: 1,
                      padding: '12px 14px',
                      border: '1px solid #E8EAED',
                      borderRadius: '8px',
                      fontSize: '13px',
                      outline: 'none'
                    }"
                    @keypress="handleChatKeypress"
                  />
                  <button
                    @click="sendChatMessage"
                    :disabled="isChatLoading || !chatInput.trim()"
                    :style="{
                      padding: '12px 16px',
                      background: '#FF7A00',
                      color: '#FFFFFF',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: isChatLoading ? 'not-allowed' : 'pointer',
                      fontWeight: 600,
                      fontSize: '13px',
                      opacity: isChatLoading ? 0.5 : 1
                    }"
                  >
                    <Send class="w-4 h-4" />
                  </button>
                </div>

                <!-- Example Commands -->
                <div :style="{ display: 'flex', flexDirection: 'column', gap: '6px' }">
                  <div
                    v-for="command in exampleCommands"
                    :key="command"
                    @click="useExample(command)"
                    :style="{
                      fontSize: '11px',
                      padding: '8px 12px',
                      background: '#FFFFFF',
                      border: '1px solid #E8EAED',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      color: '#6B7280',
                      transition: 'all 0.2s'
                    }"
                    @mouseover="($event.target as HTMLElement).style.borderColor = '#FF7A00'; ($event.target as HTMLElement).style.color = '#FF7A00'"
                    @mouseout="($event.target as HTMLElement).style.borderColor = '#E8EAED'; ($event.target as HTMLElement).style.color = '#6B7280'"
                  >
                    {{ command }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
