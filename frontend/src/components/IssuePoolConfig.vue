<template>
  <div
    class="w-full h-full flex flex-col"
    :style="{
      background: '#F7F8FA',
      paddingLeft: '54px'
    }"
  >
    <!-- Top Bar -->
    <div :style="{
      background: '#FFFFFF',
      borderBottom: '1px solid #E8EAED'
    }">
      <!-- First Row: Main Tabs -->
      <div :style="{
        padding: '16px 40px 0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }">
        <div class="flex gap-0">
          <button
            v-for="tab in modeTabs"
            :key="tab.id"
            @click="mode = tab.id as 'list' | 'config'"
            :style="{
              padding: '10px 20px',
              fontSize: '13px',
              fontWeight: 600,
              color: mode === tab.id ? '#1A1F2E' : '#9CA3AF',
              borderTop: 'none',
              borderLeft: 'none',
              borderRight: 'none',
              borderBottom: mode === tab.id ? '3px solid #EA7F52' : '3px solid transparent',
              background: 'transparent',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Right: Survey Button (config mode only) -->
        <div class="flex items-center gap-3">
          <!-- Survey Button - Only show in config mode -->
          <button
            v-if="mode === 'config'"
            @click="showSurveyModal = true"
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
          >
            <FileText class="w-4 h-4" />
            설문조사 생성
          </button>
        </div>
      </div>

    </div>

    <!-- Main Content -->
    <div class="flex-1 overflow-hidden">
      <!-- Document List View (list mode) -->
      <DocumentList v-if="mode === 'list'" />

      <!-- Issue Pool Config View -->
      <div v-else class="h-full flex" :style="{ gap: '0' }">
        <!-- Left Panel - Issue List -->
        <div :style="{
          width: '240px',
          background: '#FFFFFF',
          borderRight: '1px solid #E8EAED',
          padding: '20px',
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }">
          <div :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E' }">
            이슈 목록
          </div>

          <div class="space-y-2">
            <button
              v-for="(issue, index) in issues"
              :key="issue.id"
              @click="selectedIssue = issue.id"
              :style="{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '8px',
                background: selectedIssue === issue.id ? '#FFF5F0' : '#FFFFFF',
                border: selectedIssue === issue.id ? '1px solid #FF8F68' : '1px solid #E8EAED',
                fontSize: '12px',
                fontWeight: 500,
                color: selectedIssue === issue.id ? '#1A1F2E' : '#6B7280',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }"
            >
              <span :style="{
                fontSize: '10px',
                fontWeight: 600,
                color: selectedIssue === issue.id ? '#FF7A00' : '#9CA3AF',
                minWidth: '20px'
              }">
                {{ index + 1 }}.
              </span>
              <span :style="{ flex: 1 }">
                {{ issue.name }}
              </span>
            </button>
          </div>
        </div>

        <!-- Center Left Panel - Analysis Selection -->
        <div :style="{
          width: '280px',
          background: '#FFFFFF',
          borderRight: '1px solid #E8EAED',
          padding: '20px',
          overflow: 'auto'
        }">
          <div :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E', marginBottom: '16px' }">
            자료 선택
          </div>
          <div class="space-y-3">
            <button
              v-for="analysis in analyses"
              :key="analysis.id"
              @click="handleAnalysisSelect(analysis.id)"
              :style="{
                width: '100%',
                padding: '16px',
                borderRadius: '12px',
                background: '#FFFFFF',
                border: selectedAnalysis === analysis.id ? '2px solid #FF8F68' : '1px solid #E8EAED',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }"
            >
              <div :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E' }">
                {{ analysis.name }}
              </div>
              <div :style="{ fontSize: '11px', color: '#9CA3AF', lineHeight: '1.5' }">
                {{ analysis.summary }}
              </div>
              <div v-if="analysis.documentName" :style="{ fontSize: '11px', fontWeight: 500, color: '#FF8F68', marginTop: '4px' }">
                {{ analysis.documentName }}
              </div>
            </button>
          </div>
        </div>

        <!-- Center Right Panel - Analysis Result -->
        <div :style="{
          flex: 1,
          background: '#FFFFFF',
          padding: '20px',
          overflow: 'auto'
        }">
          <div :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E', marginBottom: '16px' }">
            자료 분석
          </div>

          <!-- 벤치마킹 분석 선택 시 테이블 표시 -->
          <template v-if="selectedAnalysis === 'benchmark'">
            <!-- Loading -->
            <div v-if="benchmarkLoading" :style="{ textAlign: 'center', padding: '40px' }">
              <div :style="{
                width: '32px',
                height: '32px',
                border: '3px solid #E8EAED',
                borderTop: '3px solid #FF8F68',
                borderRadius: '50%',
                margin: '0 auto 12px',
                animation: 'spin 1s linear infinite'
              }"></div>
              <div :style="{ fontSize: '12px', color: '#6B7280' }">데이터 로딩 중...</div>
            </div>

            <!-- 벤치마킹 테이블 -->
            <div v-else-if="benchmarkCompanies.length > 0">
              <div :style="{
                padding: '12px 16px',
                borderRadius: '8px',
                background: 'linear-gradient(120deg, #FF8F68, #F76D47)',
                marginBottom: '16px'
              }">
                <div :style="{ fontSize: '13px', fontWeight: 600, color: '#FFFFFF' }">
                  경쟁사 벤치마킹 분석 ({{ benchmarkCompanies.length }}개사)
                </div>
              </div>

              <!-- 상위 5개 이슈 -->
              <div :style="{ marginBottom: '16px' }">
                <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '10px' }">
                  경쟁사 중요 이슈 TOP 5
                </div>
                <div :style="{ display: 'flex', gap: '8px', flexWrap: 'wrap' }">
                  <div
                    v-for="(item, index) in top5Issues"
                    :key="item.issue"
                    :style="{
                      padding: '8px 12px',
                      background: index === 0 ? '#FF8F68' : '#F3F4F6',
                      borderRadius: '8px',
                      fontSize: '11px',
                      fontWeight: 500,
                      color: index === 0 ? '#FFFFFF' : '#4A5568',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }"
                  >
                    <span :style="{ fontWeight: 700 }">#{{ index + 1 }}</span>
                    {{ item.issue.length > 15 ? item.issue.substring(0, 15) + '..' : item.issue }}
                    <span :style="{
                      background: index === 0 ? 'rgba(255,255,255,0.3)' : '#E8EAED',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      fontSize: '10px'
                    }">{{ item.count }}개사</span>
                  </div>
                </div>
              </div>

              <!-- 테이블 -->
              <div :style="{ border: '1px solid #E8EAED', borderRadius: '8px', overflow: 'hidden' }">
                <div :style="{ overflowX: 'auto' }">
                  <table :style="{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }">
                    <thead>
                      <tr :style="{ background: '#F8F9FA' }">
                        <th :style="{
                          padding: '12px',
                          textAlign: 'left',
                          fontSize: '11px',
                          fontWeight: 600,
                          color: '#4A5568',
                          borderBottom: '1px solid #E8EAED',
                          position: 'sticky',
                          left: 0,
                          background: '#F8F9FA',
                          minWidth: '180px'
                        }">
                          2024 이슈풀 (18개)
                        </th>
                        <th
                          v-for="company in benchmarkCompanies"
                          :key="company"
                          :style="{
                            padding: '12px 8px',
                            textAlign: 'center',
                            fontSize: '10px',
                            fontWeight: 600,
                            color: '#4A5568',
                            borderBottom: '1px solid #E8EAED',
                            minWidth: '60px',
                            maxWidth: '80px',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis'
                          }"
                          :title="company"
                        >
                          {{ company.length > 8 ? company.substring(0, 8) + '..' : company }}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(issue, idx) in sk18Issues"
                        :key="issue"
                        :style="{
                          background: idx % 2 === 0 ? '#FFFFFF' : '#FAFBFC'
                        }"
                      >
                        <td :style="{
                          padding: '10px 12px',
                          fontSize: '11px',
                          color: '#1A1F2E',
                          borderBottom: '1px solid #E8EAED',
                          position: 'sticky',
                          left: 0,
                          background: idx % 2 === 0 ? '#FFFFFF' : '#FAFBFC'
                        }">
                          <span :style="{ color: '#EA7F52', fontWeight: 600, marginRight: '6px' }">{{ idx + 1 }}.</span>
                          {{ issue }}
                        </td>
                        <td
                          v-for="company in benchmarkCompanies"
                          :key="`${issue}-${company}`"
                          :style="{
                            padding: '10px 8px',
                            textAlign: 'center',
                            borderBottom: '1px solid #E8EAED'
                          }"
                        >
                          <!-- Yes일 때만 주황색 점 표시 (클릭 가능) -->
                          <span
                            v-if="getBenchmarkCoverage(company, issue) === 'Yes'"
                            @click="showBenchmarkDetail(company, issue)"
                            :style="{
                              display: 'inline-block',
                              width: '10px',
                              height: '10px',
                              borderRadius: '50%',
                              background: '#FF8F68',
                              cursor: 'pointer',
                              transition: 'transform 0.2s'
                            }"
                            @mouseenter="($event.target as HTMLElement).style.transform = 'scale(1.3)'"
                            @mouseleave="($event.target as HTMLElement).style.transform = 'scale(1)'"
                          ></span>
                          <span v-else :style="{ color: '#E8EAED' }">-</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- 범례 -->
              <div :style="{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '16px', justifyContent: 'flex-end' }">
                <div :style="{ display: 'flex', alignItems: 'center', gap: '6px' }">
                  <span :style="{ width: '10px', height: '10px', borderRadius: '50%', background: '#FF8F68' }"></span>
                  <span :style="{ fontSize: '11px', color: '#6B7280' }">커버됨 (클릭하여 상세보기)</span>
                </div>
                <div :style="{ display: 'flex', alignItems: 'center', gap: '6px' }">
                  <span :style="{ fontSize: '11px', color: '#9CA3AF' }">-</span>
                  <span :style="{ fontSize: '11px', color: '#6B7280' }">미커버</span>
                </div>
              </div>

            </div>

            <!-- 데이터 없음 -->
            <div v-else :style="{ textAlign: 'center', padding: '40px', color: '#9CA3AF', fontSize: '13px' }">
              벤치마킹 데이터가 없습니다
            </div>
          </template>

          <!-- ESG 표준 분석 선택 시 -->
          <template v-else-if="selectedAnalysis === 'esg'">
            <!-- Header -->
            <div :style="{
              padding: '12px 16px',
              borderRadius: '8px',
              background: 'linear-gradient(120deg, #FF8F68, #F76D47)',
              marginBottom: '16px'
            }">
              <div :style="{ fontSize: '13px', fontWeight: 600, color: '#FFFFFF' }">
                ESG 표준 분석 (GRI / SASB)
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="esgStandardsError" :style="{
              padding: '10px 12px',
              background: '#FEE2E2',
              borderRadius: '8px',
              marginBottom: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }">
              <AlertCircle class="w-4 h-4" :style="{ color: '#EF4444' }" />
              <span :style="{ fontSize: '11px', color: '#B91C1C', flex: 1 }">{{ esgStandardsError }}</span>
              <button @click="esgStandardsError = ''" :style="{ background: 'none', border: 'none', cursor: 'pointer', color: '#B91C1C' }">
                <X class="w-3 h-3" />
              </button>
            </div>

            <!-- Loading State -->
            <div v-if="esgStandardsLoading" :style="{ textAlign: 'center', padding: '40px' }">
              <div :style="{
                width: '32px',
                height: '32px',
                border: '3px solid #E8EAED',
                borderTop: '3px solid #FF8F68',
                borderRadius: '50%',
                margin: '0 auto 12px',
                animation: 'spin 1s linear infinite'
              }"></div>
              <div :style="{ fontSize: '12px', color: '#6B7280' }">ESG 표준 데이터 로딩 중...</div>
            </div>

            <!-- Results -->
            <template v-else-if="esgIssuesWithDisclosures.length > 0">
              <!-- Summary Stats -->
              <div :style="{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', marginBottom: '16px' }">
                <div :style="{ padding: '12px', background: '#FFF5F0', borderRadius: '8px', textAlign: 'center' }">
                  <div :style="{ fontSize: '18px', fontWeight: 700, color: '#EA7F52' }">{{ esgIssuesWithDisclosures.reduce((sum, i) => sum + i.gri_count, 0) }}</div>
                  <div :style="{ fontSize: '10px', color: '#F76D47' }">GRI 공시</div>
                </div>
                <div :style="{ padding: '12px', background: '#CFFAFE', borderRadius: '8px', textAlign: 'center' }">
                  <div :style="{ fontSize: '18px', fontWeight: 700, color: '#0891B2' }">{{ esgIssuesWithDisclosures.reduce((sum, i) => sum + i.sasb_count, 0) }}</div>
                  <div :style="{ fontSize: '10px', color: '#0E7490' }">SASB 공시</div>
                </div>
              </div>

              <!-- Selected Issue Details -->
              <div v-if="selectedESGIssueData">
                <div :style="{
                  padding: '16px',
                  background: '#F8FAFC',
                  borderRadius: '12px',
                  border: '1px solid #E2E8F0',
                  marginBottom: '12px'
                }">
                  <div :style="{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }">
                    <span :style="{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      background: getESGCategoryColor(selectedESGIssueData.category),
                      fontSize: '10px',
                      fontWeight: 600,
                      color: '#FFFFFF'
                    }">{{ getESGCategoryLabel(selectedESGIssueData.category) }}</span>
                    <span :style="{ fontSize: '13px', fontWeight: 600, color: '#1A1F2E' }">{{ selectedESGIssueData.issue }}</span>
                  </div>

                  <!-- Disclosure List -->
                  <div :style="{ fontSize: '11px', fontWeight: 600, color: '#6B7280', marginBottom: '8px' }">
                    관련 공시 기준 ({{ selectedESGIssueData.disclosure_count }}개)
                  </div>
                  <div class="space-y-2">
                    <div
                      v-for="disclosure in selectedESGIssueData.disclosures"
                      :key="disclosure.id"
                      :style="{
                        padding: '12px 14px',
                        background: '#FFFFFF',
                        border: '1px solid #E8EAED',
                        borderRadius: '8px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px'
                      }"
                    >
                      <!-- Header Row: Standard + ID + Title -->
                      <div :style="{ display: 'flex', alignItems: 'flex-start', gap: '8px' }">
                        <span :style="{
                          padding: '2px 6px',
                          borderRadius: '3px',
                          background: getStandardColor(disclosure.standard) + '20',
                          fontSize: '9px',
                          fontWeight: 600,
                          color: getStandardColor(disclosure.standard),
                          flexShrink: 0
                        }">{{ disclosure.standard }}</span>
                        <div :style="{ flex: 1, minWidth: 0 }">
                          <div :style="{ fontSize: '11px', fontWeight: 600, color: '#1A1F2E', marginBottom: '2px' }">
                            {{ disclosure.id }}
                          </div>
                          <div :style="{ fontSize: '10px', color: '#4A5568' }">
                            {{ disclosure.title }}
                          </div>
                        </div>
                      </div>

                      <!-- Description -->
                      <div v-if="disclosure.description" :style="{
                        fontSize: '10px',
                        color: '#6B7280',
                        lineHeight: '1.5',
                        paddingLeft: '4px',
                        borderLeft: '2px solid #E8EAED'
                      }">
                        {{ disclosure.description.length > 150 ? disclosure.description.substring(0, 150) + '...' : disclosure.description }}
                      </div>

                      <!-- Source Info -->
                      <div :style="{ fontSize: '9px', color: '#9CA3AF' }">
                        출처: {{ disclosure.standard === 'GRI' ? 'GRI Standards' : 'SASB Standards' }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- AI Analysis -->
                <div v-if="esgAnalysisLoading" :style="{ textAlign: 'center', padding: '20px' }">
                  <div :style="{
                    width: '24px',
                    height: '24px',
                    border: '2px solid #E8EAED',
                    borderTop: '2px solid #FF8F68',
                    borderRadius: '50%',
                    margin: '0 auto 8px',
                    animation: 'spin 1s linear infinite'
                  }"></div>
                  <div :style="{ fontSize: '11px', color: '#6B7280' }">AI 분석 중...</div>
                </div>

                <div v-else-if="esgAnalysisResult" :style="{
                  padding: '16px',
                  background: '#FFFBEB',
                  borderRadius: '12px',
                  border: '1px solid #FDE68A'
                }">
                  <div :style="{ fontSize: '12px', fontWeight: 600, color: '#92400E', marginBottom: '10px' }">
                    ✨ AI 분석 결과
                  </div>
                  <div :style="{ fontSize: '11px', color: '#78350F', lineHeight: '1.6', marginBottom: '12px' }">
                    {{ esgAnalysisResult.analysis.summary }}
                  </div>

                  <div v-if="esgAnalysisResult.analysis.recommendations?.length > 0">
                    <div :style="{ fontSize: '11px', fontWeight: 600, color: '#92400E', marginBottom: '6px' }">권장사항</div>
                    <ul :style="{ margin: 0, paddingLeft: '16px' }">
                      <li
                        v-for="(rec, idx) in esgAnalysisResult.analysis.recommendations"
                        :key="idx"
                        :style="{ fontSize: '10px', color: '#78350F', marginBottom: '4px' }"
                      >{{ rec }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </template>

            <!-- Empty State -->
            <div v-else :style="{ textAlign: 'center', padding: '40px', color: '#9CA3AF' }">
              <FileText class="w-8 h-8 mx-auto mb-3" :style="{ opacity: 0.5 }" />
              <div :style="{ fontSize: '12px', marginBottom: '4px' }">ESG 표준 데이터가 없습니다</div>
              <div :style="{ fontSize: '10px' }">새로고침을 클릭하여 데이터를 로드하세요</div>
            </div>
          </template>

          <!-- 미디어 분석 선택 시 -->
          <template v-else-if="selectedAnalysis === 'media'">
            <!-- Header -->
            <div :style="{
              padding: '12px 16px',
              borderRadius: '8px',
              background: 'linear-gradient(120deg, #FF8F68, #F76D47)',
              marginBottom: '16px'
            }">
              <div :style="{ fontSize: '13px', fontWeight: 600, color: '#FFFFFF' }">
                ESG 미디어 분석
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="mediaError" :style="{
              padding: '10px 12px',
              background: '#FEE2E2',
              borderRadius: '8px',
              marginBottom: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }">
              <AlertCircle class="w-4 h-4" :style="{ color: '#EF4444' }" />
              <span :style="{ fontSize: '11px', color: '#B91C1C', flex: 1 }">{{ mediaError }}</span>
              <button @click="mediaError = ''" :style="{ background: 'none', border: 'none', cursor: 'pointer', color: '#B91C1C' }">
                <X class="w-3 h-3" />
              </button>
            </div>

            <!-- Loading State -->
            <div v-if="mediaLoading" :style="{ textAlign: 'center', padding: '40px' }">
              <div :style="{
                width: '32px',
                height: '32px',
                border: '3px solid #E8EAED',
                borderTop: '3px solid #FF8F68',
                borderRadius: '50%',
                margin: '0 auto 12px',
                animation: 'spin 1s linear infinite'
              }"></div>
              <div :style="{ fontSize: '12px', color: '#6B7280' }">뉴스 분석 중...</div>
            </div>

            <!-- Results -->
            <template v-else-if="mediaTotalArticles > 0">
              <!-- Summary Stats -->
              <div :style="{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', marginBottom: '16px' }">
                <div :style="{ padding: '12px', background: '#F3F4F6', borderRadius: '8px', textAlign: 'center' }">
                  <div :style="{ fontSize: '18px', fontWeight: 700, color: '#1A1F2E' }">{{ mediaTotalArticles }}</div>
                  <div :style="{ fontSize: '10px', color: '#6B7280' }">기사</div>
                </div>
                <div :style="{ padding: '12px', background: '#FFF5F0', borderRadius: '8px', textAlign: 'center' }">
                  <div :style="{ fontSize: '18px', fontWeight: 700, color: '#EA7F52' }">{{ mediaPositiveCount }}</div>
                  <div :style="{ fontSize: '10px', color: '#F76D47' }">긍정</div>
                </div>
                <div :style="{ padding: '12px', background: '#FEE2E2', borderRadius: '8px', textAlign: 'center' }">
                  <div :style="{ fontSize: '18px', fontWeight: 700, color: '#EF4444' }">{{ mediaNegativeCount }}</div>
                  <div :style="{ fontSize: '10px', color: '#B91C1C' }">부정</div>
                </div>
                <div :style="{ padding: '12px', background: '#F3F4F6', borderRadius: '8px', textAlign: 'center' }">
                  <div :style="{ fontSize: '18px', fontWeight: 700, color: '#6B7280' }">{{ mediaNeutralCount }}</div>
                  <div :style="{ fontSize: '10px', color: '#6B7280' }">중립</div>
                </div>
              </div>

              <!-- Recent Articles -->
              <div>
                <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '8px' }">
                  {{ currentIssue?.name ? `'${currentIssue.name}' 관련 기사` : '주요 기사' }}
                </div>

                <!-- 관련 기사가 없는 경우 -->
                <div v-if="filteredMediaArticles.length === 0 && currentIssue?.name" :style="{
                  textAlign: 'center',
                  padding: '24px',
                  background: '#F9FAFB',
                  borderRadius: '8px',
                  color: '#6B7280'
                }">
                  <div :style="{ fontSize: '11px', marginBottom: '4px' }">
                    '{{ currentIssue?.name }}' 관련 기사가 없습니다
                  </div>
                  <div :style="{ fontSize: '10px', color: '#9CA3AF' }">
                    다른 이슈를 선택해보세요
                  </div>
                </div>

                <div v-else class="space-y-2">
                  <div
                    v-for="(article, idx) in filteredMediaArticles"
                    :key="idx"
                    @click="openMediaArticle(article.link)"
                    :style="{
                      padding: '10px 12px',
                      background: '#FFFFFF',
                      border: '1px solid #E8EAED',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }"
                  >
                    <div :style="{ display: 'flex', alignItems: 'flex-start', gap: '8px' }">
                      <div :style="{
                        padding: '2px 6px',
                        borderRadius: '3px',
                        fontSize: '9px',
                        fontWeight: 600,
                        flexShrink: 0,
                        ...getMediaSentimentStyle(article.sentiment)
                      }">
                        {{ article.sentiment }}
                      </div>
                      <div :style="{ flex: 1, minWidth: 0 }">
                        <div :style="{
                          fontSize: '11px',
                          fontWeight: 500,
                          color: '#1A1F2E',
                          marginBottom: '4px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }">
                          {{ article.clean_title || article.title }}
                        </div>
                        <div :style="{ display: 'flex', alignItems: 'center', gap: '6px' }">
                          <span
                            v-for="(issue, issueIdx) in (article.esg_issues || []).slice(0, 1)"
                            :key="issueIdx"
                            :style="{
                              padding: '1px 4px',
                              background: '#F3F4F6',
                              borderRadius: '2px',
                              fontSize: '9px',
                              color: '#6B7280'
                            }"
                          >{{ issue.length > 8 ? issue.substring(0, 8) + '..' : issue }}</span>
                          <span :style="{ fontSize: '9px', color: '#9CA3AF' }">{{ formatMediaDate(article.pubDate) }}</span>
                        </div>
                      </div>
                      <ExternalLink class="w-3 h-3" :style="{ color: '#9CA3AF', flexShrink: 0 }" />
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <!-- Empty State -->
            <div v-else :style="{ textAlign: 'center', padding: '40px', color: '#9CA3AF' }">
              <FileText class="w-8 h-8 mx-auto mb-3" :style="{ opacity: 0.5 }" />
              <div :style="{ fontSize: '12px', marginBottom: '4px' }">미디어 데이터가 없습니다</div>
              <div :style="{ fontSize: '10px' }">데이터를 불러오는 중이거나 수집된 뉴스가 없습니다</div>
            </div>
          </template>

          <!-- 다른 분석 선택 시 기존 UI -->
          <template v-else-if="selectedAnalysis">
            <div v-if="currentAnalysis?.documentName" :style="{
              padding: '12px 16px',
              borderRadius: '8px',
              background: '#FF8F68',
              marginBottom: '16px'
            }">
              <div :style="{ fontSize: '13px', fontWeight: 600, color: '#FFFFFF' }">
                {{ currentAnalysis?.documentName }}
              </div>
            </div>

            <div :style="{
              padding: '16px',
              borderRadius: '12px',
              background: '#FFF5F0',
              border: '1px solid #E8EAED',
              marginBottom: '20px'
            }">
              <div :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E', marginBottom: '8px' }">
                {{ currentIssue?.name }}
              </div>
              <div :style="{ fontSize: '12px', color: '#6B7280' }">
                {{ currentAnalysis?.name }}
              </div>
            </div>

            <div :style="{ marginBottom: '20px' }">
              <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '12px' }">
                주요 발견 사항
              </div>
              <div class="space-y-3">
                <div
                  v-for="(highlight, idx) in currentAnalysis?.highlights"
                  :key="idx"
                  :style="{
                    padding: '12px 16px',
                    background: '#FFE5B4',
                    borderRadius: '8px',
                    border: '1px solid #FFD580',
                    fontSize: '12px',
                    color: '#1A1F2E',
                    lineHeight: '1.6'
                  }"
                >
                  <div :style="{ fontWeight: 600, marginBottom: '4px' }">
                    {{ highlight.text }}
                  </div>
                  <div :style="{ fontSize: '11px', color: '#6B7280' }">
                    페이지 {{ highlight.page }}
                  </div>
                </div>
              </div>
            </div>
          </template>

          <div
            v-else
            :style="{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '300px',
              fontSize: '13px',
              color: '#9CA3AF'
            }"
          >
            분석 항목을 선택해주세요
          </div>
        </div>
      </div>
    </div>

    <!-- Survey Modal -->
    <div
      v-if="showSurveyModal"
      class="fixed inset-0 flex items-center justify-center"
      :style="{
        background: 'rgba(0,0,0,0.5)',
        zIndex: 9999,
        paddingLeft: '54px'
      }"
      @click="showSurveyModal = false"
    >
      <div
        class="relative"
        :style="{
          width: '900px',
          maxHeight: '80vh',
          background: '#FFFFFF',
          borderRadius: '16px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }"
        @click.stop
      >
        <!-- Modal Header -->
        <div :style="{
          padding: '24px 32px',
          borderBottom: '1px solid #E8EAED',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }">
          <div>
            <div :style="{ fontSize: '20px', fontWeight: 600, color: '#1A1F2E', marginBottom: '4px' }">
              설문조사 미리보기
            </div>
            <div :style="{ fontSize: '12px', color: '#6B7280' }">
              18개 이슈에 대한 중대성 평가 설문지
            </div>
          </div>
          <button
            @click="showSurveyModal = false"
            :style="{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: '#F3F4F6',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }"
          >
            <X class="w-5 h-5" :style="{ color: '#6B7280' }" />
          </button>
        </div>

        <!-- Modal Content -->
        <div :style="{ flex: 1, overflowY: 'auto', padding: '32px' }">
          <div :style="{
            background: '#FFF9F5',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid #FFE5D6',
            marginBottom: '24px'
          }">
            <div :style="{ fontSize: '14px', fontWeight: 600, color: '#FF7A00', marginBottom: '8px' }">
              설문 안내
            </div>
            <div :style="{ fontSize: '12px', color: '#6B7280', lineHeight: '1.6' }">
              다음 각 이슈에 대해 영향 중대성(이해관계자 영향)과 재무 중대성(재무적 영향)을 1-5점 척도로 평가해 주세요.
            </div>
          </div>

          <div class="space-y-6">
            <div
              v-for="(issue, index) in issues"
              :key="issue.id"
              :style="{
                padding: '20px',
                background: '#FFFFFF',
                borderRadius: '12px',
                border: '1px solid #E8EAED'
              }"
            >
              <div :style="{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }">
                <div :style="{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #FF8F68, #F76D47)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#FFFFFF'
                }">
                  {{ index + 1 }}
                </div>
                <div :style="{ fontSize: '14px', fontWeight: 600, color: '#1A1F2E' }">
                  {{ issue.name }}
                </div>
                <div :style="{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  background: getCategoryColor(issue.category) + '20',
                  fontSize: '10px',
                  fontWeight: 600,
                  color: getCategoryColor(issue.category)
                }">
                  {{ getCategoryLabel(issue.category) }}
                </div>
              </div>

              <!-- Rating scales -->
              <div :style="{ marginBottom: '16px' }">
                <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '8px' }">
                  영향 중대성 (이해관계자 영향)
                </div>
                <div :style="{ display: 'flex', gap: '8px' }">
                  <div
                    v-for="score in 5"
                    :key="score"
                    :style="{
                      flex: 1,
                      height: '40px',
                      borderRadius: '6px',
                      border: '1px solid #E8EAED',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '12px',
                      fontWeight: 500,
                      color: '#6B7280',
                      cursor: 'pointer'
                    }"
                  >
                    {{ score }}
                  </div>
                </div>
              </div>

              <div>
                <div :style="{ fontSize: '12px', fontWeight: 600, color: '#1A1F2E', marginBottom: '8px' }">
                  재무 중대성 (재무적 영향)
                </div>
                <div :style="{ display: 'flex', gap: '8px' }">
                  <div
                    v-for="score in 5"
                    :key="score"
                    :style="{
                      flex: 1,
                      height: '40px',
                      borderRadius: '6px',
                      border: '1px solid #E8EAED',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '12px',
                      fontWeight: 500,
                      color: '#6B7280',
                      cursor: 'pointer'
                    }"
                  >
                    {{ score }}
                  </div>
                </div>
              </div>
            </div>

            <div :style="{ padding: '16px', textAlign: 'center', fontSize: '12px', color: '#9CA3AF' }">
              ... 외 {{ issues.length - 5 }}개 이슈
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div :style="{
          padding: '20px 32px',
          borderTop: '1px solid #E8EAED',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '12px'
        }">
          <button
            @click="showSurveyModal = false"
            :style="{
              padding: '10px 20px',
              background: '#F3F4F6',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 600,
              color: '#6B7280'
            }"
          >
            닫기
          </button>
          <button
            @click="handleSendSurvey"
            :style="{
              padding: '10px 24px',
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
          >
            <Send class="w-4 h-4" />
            전송하기
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- 벤치마크 상세 팝업 모달 -->
  <Teleport to="body">
    <div
      v-if="benchmarkDetailData"
      :style="{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999
      }"
      @click.self="benchmarkDetailData = null"
    >
      <div :style="{
        background: '#FFFFFF',
        borderRadius: '16px',
        width: '400px',
        maxWidth: '90vw',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        overflow: 'hidden'
      }">
        <!-- 헤더 -->
        <div :style="{
          background: '#EA7F52',
          padding: '16px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }">
          <div>
            <div :style="{ fontSize: '11px', color: 'rgba(255,255,255,0.8)', marginBottom: '2px' }">벤치마킹 상세</div>
            <div :style="{ fontSize: '16px', fontWeight: 600, color: '#FFFFFF' }">{{ benchmarkDetailData.company }}</div>
          </div>
          <button
            @click="benchmarkDetailData = null"
            :style="{
              background: 'rgba(255,255,255,0.2)',
              border: 'none',
              borderRadius: '50%',
              width: '28px',
              height: '28px',
              cursor: 'pointer',
              color: '#FFFFFF',
              fontSize: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }"
          >
            <X :size="16" />
          </button>
        </div>

        <!-- 본문 -->
        <div :style="{ padding: '20px' }">
          <!-- SK 이슈 -->
          <div :style="{ marginBottom: '16px' }">
            <div :style="{ fontSize: '12px', color: '#6B7280', marginBottom: '8px' }">SK 이슈</div>
            <div :style="{
              padding: '12px 16px',
              background: '#F9FAFB',
              borderRadius: '8px',
              fontSize: '14px',
              color: '#1F2937',
              border: '1px solid #E5E7EB'
            }">{{ benchmarkDetailData.issue }}</div>
          </div>

          <!-- 매핑된 이슈 -->
          <div :style="{ marginBottom: '16px' }">
            <div :style="{ fontSize: '12px', color: '#6B7280', marginBottom: '8px' }">{{ benchmarkDetailData.company }}의 매핑된 이슈</div>
            <div :style="{
              padding: '12px 16px',
              background: '#FFF7ED',
              borderRadius: '8px',
              fontSize: '14px',
              color: '#EA7F52',
              border: '1px solid #FDBA74'
            }">{{ benchmarkDetailData.matched_issue || '매핑된 이슈 없음' }}</div>
          </div>

          <!-- 참조 페이지 -->
          <div v-if="benchmarkDetailData.source_pages?.length > 0" :style="{ marginBottom: '20px' }">
            <div :style="{ fontSize: '12px', color: '#6B7280', marginBottom: '8px' }">참조 페이지</div>
            <div :style="{ display: 'flex', gap: '8px', flexWrap: 'wrap' }">
              <span
                v-for="page in benchmarkDetailData.source_pages.slice(0, 5)"
                :key="page"
                :style="{
                  padding: '6px 14px',
                  background: '#FFFFFF',
                  borderRadius: '20px',
                  fontSize: '13px',
                  color: '#EA7F52',
                  border: '1px solid #FDBA74',
                  fontWeight: 500
                }"
              >p. {{ page }}</span>
            </div>
          </div>

          <!-- 닫기 버튼 -->
          <button
            @click="benchmarkDetailData = null"
            :style="{
              width: '100%',
              padding: '12px',
              background: '#F3F4F6',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 500,
              color: '#374151',
              cursor: 'pointer'
            }"
          >닫기</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { FileText, X, Send, ExternalLink, AlertCircle } from 'lucide-vue-next'
