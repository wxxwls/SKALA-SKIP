/**
 * Report Store
 *
 * ESG 보고서 상태 관리 (Pinia)
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import {
  reportApi,
  type MaterialityAssessmentSaveRequest,
  type MaterialityAssessmentSaveResponse,
  type ESGReportResponse
} from '@/api/report.api';

export const useReportStore = defineStore('report', () => {
  // ============================================
  // State
  // ============================================

  /** 현재 보고서 */
  const currentReport = ref<ESGReportResponse | null>(null);

  /** 마지막 저장 응답 */
  const lastSaveResponse = ref<MaterialityAssessmentSaveResponse | null>(null);

  /** 로딩 상태 */
  const isLoading = ref(false);

  /** 보고서 생성 중 상태 */
  const isGenerating = ref(false);

  /** 에러 상태 */
  const error = ref<string | null>(null);

  // ============================================
  // Getters
  // ============================================

  /** 보고서가 있는지 여부 */
  const hasReport = computed(() => currentReport.value !== null);

  /** 보고서 HTML */
  const reportHtml = computed(() => currentReport.value?.reportHtml || '');

  /** 보고서 메타데이터 */
  const reportMetadata = computed(() => currentReport.value?.metadata || null);

  /** 보고서 생성 상태 */
  const generationStatus = computed(() => lastSaveResponse.value?.reportStatus || null);

  // ============================================
  // Actions
  // ============================================

  /**
   * 중대성 평가 저장 및 보고서 생성
   */
  async function saveAndGenerateReport(request: MaterialityAssessmentSaveRequest): Promise<MaterialityAssessmentSaveResponse> {
    isLoading.value = true;
    isGenerating.value = true;
    error.value = null;

    try {
      const response = await reportApi.saveAndGenerateReport(request.companyId, request);
      lastSaveResponse.value = response;

      // 보고서 생성 성공 시 자동으로 보고서 조회
      if (response.reportStatus.status === 'COMPLETED' && response.reportStatus.reportId) {
        await fetchReport(request.companyId, request.reportYear);
      }

      return response;
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : '보고서 생성에 실패했습니다';
      error.value = errorMessage;
      throw e;
    } finally {
      isLoading.value = false;
      isGenerating.value = false;
    }
  }

  /**
   * 보고서 조회
   */
  async function fetchReport(companyId: string, year: number): Promise<ESGReportResponse> {
    isLoading.value = true;
    error.value = null;

    try {
      const report = await reportApi.getReport(companyId, year);
      currentReport.value = report;
      return report;
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : '보고서를 불러오는데 실패했습니다';
      error.value = errorMessage;
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * 보고서 재생성
   */
  async function regenerateReport(companyId: string, year: number): Promise<ESGReportResponse> {
    isLoading.value = true;
    isGenerating.value = true;
    error.value = null;

    try {
      const report = await reportApi.regenerateReport(companyId, year);
      currentReport.value = report;
      return report;
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : '보고서 재생성에 실패했습니다';
      error.value = errorMessage;
      throw e;
    } finally {
      isLoading.value = false;
      isGenerating.value = false;
    }
  }

  /**
   * 상태 초기화
   */
  function resetState() {
    currentReport.value = null;
    lastSaveResponse.value = null;
    error.value = null;
    isLoading.value = false;
    isGenerating.value = false;
  }

  /**
   * 에러 클리어
   */
  function clearError() {
    error.value = null;
  }

  return {
    // State
    currentReport,
    lastSaveResponse,
    isLoading,
    isGenerating,
    error,

    // Getters
    hasReport,
    reportHtml,
    reportMetadata,
    generationStatus,

    // Actions
    saveAndGenerateReport,
    fetchReport,
    regenerateReport,
    resetState,
    clearError
  };
});
