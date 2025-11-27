<template>
  <div
    class="w-full h-full flex flex-col"
    :style="{
      background: '#F7F8FA',
      paddingLeft: '54px'
    }"
  >
    <!-- Top Bar -->
    <div
:style="{
      background: '#FFFFFF',
      borderBottom: '1px solid #E8EAED',
      padding: '16px 40px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between'
    }">
      <div>
        <div :style="{ fontSize: '18px', fontWeight: 600, color: '#1A1F2E', marginBottom: '4px' }">
          중대성 평가 (Materiality Assessment)
        </div>
        <div :style="{ fontSize: '12px', color: '#6B7280' }">
          설문조사 및 미디어 분석을 통한 20개 이슈 우선순위 평가
        </div>
      </div>

      <button
        :style="{
          padding: '10px 20px',
          background: 'linear-gradient(120deg, #FF8F68, #F76D47)',
          borderRadius: '8px',
          border: 'none',
          cursor: 'pointer',
          fontSize: '13px',
          fontWeight: 600,
          color: '#FFFFFF',
          boxShadow: '0px 2px 6px rgba(247,109,71,0.3)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }"
        @click="handleSave"
      >
        <Save class="w-4 h-4" />
        평가 저장
      </button>
    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-auto" :style="{ padding: '32px 40px' }">
      <div class="flex flex-col gap-6">
        <!-- Top Section - 3 Columns -->
        <div :style="{ display: 'grid', gridTemplateColumns: '280px 280px 1fr', gap: '20px' }">
          <!-- Column 1: Survey Results -->
          <div :style="{ display: 'flex', flexDirection: 'column', gap: '20px' }">
            <!-- Survey Impact -->
            <div
:style="{
              background: '#FFFFFF',
              borderRadius: '12px',
              border: '1px solid #E8EAED',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              height: '360px'
            }">
              <div :style="{ fontSize: '14px', fontWeight: 600, color: '#FF7A00', marginBottom: '2px' }">
                설문조사 결과
              </div>
              <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '4px' }">
                영향 중대성
              </div>
              <div :style="{ fontSize: '9px', color: '#FF7A00', marginBottom: '12px' }">
                설문 응답 - 이해관계자 영향
              </div>

              <div class="flex-1 overflow-y-auto" :style="{ paddingRight: '6px' }">
                <div class="space-y-1.5">
                  <div
                    v-for="(issue, index) in surveyImpactRanked"
                    :key="issue.id"
                    :style="{
                      padding: '8px 10px',
                      borderRadius: '6px',
                      background: index < 5 ? '#FFF9F5' : '#F9FAFB',
                      border: `1px solid ${index < 5 ? '#FFE5D6' : '#E5E7EB'}`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }"
                  >
                    <div
:style="{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: index < 5 ? 'linear-gradient(135deg, #FF8F68, #F76D47)' : '#E5E7EB',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '9px',
                      fontWeight: 600,
                      color: index < 5 ? '#FFFFFF' : '#6B7280',
                      flexShrink: 0
                    }">
                      {{ index + 1 }}
                    </div>
                    <div :style="{ flex: 1, minWidth: 0 }">
                      <div
:style="{
                        fontSize: '9px',
                        fontWeight: index < 5 ? 600 : 500,
                        color: index < 5 ? '#1A1F2E' : '#6B7280',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis'
                      }">
                        {{ issue.name }}
                      </div>
                    </div>
                    <div
:style="{
                      fontSize: '10px',
                      fontWeight: 600,
                      color: index < 5 ? '#FF7A00' : '#9CA3AF',
                      flexShrink: 0
                    }">
                      {{ issue.surveyImpactScore }}
                    </div>
                    <div
                      :style="{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: getCategoryColor(issue.category),
                        flexShrink: 0
                      }"
                      :title="getCategoryLabel(issue.category)"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Survey Financial -->
            <div