// TODO: Restore when tabs are implemented
// import ESGStandardAnalysis from './issuepool/ESGStandardAnalysis.vue'
// import BenchmarkAnalysis from './issuepool/BenchmarkAnalysis.vue'
// import MediaAnalysis from './issuepool/MediaAnalysis.vue'
import DocumentList from './issuepool/DocumentList.vue'
import apiClient from '@/api/axios.config'
import aiClient from '@/api/aiClient'

// =============================================================================
// Cache Helpers - localStorage 기반 캐싱 (30분 유효)
// =============================================================================
const CACHE_DURATION = 30 * 60 * 1000 // 30 minutes

interface CacheEntry<T> {
  data: T
  timestamp: number
}

const getCache = <T>(key: string): T | null => {
  try {
    const cached = localStorage.getItem(key)
    if (!cached) return null

    const entry: CacheEntry<T> = JSON.parse(cached)
    const now = Date.now()

    if (now - entry.timestamp > CACHE_DURATION) {
      localStorage.removeItem(key)
      return null
    }

    return entry.data
  } catch {
    return null
  }
}

const setCache = <T>(key: string, data: T): void => {
  try {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now()
    }
    localStorage.setItem(key, JSON.stringify(entry))
  } catch (e) {
    console.warn('Cache storage failed:', e)
  }
}

interface Issue {
  id: string
  name: string
  category: 'environment' | 'social' | 'governance'
}

interface Analysis {
  id: string
  name: string
  documentName: string
  summary: string
  highlights: Array<{ text: string; page: number }>
}

interface BenchmarkResult {
  coverage: 'Yes' | 'Partially' | 'No'
  response: string
  matched_issue?: string
  source_pages: number[]
}

interface BenchmarkData {
  [company: string]: {
    [issue: string]: BenchmarkResult
  }
}

const mode = ref<'list' | 'config'>('list')
const selectedIssue = ref('issue1')
const selectedAnalysis = ref<string | null>(null)
const showSurveyModal = ref(false)

// 벤치마킹 데이터
const benchmarkLoading = ref(false)
const benchmarkData = ref<BenchmarkData>({})
const sk18Issues = ref<string[]>([])
const benchmarkDetailData = ref<{
  company: string
  issue: string
  matched_issue: string
  response: string
  source_pages: number[]
} | null>(null)

// ESG 표준 분석 데이터
interface ESGDisclosure {
  id: string
  title: string
  standard: string
  description?: string
}

interface ESGIssueWithStats {
  issue: string
  category: string
  disclosures: ESGDisclosure[]
  disclosure_count: number
  gri_count: number
  sasb_count: number
}