:style="{
              background: '#FFFFFF',
              borderRadius: '12px',
              border: '1px solid #E8EAED',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              height: '360px'
            }">
              <div :style="{ fontSize: '14px', fontWeight: 600, color: '#FF7A00', marginBottom: '2px' }">
                설문조사 결과
              </div>
              <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '4px' }">
                재무 중대성
              </div>
              <div :style="{ fontSize: '9px', color: '#FF7A00', marginBottom: '12px' }">
                설문 응답 - 재무적 영향
              </div>

              <div class="flex-1 overflow-y-auto" :style="{ paddingRight: '6px' }">
                <div class="space-y-1.5">
                  <div
                    v-for="(issue, index) in surveyFinancialRanked"
                    :key="issue.id"
                    :style="{
                      padding: '8px 10px',
                      borderRadius: '6px',
                      background: index < 5 ? '#FFF9F5' : '#F9FAFB',
                      border: `1px solid ${index < 5 ? '#FFE5D6' : '#E5E7EB'}`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }"
                  >
                    <div
:style="{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: index < 5 ? 'linear-gradient(135deg, #FF8F68, #F76D47)' : '#E5E7EB',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '9px',
                      fontWeight: 600,
                      color: index < 5 ? '#FFFFFF' : '#6B7280',
                      flexShrink: 0
                    }">
                      {{ index + 1 }}
                    </div>
                    <div :style="{ flex: 1, minWidth: 0 }">
                      <div
:style="{
                        fontSize: '9px',
                        fontWeight: index < 5 ? 600 : 500,
                        color: index < 5 ? '#1A1F2E' : '#6B7280',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis'
                      }">
                        {{ issue.name }}
                      </div>
                    </div>
                    <div
:style="{
                      fontSize: '10px',
                      fontWeight: 600,
                      color: index < 5 ? '#FF7A00' : '#9CA3AF',
                      flexShrink: 0
                    }">
                      {{ issue.surveyFinancialScore }}
                    </div>
                    <div
                      :style="{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: getCategoryColor(issue.category),
                        flexShrink: 0
                      }"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Column 2: Media Analysis Results -->
          <div :style="{ display: 'flex', flexDirection: 'column', gap: '20px' }">
            <!-- Media Impact -->
            <div
:style="{
              background: '#FFFFFF',
              borderRadius: '12px',
              border: '1px solid #E8EAED',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              height: '360px'
            }">
              <div :style="{ fontSize: '14px', fontWeight: 600, color: '#FF7A00', marginBottom: '2px' }">
                미디어 분석 결과
              </div>
              <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '4px' }">
                영향 중대성
              </div>
              <div :style="{ fontSize: '9px', color: '#FF7A00', marginBottom: '12px' }">
                미디어 분석 - 이해관계자 영향
              </div>

              <div class="flex-1 overflow-y-auto" :style="{ paddingRight: '6px' }">
                <div class="space-y-1.5">
                  <div
                    v-for="(issue, index) in mediaImpactRanked"
                    :key="issue.id"
                    :style="{
                      padding: '8px 10px',
                      borderRadius: '6px',
                      background: index < 5 ? '#FFF9F5' : '#F9FAFB',
                      border: `1px solid ${index < 5 ? '#FFE5D6' : '#E5E7EB'}`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }"
                  >
                    <div
:style="{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: index < 5 ? 'linear-gradient(135deg, #FF8F68, #F76D47)' : '#E5E7EB',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '9px',
                      fontWeight: 600,
                      color: index < 5 ? '#FFFFFF' : '#6B7280',
                      flexShrink: 0
                    }">
                      {{ index + 1 }}
                    </div>
                    <div :style="{ flex: 1, minWidth: 0 }">
                      <div
:style="{
                        fontSize: '9px',
                        fontWeight: index < 5 ? 600 : 500,
                        color: index < 5 ? '#1A1F2E' : '#6B7280',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis'
                      }">
                        {{ issue.name }}
                      </div>
                    </div>
                    <div
:style="{
                      fontSize: '10px',
                      fontWeight: 600,
                      color: index < 5 ? '#FF7A00' : '#9CA3AF',
                      flexShrink: 0
                    }">
                      {{ issue.mediaImpactScore }}
                    </div>
                    <div
                      :style="{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: getCategoryColor(issue.category),
                        flexShrink: 0
                      }"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Media Financial -->
            <div