interface ESGAnalysisResult {
  issue: string
  category: string
  disclosures: ESGDisclosure[]
  analysis: {
    summary: string
    key_disclosures: string[]
    recommendations: string[]
  }
}

const esgStandardsLoading = ref(false)
const esgStandardsError = ref('')
const esgIssuesWithDisclosures = ref<ESGIssueWithStats[]>([])
// TODO: esgSelectedIssue - restore when ESG issue analysis tab is implemented
// const esgSelectedIssue = ref('')
const esgAnalysisResult = ref<ESGAnalysisResult | null>(null)
const esgAnalysisLoading = ref(false)

// 미디어 분석 데이터
interface MediaArticle {
  title: string
  clean_title?: string
  description: string
  clean_description?: string
  link: string
  pubDate: string
  sentiment: '긍정' | '부정' | '중립'
  sentiment_score: number
  esg_issues: string[]
  esg_categories?: string[]
}

const mediaLoading = ref(false)
const mediaError = ref('')
const mediaTotalArticles = ref(0)
const mediaPositiveCount = ref(0)
const mediaNegativeCount = ref(0)
const mediaNeutralCount = ref(0)
const mediaAvgScore = ref('0.00')
const mediaArticles = ref<MediaArticle[]>([])

const modeTabs = [
  { id: 'list', label: '문서목록' },
  { id: 'config', label: '이슈풀 구성' },
]


// 2024년 18개 이슈풀
const issues: Issue[] = [
  { id: 'issue1', name: '기후변화 대응', category: 'environment' },
  { id: 'issue2', name: '신재생에너지 확대 및 전력 효율화', category: 'environment' },
  { id: 'issue3', name: '환경영향 관리', category: 'environment' },
  { id: 'issue4', name: '생물다양성 보호', category: 'environment' },
  { id: 'issue5', name: '친환경 사업/기술 투자', category: 'environment' },
  { id: 'issue6', name: '인재양성 및 다양성', category: 'social' },
  { id: 'issue7', name: '인권경영 고도화', category: 'social' },
  { id: 'issue8', name: '안전보건 관리', category: 'social' },
  { id: 'issue9', name: '공급망 ESG 관리', category: 'governance' },
  { id: 'issue10', name: '책임있는 제품/서비스 관리', category: 'social' },
  { id: 'issue11', name: '정보보안 및 프라이버시', category: 'governance' },
  { id: 'issue12', name: '지역사회 공헌', category: 'social' },
  { id: 'issue13', name: '포트폴리오 ESG 관리', category: 'governance' },
  { id: 'issue14', name: '투명한 이사회 경영', category: 'governance' },
  { id: 'issue15', name: '윤리 및 컴플라이언스', category: 'governance' },
  { id: 'issue16', name: '주주가치 제고', category: 'governance' },
  { id: 'issue17', name: '리스크 관리', category: 'governance' },
  { id: 'issue18', name: 'ESG 공시 의무화 대응', category: 'governance' },
]