:style="{
              background: '#FFFFFF',
              borderRadius: '12px',
              border: '1px solid #E8EAED',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              height: '360px'
            }">
              <div :style="{ fontSize: '14px', fontWeight: 600, color: '#FF7A00', marginBottom: '2px' }">
                미디어 분석 결과
              </div>
              <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '4px' }">
                재무 중대성
              </div>
              <div :style="{ fontSize: '9px', color: '#FF7A00', marginBottom: '12px' }">
                미디어 분석 - 재무적 영향
              </div>

              <div class="flex-1 overflow-y-auto" :style="{ paddingRight: '6px' }">
                <div class="space-y-1.5">
                  <div
                    v-for="(issue, index) in mediaFinancialRanked"
                    :key="issue.id"
                    :style="{
                      padding: '8px 10px',
                      borderRadius: '6px',
                      background: index < 5 ? '#FFF9F5' : '#F9FAFB',
                      border: `1px solid ${index < 5 ? '#FFE5D6' : '#E5E7EB'}`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }"
                  >
                    <div
:style="{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      background: index < 5 ? 'linear-gradient(135deg, #FF8F68, #F76D47)' : '#E5E7EB',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '9px',
                      fontWeight: 600,
                      color: index < 5 ? '#FFFFFF' : '#6B7280',
                      flexShrink: 0
                    }">
                      {{ index + 1 }}
                    </div>
                    <div :style="{ flex: 1, minWidth: 0 }">
                      <div
:style="{
                        fontSize: '9px',
                        fontWeight: index < 5 ? 600 : 500,
                        color: index < 5 ? '#1A1F2E' : '#6B7280',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis'
                      }">
                        {{ issue.name }}
                      </div>
                    </div>
                    <div
:style="{
                      fontSize: '10px',
                      fontWeight: 600,
                      color: index < 5 ? '#FF7A00' : '#9CA3AF',
                      flexShrink: 0
                    }">
                      {{ issue.mediaFinancialScore }}
                    </div>
                    <div
                      :style="{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: getCategoryColor(issue.category),
                        flexShrink: 0
                      }"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Column 3: Matrix -->
          <div
:style="{
            background: '#FFFFFF',
            borderRadius: '12px',
            border: '1px solid #E8EAED',
            padding: '28px',
            height: '740px'
          }">
            <div :style="{ fontSize: '15px', fontWeight: 600, color: '#1A1F2E', marginBottom: '6px' }">
              이슈 중대성 매트릭스
            </div>
            <div :style="{ fontSize: '10px', color: '#6B7280', marginBottom: '24px' }">
              영향 중대성 x 재무 중대성
            </div>

            <!-- Matrix Container -->
            <div
:style="{
              position: 'relative',
              width: '100%',
              height: 'calc(100% - 90px)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }">
              <div
:style="{
                position: 'relative',
                width: '100%',
                height: '100%',
                paddingLeft: '50px',
                paddingBottom: '35px'
              }">
                <!-- Background Quadrants -->
                <div
:style="{
                  position: 'absolute',
                  width: 'calc(100% - 50px)',
                  height: 'calc(100% - 35px)',
                  left: '50px',
                  top: 0,
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gridTemplateRows: '1fr 1fr'
                }">
                  <div :style="{ background: '#FEF3C7', opacity: 0.3, borderRight: '1px dashed #D1D5DB', borderBottom: '1px dashed #D1D5DB' }" />
                  <div :style="{ background: '#FECACA', opacity: 0.4, borderBottom: '1px dashed #D1D5DB' }" />
                  <div :style="{ background: '#D1FAE5', opacity: 0.3, borderRight: '1px dashed #D1D5DB' }" />
                  <div :style="{ background: '#FED7AA', opacity: 0.4 }" />
                </div>

                <!-- Y Axis -->
                <div
:style="{
                  position: 'absolute',
                  left: '0px',
                  top: '50%',
                  transform: 'translateY(-50%) rotate(-90deg)',
                  fontSize: '10px',
                  fontWeight: 600,
                  color: '#6B7280',
                  whiteSpace: 'nowrap'
                }">
                  영향 중대성
                </div>

                <!-- X Axis -->
                <div