const analyses: Analysis[] = [
  {
    id: 'esg',
    name: 'ESG 표준 분석',
    documentName: '',
    summary: 'GRI 표준의 환경 관련 지표 및 보고 요구사항을 분석합니다.',
    highlights: []
  },
  {
    id: 'company',
    name: '기업 현황 분석',
    documentName: '',
    summary: 'SASB 산업별 지속가능성 회계 기준을 기반으로 기업 현황을 분석합니다.',
    highlights: []
  },
  {
    id: 'benchmark',
    name: '벤치마킹 분석',
    documentName: '',
    summary: '경쟁사 보고서를 분석하여 18개 이슈 커버리지를 비교합니다.',
    highlights: []
  },
  {
    id: 'media',
    name: '미디어 분석',
    documentName: '',
    summary: 'TCFD 권고안에 따른 기후 관련 재무정보 공개를 분석합니다.',
    highlights: []
  }
]

const benchmarkCompanies = computed(() => Object.keys(benchmarkData.value))

// 상위 5개 이슈 계산
const top5Issues = computed(() => {
  if (!sk18Issues.value || sk18Issues.value.length === 0) return []

  const issueCounts = sk18Issues.value.map(issue => {
    let count = 0
    for (const company of benchmarkCompanies.value) {
      if (getBenchmarkCoverage(company, issue) === 'Yes') {
        count++
      }
    }
    return { issue, count }
  })

  return issueCounts
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)
})