:style="{
                  position: 'absolute',
                  bottom: '0px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  fontSize: '10px',
                  fontWeight: 600,
                  color: '#6B7280',
                  whiteSpace: 'nowrap'
                }">
                  재무 중대성
                </div>

                <!-- Chart Area -->
                <div
:style="{
                  position: 'absolute',
                  left: '50px',
                  top: 0,
                  width: 'calc(100% - 50px)',
                  height: 'calc(100% - 35px)'
                }">
                  <!-- Data Points -->
                  <div
                    v-for="item in issuesWithAverage"
                    :key="item.id"
                    class="chart-point"
                    :style="{
                      position: 'absolute',
                      left: `${item.averageFinancial}%`,
                      bottom: `${item.averageImpact}%`,
                      transform: 'translate(-50%, 50%)',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      cursor: 'pointer',
                      zIndex: selectedIssue === item.id ? 100 : topIssues.some(t => t.id === item.id) ? 10 : 1
                    }"
                    @click="selectedIssue = item.id"
                  >
                    <!-- Bubble -->
                    <div :style="{
                      width: selectedIssue === item.id ? '16px' : topIssues.some(t => t.id === item.id) ? '12px' : '9px',
                      height: selectedIssue === item.id ? '16px' : topIssues.some(t => t.id === item.id) ? '12px' : '9px',
                      borderRadius: '50%',
                      background: getCategoryColor(item.category),
                      border: selectedIssue === item.id ? '3px solid #FFFFFF' : '2px solid #FFFFFF',
                      boxShadow: selectedIssue === item.id ? '0 4px 12px rgba(0,0,0,0.3)' : '0 2px 6px rgba(0,0,0,0.2)',
                      transition: 'all 0.2s',
                      opacity: topIssues.some(t => t.id === item.id) ? 1 : 0.35
                    }" />
                    <!-- Tooltip on hover -->
                    <div
                      class="chart-tooltip"
                      :style="{
                        position: 'absolute',
                        top: '100%',
                        marginTop: '8px',
                        padding: '8px 12px',
                        background: 'rgba(55, 65, 81, 0.95)',
                        borderRadius: '6px',
                        whiteSpace: 'nowrap',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                        pointerEvents: 'none'
                      }"
                    >
                      <div :style="{ fontSize: '12px', fontWeight: 600, color: '#FFFFFF', marginBottom: '4px' }">{{ item.name }}</div>
                      <div :style="{ fontSize: '11px', color: 'rgba(255,255,255,0.8)' }">
                        영향: {{ item.averageImpact.toFixed(1) }} | 재무: {{ item.averageFinancial.toFixed(1) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Legend -->
            <div :style="{ marginTop: '20px', display: 'flex', gap: '16px', justifyContent: 'center' }">
              <div :style="{ display: 'flex', alignItems: 'center', gap: '6px' }">
                <div :style="{ width: '10px', height: '10px', borderRadius: '50%', background: '#10B981' }" />
                <span :style="{ fontSize: '10px', color: '#6B7280' }">환경 (E)</span>
              </div>
              <div :style="{ display: 'flex', alignItems: 'center', gap: '6px' }">
                <div :style="{ width: '10px', height: '10px', borderRadius: '50%', background: '#3B82F6' }" />
                <span :style="{ fontSize: '10px', color: '#6B7280' }">사회 (S)</span>
              </div>
              <div :style="{ display: 'flex', alignItems: 'center', gap: '6px' }">
                <div :style="{ width: '10px', height: '10px', borderRadius: '50%', background: '#8B5CF6' }" />
                <span :style="{ fontSize: '10px', color: '#6B7280' }">지배구조 (G)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Bottom Section - Bar Charts -->
        <div
:style="{
          background: '#FFFFFF',
          borderRadius: '12px',
          border: '1px solid #E8EAED',
          padding: '28px'
        }">
          <div :style="{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }">
            <!-- Impact Bar Chart -->
            <div>
              <div :style="{ fontSize: '14px', fontWeight: 600, color: '#FF7A00', marginBottom: '4px' }">
                영향 중대성 평가 결과
              </div>
              <div :style="{ fontSize: '10px', color: '#9CA3AF', marginBottom: '16px' }">
                (설문 + 미디어) / 2
              </div>

              <div class="space-y-2">
                <div
                  v-for="issue in impactRanked.slice(0, 8)"
                  :key="issue.id"
                  :style="{ display: 'flex', alignItems: 'center', gap: '10px' }"
                >
                  <div
:style="{
                    fontSize: '10px',
                    color: '#6B7280',
                    minWidth: '140px',
                    textAlign: 'left',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }">
                    {{ issue.name }}
                  </div>
                  <div
:style="{
                    flex: 1,
                    height: '22px',
                    background: '#F3F4F6',
                    borderRadius: '4px',
                    overflow: 'hidden',
                    position: 'relative'
                  }">
                    <div
:style="{
                      width: `${issue.averageImpact}%`,
                      height: '100%',
                      background: 'linear-gradient(90deg, #FF8F68, #F76D47)',
                      borderRadius: '4px',
                      transition: 'width 0.3s ease'
                    }" />
                  </div>
                  <div
:style="{
                    fontSize: '11px',
                    fontWeight: 600,
                    color: '#FF7A00',
                    minWidth: '32px',
                    textAlign: 'right'
                  }">
                    {{ issue.averageImpact.toFixed(1) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Financial Bar Chart -->
            <div>
              <div :style="{ fontSize: '14px', fontWeight: 600, color: '#FF7A00', marginBottom: '4px' }">
                재무 중대성 평가 결과
              </div>
              <div :style="{ fontSize: '10px', color: '#9CA3AF', marginBottom: '16px' }">
                (설문 + 미디어) / 2
              </div>

              <div class="space-y-2">
                <div
                  v-for="issue in financialRanked.slice(0, 8)"
                  :key="issue.id"
                  :style="{ display: 'flex', alignItems: 'center', gap: '10px' }"
                >
                  <div
:style="{
                    fontSize: '10px',
                    color: '#6B7280',
                    minWidth: '140px',
                    textAlign: 'left',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }">
                    {{ issue.name }}
                  </div>
                  <div
:style="{
                    flex: 1,
                    height: '22px',
                    background: '#F3F4F6',
                    borderRadius: '4px',
                    overflow: 'hidden',
                    position: 'relative'
                  }">
                    <div
:style="{
                      width: `${issue.averageFinancial}%`,
                      height: '100%',
                      background: 'linear-gradient(90deg, #FF8F68, #F76D47)',
                      borderRadius: '4px',
                      transition: 'width 0.3s ease'
                    }" />
                  </div>
                  <div