const currentIssue = computed(() => issues.find(i => i.id === selectedIssue.value))
const currentAnalysis = computed(() => analyses.find(a => a.id === selectedAnalysis.value))

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

// 벤치마킹 데이터 로드
const BENCHMARK_CACHE_KEY = 'esg_benchmark_data_cache'

interface BenchmarkCacheData {
  issues: string[]
  data: Record<string, any>
}

const loadBenchmarkData = async () => {
  benchmarkLoading.value = true

  // Check cache first (with validation)
  const cached = getCache<BenchmarkCacheData>(BENCHMARK_CACHE_KEY)
  if (cached && cached.issues && Array.isArray(cached.issues) && cached.issues.length > 0 && cached.data) {
    console.log('Using cached benchmark data')
    sk18Issues.value = cached.issues
    benchmarkData.value = cached.data
    benchmarkLoading.value = false
    return
  } else if (cached) {
    // Invalid cache format, clear it
    console.log('Invalid cache format detected, clearing cache')
    localStorage.removeItem(BENCHMARK_CACHE_KEY)
  }

  try {
    // SK 18개 이슈 목록 로드 (Python AI 서비스 직접 호출)
    const issuesResponse = await aiClient.get('/internal/v1/benchmarks/issues')
    if (issuesResponse.data.success) {
      sk18Issues.value = issuesResponse.data.issues
    }

    // 벤치마킹 데이터 로드 (Python AI 서비스 직접 호출)
    const dataResponse = await aiClient.get('/internal/v1/benchmarks/data')
    if (dataResponse.data.success) {
      benchmarkData.value = dataResponse.data.data

      // Save to cache
      setCache<BenchmarkCacheData>(BENCHMARK_CACHE_KEY, {
        issues: sk18Issues.value,
        data: benchmarkData.value
      })
    }
  } catch (error) {
    console.error('Failed to load benchmark data:', error)
  } finally {
    benchmarkLoading.value = false
  }
}

// 벤치마킹 커버리지 확인
const getBenchmarkCoverage = (company: string, issue: string): string => {
  return benchmarkData.value[company]?.[issue]?.coverage || 'No'
}

// 벤치마킹 상세 정보 표시
const showBenchmarkDetail = (company: string, issue: string) => {
  const data = benchmarkData.value[company]?.[issue]
  if (data) {
    // response에서 매핑된 이슈 추출 (유사도 제거)
    let matchedIssue = ''
    const response = data.response || ''

    if (response.startsWith('매칭:')) {
      // "매칭: XXX (유사도 YY%)" 패턴에서 XXX만 추출 (유사도 제거)
      const match = response.match(/매칭:\s*(.+?)(?:\s*\(유사도|$)/)
      if (match) {
        matchedIssue = match[1].trim()
      }
    } else if (response.startsWith('폴백 매칭:')) {
      // "폴백 매칭: 관련 섹션명: XXX (유사도 YY%)" 패턴에서 섹션명만 추출
      const match = response.match(/폴백 매칭:\s*(?:관련 섹션명:\s*|Related section:\s*)?(.+?)(?:\s*\(유사도|$)/)
      if (match) {
        matchedIssue = match[1].trim()
      }
    } else if (response.startsWith('키워드 발견:')) {
      // "키워드 발견: XXX" 패턴에서 키워드만 추출
      const match = response.match(/키워드 발견:\s*(.+)/)
      if (match) {
        matchedIssue = match[1].trim()
      }
    }

    benchmarkDetailData.value = {
      company,
      issue,
      matched_issue: matchedIssue,
      response: response,
      source_pages: data.source_pages || []
    }
  }
}

// 분석 선택 핸들러
const handleAnalysisSelect = (analysisId: string) => {
  selectedAnalysis.value = analysisId
  if (analysisId === 'benchmark') {
    loadBenchmarkData()
  } else if (analysisId === 'esg') {
    loadESGStandardsData()
  } else if (analysisId === 'media') {
    loadMediaData()
  }
}

const handleSendSurvey = () => {
  alert('설문조사가 전송되었습니다!')
  showSurveyModal.value = false
}

// 미디어 분석 함수들
const MEDIA_CACHE_KEY = 'esg_media_data_cache'

interface MediaCacheData {
  totalArticles: number
  articles: any[]
  positiveCount: number
  negativeCount: number
  neutralCount: number
  avgScore: string
}

const loadMediaData = async () => {
  mediaLoading.value = true
  mediaError.value = ''

  // Check cache first
  const cached = getCache<MediaCacheData>(MEDIA_CACHE_KEY)
  if (cached) {
    console.log('Using cached media data')
    mediaTotalArticles.value = cached.totalArticles
    mediaArticles.value = cached.articles
    mediaPositiveCount.value = cached.positiveCount
    mediaNegativeCount.value = cached.negativeCount
    mediaNeutralCount.value = cached.neutralCount
    mediaAvgScore.value = cached.avgScore
    mediaLoading.value = false
    return
  }

  try {
    const response = await apiClient.get('/api/v1/media')

    if (response.data.success) {
      const data = response.data.data

      mediaTotalArticles.value = data.total_articles || data.unique_articles || 0
      mediaArticles.value = data.articles || []

      const sentimentStats = data.statistics?.sentiment_statistics || {}
      mediaPositiveCount.value = sentimentStats['긍정'] || 0
      mediaNegativeCount.value = sentimentStats['부정'] || 0
      mediaNeutralCount.value = sentimentStats['중립'] || 0
      mediaAvgScore.value = (sentimentStats.avg_score || 0).toFixed(2)

      // Save to cache
      setCache<MediaCacheData>(MEDIA_CACHE_KEY, {
        totalArticles: mediaTotalArticles.value,
        articles: mediaArticles.value,
        positiveCount: mediaPositiveCount.value,
        negativeCount: mediaNegativeCount.value,
        neutralCount: mediaNeutralCount.value,
        avgScore: mediaAvgScore.value
      })
    } else {
      mediaError.value = response.data.error?.message || '데이터 로드 중 오류가 발생했습니다.'
    }
  } catch (error: any) {
    console.error('Media data load error:', error)
    mediaError.value = error.response?.data?.error?.message ||
                       error.message ||
                       '서버 연결에 실패했습니다.'
  } finally {
    mediaLoading.value = false
  }
}

const getMediaSentimentStyle = (sentiment: string) => {
  switch (sentiment) {
    case '긍정':
      return { background: '#D1FAE5', color: '#047857' }
    case '부정':
      return { background: '#FEE2E2', color: '#B91C1C' }
    case '중립':
      return { background: '#F3F4F6', color: '#6B7280' }
    default:
      return { background: '#F3F4F6', color: '#6B7280' }
  }
}

const formatMediaDate = (dateStr: string) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ko-KR', { month: '2-digit', day: '2-digit' })
  } catch {
    return dateStr
  }
}

const filteredMediaArticles = computed(() => {
  // 왼쪽 이슈 목록에서 선택된 이슈만 사용
  const issueToFilter = currentIssue.value?.name

  if (!issueToFilter) {
    return mediaArticles.value.slice(0, 10)
  }

  // 선택된 이슈와 관련된 기사만 필터링
  const filtered = mediaArticles.value.filter(article => {
    if (!article.esg_issues || article.esg_issues.length === 0) {
      return false
    }
    // 정확히 일치하거나 부분 일치하는 이슈가 있는지 확인
    return article.esg_issues.some(issue =>
      issue === issueToFilter ||
      issue.includes(issueToFilter) ||
      issueToFilter.includes(issue)
    )
  })

  // 필터링 결과가 없으면 빈 배열 반환 (관련 기사 없음 표시)
  return filtered.slice(0, 10)
})

const openMediaArticle = (link: string) => {
  if (link) {
    window.open(link, '_blank')
  }
}

// ESG 표준 분석 함수들
const ESG_STANDARDS_CACHE_KEY = 'esg_standards_data_cache'

const loadESGStandardsData = async () => {
  esgStandardsLoading.value = true
  esgStandardsError.value = ''

  // Check cache first
  const cached = getCache<any[]>(ESG_STANDARDS_CACHE_KEY)
  if (cached) {
    console.log('Using cached ESG standards data')
    esgIssuesWithDisclosures.value = cached
    esgStandardsLoading.value = false
    return
  }

  try {
    const response = await apiClient.get('/api/v1/standards/issues/with-disclosures')
    if (response.data.success) {
      esgIssuesWithDisclosures.value = response.data.data
      // Save to cache
      setCache(ESG_STANDARDS_CACHE_KEY, response.data.data)
    } else {
      esgStandardsError.value = response.data.error?.message || '데이터 로드에 실패했습니다.'
    }
  } catch (error: any) {
    console.error('ESG Standards load error:', error)
    esgStandardsError.value = error.response?.data?.error?.message ||
                              error.message ||
                              '서버 연결에 실패했습니다.'
  } finally {
    esgStandardsLoading.value = false
  }
}

// TODO: handleESGIssueSelect - restore when ESG issue analysis tab is implemented
// const handleESGIssueSelect = async (issueName: string) => { ... }

const getESGCategoryColor = (category: string) => {
  switch (category) {
    case 'E': return '#10B981'
    case 'S': return '#3B82F6'
    case 'G': return '#8B5CF6'
    default: return '#6B7280'
  }
}

const getESGCategoryLabel = (category: string) => {
  switch (category) {
    case 'E': return '환경'
    case 'S': return '사회'
    case 'G': return '지배구조'
    default: return ''
  }
}

const getStandardColor = (standard: string) => {
  return standard === 'GRI' ? '#EA7F52' : '#0891B2'
}

const selectedESGIssueData = computed(() => {
  // 왼쪽 이슈 목록에서 선택된 이슈 이름 기반으로 공시 데이터 찾기
  const issueName = currentIssue.value?.name
  if (!issueName) return null
  return esgIssuesWithDisclosures.value.find(i => i.issue === issueName)
})
</script>

<style>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