:style="{
                    fontSize: '11px',
                    fontWeight: 600,
                    color: '#FF7A00',
                    minWidth: '32px',
                    textAlign: 'right'
                  }">
                    {{ issue.averageFinancial.toFixed(1) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Preview Modal -->
    <ReportPreviewModal
      :is-open="isReportModalOpen"
      :report-html="reportStore.reportHtml"
      :is-loading="reportStore.isGenerating"
      :metadata="reportStore.reportMetadata"
      :generation-status="reportStore.generationStatus"
      @close="handleCloseModal"
      @regenerate="handleRegenerate"
      @download="handleDownload"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { Save } from 'lucide-vue-next';
import { useReportStore } from '@/stores/reportStore';
import ReportPreviewModal from '@/components/report/ReportPreviewModal.vue';

interface Issue {
  id: string;
  name: string;
  category: 'environment' | 'social' | 'governance';
  surveyImpactScore: number;
  surveyFinancialScore: number;
  mediaImpactScore: number;
  mediaFinancialScore: number;
}

// Store & Router
const reportStore = useReportStore();
const router = useRouter();

// Local State
const selectedIssue = ref<string | null>(null);
const isReportModalOpen = ref(false);
const companyId = ref('SK_001');
const reportYear = ref(new Date().getFullYear());

const issues: Issue[] = [
  { id: 'issue1', name: '기후변화 대응(완화/적응)', category: 'environment', surveyImpactScore: 95, surveyFinancialScore: 90, mediaImpactScore: 92, mediaFinancialScore: 88 },
  { id: 'issue2', name: '안전보건 및 보호', category: 'social', surveyImpactScore: 88, surveyFinancialScore: 82, mediaImpactScore: 85, mediaFinancialScore: 80 },
  { id: 'issue3', name: '인재경영 및 인적자본 관리', category: 'social', surveyImpactScore: 85, surveyFinancialScore: 80, mediaImpactScore: 82, mediaFinancialScore: 78 },
  { id: 'issue4', name: '윤리경영 및 반부패', category: 'governance', surveyImpactScore: 82, surveyFinancialScore: 88, mediaImpactScore: 80, mediaFinancialScore: 85 },
  { id: 'issue5', name: '이해관계 관여', category: 'governance', surveyImpactScore: 80, surveyFinancialScore: 75, mediaImpactScore: 78, mediaFinancialScore: 72 },
  { id: 'issue6', name: '공급망 ESG 관리', category: 'governance', surveyImpactScore: 78, surveyFinancialScore: 73, mediaImpactScore: 75, mediaFinancialScore: 70 },
  { id: 'issue7', name: '환경경영 목표 관리', category: 'environment', surveyImpactScore: 75, surveyFinancialScore: 70, mediaImpactScore: 82, mediaFinancialScore: 78 },
  { id: 'issue8', name: '서비스 품질 및 안정성', category: 'social', surveyImpactScore: 73, surveyFinancialScore: 68, mediaImpactScore: 85, mediaFinancialScore: 82 },
  { id: 'issue9', name: '투명한 이사회 경영', category: 'governance', surveyImpactScore: 70, surveyFinancialScore: 72, mediaImpactScore: 68, mediaFinancialScore: 75 },
  { id: 'issue10', name: '신재생에너지 전환 확대', category: 'environment', surveyImpactScore: 68, surveyFinancialScore: 65, mediaImpactScore: 80, mediaFinancialScore: 77 },
  { id: 'issue11', name: '정보보안 및 고객 정보보호', category: 'governance', surveyImpactScore: 65, surveyFinancialScore: 70, mediaImpactScore: 75, mediaFinancialScore: 80 },
  { id: 'issue12', name: '전환 자산/기술 투자', category: 'environment', surveyImpactScore: 62, surveyFinancialScore: 58, mediaImpactScore: 70, mediaFinancialScore: 68 },
  { id: 'issue13', name: '지역사회 공헌', category: 'social', surveyImpactScore: 60, surveyFinancialScore: 55, mediaImpactScore: 65, mediaFinancialScore: 62 },
  { id: 'issue14', name: '폐기물 관리', category: 'environment', surveyImpactScore: 58, surveyFinancialScore: 60, mediaImpactScore: 68, mediaFinancialScore: 70 },
  { id: 'issue15', name: '주주가치 제고', category: 'governance', surveyImpactScore: 55, surveyFinancialScore: 62, mediaImpactScore: 60, mediaFinancialScore: 68 },
  { id: 'issue16', name: '생물다양성 보호', category: 'environment', surveyImpactScore: 52, surveyFinancialScore: 48, mediaImpactScore: 58, mediaFinancialScore: 55 },
  { id: 'issue17', name: '포트폴리오 ESG 관리', category: 'governance', surveyImpactScore: 50, surveyFinancialScore: 52, mediaImpactScore: 55, mediaFinancialScore: 58 },
  { id: 'issue18', name: '독점 리스크 관리', category: 'governance', surveyImpactScore: 48, surveyFinancialScore: 55, mediaImpactScore: 78, mediaFinancialScore: 82 },
  { id: 'issue19', name: '환경경영 요인 관리', category: 'environment', surveyImpactScore: 45, surveyFinancialScore: 42, mediaImpactScore: 72, mediaFinancialScore: 70 },
  { id: 'issue20', name: '인권존중 및 보호', category: 'social', surveyImpactScore: 42, surveyFinancialScore: 45, mediaImpactScore: 65, mediaFinancialScore: 68 },
]

const issuesWithAverage = computed(() => issues.map(issue => ({
  ...issue,
  averageImpact: (issue.surveyImpactScore + issue.mediaImpactScore) / 2,
  averageFinancial: (issue.surveyFinancialScore + issue.mediaFinancialScore) / 2,
})))

const surveyImpactRanked = computed(() =>
  [...issuesWithAverage.value].sort((a, b) => b.surveyImpactScore - a.surveyImpactScore)
)

const surveyFinancialRanked = computed(() =>
  [...issuesWithAverage.value].sort((a, b) => b.surveyFinancialScore - a.surveyFinancialScore)
)

const mediaImpactRanked = computed(() =>
  [...issuesWithAverage.value].sort((a, b) => b.mediaImpactScore - a.mediaImpactScore)
)

const mediaFinancialRanked = computed(() =>
  [...issuesWithAverage.value].sort((a, b) => b.mediaFinancialScore - a.mediaFinancialScore)
)

const impactRanked = computed(() =>
  [...issuesWithAverage.value].sort((a, b) => b.averageImpact - a.averageImpact)
)

const financialRanked = computed(() =>
  [...issuesWithAverage.value].sort((a, b) => b.averageFinancial - a.averageFinancial)
)

const topIssues = computed(() =>
  [...issuesWithAverage.value]
    .map(issue => ({
      ...issue,
      totalScore: (issue.averageImpact + issue.averageFinancial) / 2
    }))
    .sort((a, b) => b.totalScore - a.totalScore)
    .slice(0, 5)
)

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'environment': return '#10B981'
    case 'social': return '#3B82F6'
    case 'governance': return '#8B5CF6'
    default: return '#6B7280'
  }
}

const getCategoryLabel = (category: string) => {
  switch (category) {
    case 'environment': return '환경'
    case 'social': return '사회'
    case 'governance': return '지배구조'
    default: return ''
  }
}

const handleSave = () => {
  const assessmentData = {
    id: Date.now().toString(),
    date: new Date().toISOString().split('T')[0].replace(/-/g, '.'),
    companyId: companyId.value,
    companyName: 'SK 테스트 기업',
    industry: '제조업',
    reportYear: reportYear.value,
    topIssues: topIssues.value,
    allIssues: issuesWithAverage.value,
    issues: issues.map(issue => ({
      id: issue.id,
      name: issue.name,
      category: issue.category === 'environment' ? 'E' : issue.category === 'social' ? 'S' : 'G',
      surveyImpactScore: issue.surveyImpactScore,
      surveyFinancialScore: issue.surveyFinancialScore,
      mediaImpactScore: issue.mediaImpactScore,
      mediaFinancialScore: issue.mediaFinancialScore,
      averageImpact: (issue.surveyImpactScore + issue.mediaImpactScore) / 2,
      averageFinancial: (issue.surveyFinancialScore + issue.mediaFinancialScore) / 2
    })),
    top5PriorityIssueIds: topIssues.value.map(issue => issue.id)
  };

  localStorage.setItem('materialityAssessment', JSON.stringify(assessmentData));

  router.push('/report');
};

/**
 * 보고서 모달 닫기
 */
const handleCloseModal = () => {
  isReportModalOpen.value = false;
};

/**
 * 보고서 재생성
 */
const handleRegenerate = async () => {
  try {
    await reportStore.regenerateReport(companyId.value, reportYear.value);
  } catch (error) {
    console.error('보고서 재생성 실패:', error);
  }
};

/**
 * 보고서 다운로드
 */
const handleDownload = () => {
  if (!reportStore.reportHtml) return;

  const blob = new Blob([reportStore.reportHtml], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const linkElement = document.createElement('a');
  linkElement.href = url;
  linkElement.download = `ESG_Report_${companyId.value}_${reportYear.value}.html`;
  document.body.appendChild(linkElement);
  linkElement.click();
  document.body.removeChild(linkElement);
  URL.revokeObjectURL(url);
};
</script>

<style scoped>
.chart-point .chart-tooltip {
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, visibility 0.2s ease;
}

.chart-point:hover .chart-tooltip {
  opacity: 1;
  visibility: visible;
}

.chart-point:hover {
  z-index: 200 !important;
}
</style>
