"""
Report Assistant Service - ESG 보고서 생성 서비스

SK 지속가능경영보고서 '발생영향과 통제' 챕터 스타일로 보고서 생성
영향 중대성 상위 5개 + 재무 중대성 상위 5개 = 총 10개 이슈 처리

CRITICAL CONSTRAINTS:
- 내부 데이터만 사용 (외부 검색 금지)
- 임의 수치 생성 금지
- NULL KPI는 "※ 내부 데이터 미등록" 표시 필수
"""

import time
from pathlib import Path
from typing import Optional

from app.core.exceptions import ReportGenerationError
from app.core.logging import get_logger
from app.schemas.report_schema import (
    ErrorInfo,
    IssueForReport,
    KPIData,
    ProcessingMetadata,
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportModifyRequest,
    ReportModifyResponse,
    SectionData,
)
from app.llm.clients.openai_client import get_openai_client

logger = get_logger(__name__)

# 프롬프트 템플릿 경로
PROMPTS_DIR = Path(__file__).parent.parent / "llm" / "prompts" / "report"


class ReportAssistantService:
    """
    ESG 보고서 생성 서비스

    Responsibilities:
    - 영향 중대성 상위 5개 이슈 섹션 생성
    - 재무 중대성 상위 5개 이슈 섹션 생성
    - 각 중대성 유형별 핵심 이슈 분석 표 생성
    - 전체 보고서 HTML 통합
    - KPI NULL 처리 ("※ 내부 데이터 미등록")
    """

    def __init__(self):
        """Initialize report assistant service"""
        self._load_prompts()
        logger.info("Initialized ReportAssistantService")

    def _load_prompts(self):
        """Load prompt templates from files"""
        try:
            impact_prompt_path = PROMPTS_DIR / "impact_section.txt"
            financial_prompt_path = PROMPTS_DIR / "financial_section.txt"
            full_report_prompt_path = PROMPTS_DIR / "v1_full_report.txt"

            with open(impact_prompt_path, "r", encoding="utf-8") as f:
                self.impact_prompt_template = f.read()

            with open(financial_prompt_path, "r", encoding="utf-8") as f:
                self.financial_prompt_template = f.read()

            with open(full_report_prompt_path, "r", encoding="utf-8") as f:
                self.full_report_prompt_template = f.read()

            logger.info("Loaded prompt templates successfully")
        except FileNotFoundError as e:
            logger.error(f"Prompt template not found: {e}")
            raise ReportGenerationError(
                message="프롬프트 템플릿을 찾을 수 없습니다",
                details={"path": str(e)}
            )

    async def generate_report(
        self, request: ReportGenerationRequest
    ) -> ReportGenerationResponse:
        """
        ESG 보고서 생성

        Process:
        1. 영향 중대성 상위 5개 이슈 섹션 생성
        2. 재무 중대성 상위 5개 이슈 섹션 생성
        3. 핵심 이슈 분석 표 생성
        4. 전체 보고서 HTML 통합
        5. 응답 반환

        Args:
            request: 보고서 생성 요청

        Returns:
            ReportGenerationResponse
        """
        # =====================================================================
        # TODO: [SPRING-BOOT-INPUT] Spring Boot에서 입력 데이터 수신
        # =====================================================================
        # Spring Boot가 이 API를 호출할 때 다음 데이터를 RDB에서 조회하여 전달:
        #
        # ▶ 1. company_context (companies 테이블):
        # SELECT company_id, company_name, industry, sector
        # FROM companies WHERE company_id = :company_id;
        #
        # ▶ 2. issues (issues + issue_pools 테이블):
        # SELECT i.issue_id, i.title, i.esg_category, i.description,
        #        i.financial_score, i.impact_score, i.overall_score,
        #        i.priority_rank, i.status
        # FROM issues i
        # JOIN issue_pools ip ON i.issue_pool_id = ip.issue_pool_id
        # WHERE ip.company_id = :company_id
        #   AND ip.year = :year
        #   AND ip.status = 'CONFIRMED'
        #   AND i.status = 'SELECTED'
        # ORDER BY i.priority_rank ASC;
        #
        # ▶ 3. impact_priority_issue_ids (영향 중대성 상위 5개):
        # SELECT issue_id FROM issues i
        # JOIN issue_pools ip ON i.issue_pool_id = ip.issue_pool_id
        # WHERE ip.company_id = :company_id AND ip.year = :year
        #   AND i.status = 'SELECTED'
        # ORDER BY i.impact_score DESC
        # LIMIT 5;
        #
        # ▶ 4. financial_priority_issue_ids (재무 중대성 상위 5개):
        # SELECT issue_id FROM issues i
        # JOIN issue_pools ip ON i.issue_pool_id = ip.issue_pool_id
        # WHERE ip.company_id = :company_id AND ip.year = :year
        #   AND i.status = 'SELECTED'
        # ORDER BY i.financial_score DESC
        # LIMIT 5;
        #
        # ▶ 5. kpi_data_by_issue (KPI 데이터 - sk_data 또는 별도 KPI 테이블):
        # SELECT sd.issue_id, sd.kpi_name, sd.kpi_value, sd.unit, sd.year
        # FROM sk_data sd  -- 또는 별도 kpi_data 테이블
        # WHERE sd.company_id = :company_id
        #   AND sd.year = :year
        #   AND sd.issue_id IN (:selected_issue_ids);
        #
        # → kpi_data_by_issue = {
        #     123: [
        #         {"kpi_name": "온실가스 배출량", "kpi_value": "50,000", "unit": "tCO2eq", "is_null": False},
        #         ...
        #     ],
        #     ...
        # }
        # =====================================================================
        start_time = time.time()

        try:
            logger.info(
                f"Generating report for {request.company_context.company_name} "
                f"({request.company_context.year})",
                extra={
                    "company_id": request.company_context.company_id,
                    "issue_count": len(request.issues),
                },
            )

            # 호환성: 기존 priority_issue_ids가 있으면 새 필드로 분배
            impact_ids = set(request.impact_priority_issue_ids)
            financial_ids = set(request.financial_priority_issue_ids)

            # 기존 방식 호환 (priority_issue_ids만 있는 경우)
            if not impact_ids and not financial_ids and request.priority_issue_ids:
                # 기존 방식: 평균 점수로 정렬된 상위 5개를 양쪽에 분배
                all_issues_by_id = {issue.get_issue_id: issue for issue in request.issues}
                for issue_id in request.priority_issue_ids[:5]:
                    impact_ids.add(issue_id)
                    financial_ids.add(issue_id)

            # 이슈 맵 생성
            issues_by_id = {issue.get_issue_id: issue for issue in request.issues}

            # 영향 중대성 상위 5개 이슈 추출
            impact_issues = [
                issues_by_id[issue_id]
                for issue_id in request.impact_priority_issue_ids
                if issue_id in issues_by_id
            ][:5]

            # 재무 중대성 상위 5개 이슈 추출
            financial_issues = [
                issues_by_id[issue_id]
                for issue_id in request.financial_priority_issue_ids
                if issue_id in issues_by_id
            ][:5]

            # 1. 영향 중대성 섹션 생성
            impact_sections: list[SectionData] = []
            for rank, issue in enumerate(impact_issues, 1):
                kpi_data = request.kpi_data_by_issue.get(issue.get_issue_id, [])
                section = await self._generate_impact_section(
                    request.company_context,
                    issue,
                    kpi_data,
                    rank,
                )
                impact_sections.append(section)

            # 2. 재무 중대성 섹션 생성
            financial_sections: list[SectionData] = []
            for rank, issue in enumerate(financial_issues, 1):
                kpi_data = request.kpi_data_by_issue.get(issue.get_issue_id, [])
                section = await self._generate_financial_section(
                    request.company_context,
                    issue,
                    kpi_data,
                    rank,
                )
                financial_sections.append(section)

            # 3. 전체 보고서 HTML 통합
            full_html = self._combine_sections_to_report(
                request.company_context,
                impact_sections,
                financial_sections,
                impact_issues,
                financial_issues,
            )

            # 4. 처리 시간 계산
            processing_time_ms = int((time.time() - start_time) * 1000)

            all_sections = impact_sections + financial_sections

            logger.info(
                f"Successfully generated report with {len(all_sections)} sections "
                f"(impact: {len(impact_sections)}, financial: {len(financial_sections)}) "
                f"in {processing_time_ms}ms"
            )

            # =================================================================
            # TODO: [SPRING-BOOT-OUTPUT] Spring Boot가 보고서를 RDB에 저장
            # =================================================================
            # 이 API의 응답(ReportGenerationResponse)을 받은 Spring Boot는:
            #
            # ▶ 1. reports 테이블에 보고서 생성:
            # INSERT INTO reports (
            #     company_id,      -- bigint NOT NULL (company_context.company_id)
            #     issue_pool_id,   -- bigint NOT NULL (선택된 이슈풀 ID)
            #     title,           -- varchar(255) NOT NULL (예: '2024년 ESG 중대성 이슈 보고서')
            #     version_no,      -- int NOT NULL (버전 번호)
            #     status,          -- varchar(20) NOT NULL ('DRAFT'|'REVIEW'|'FINAL')
            #     generated_by,    -- varchar(50) NOT NULL ('AI'|'MANUAL')
            #     report_html,     -- text (response.report_html - 전체 HTML)
            #     created_at,      -- timestamptz DEFAULT now()
            #     updated_at       -- timestamptz DEFAULT now()
            # ) VALUES (
            #     :company_id,
            #     :issue_pool_id,
            #     :company_name || ' ' || :year || '년 ESG 중대성 이슈 보고서',
            #     (SELECT COALESCE(MAX(version_no), 0) + 1 FROM reports
            #      WHERE company_id = :company_id AND issue_pool_id = :issue_pool_id),
            #     'DRAFT',
            #     'AI',
            #     :report_html,
            #     now(),
            #     now()
            # ) RETURNING report_id;
            #
            # ▶ 2. report_sections 테이블에 각 섹션 저장:
            # for section in response.sections:
            #     INSERT INTO report_sections (
            #         report_id,       -- bigint NOT NULL (위에서 생성된 report_id)
            #         issue_id,        -- bigint (section.issue_id)
            #         section_title,   -- varchar(255) NOT NULL (section.issue_name)
            #         ai_draft_text,   -- text (section.section_html - AI 생성 초안)
            #         final_text,      -- text (NULL - 사용자 수정 후 저장)
            #         order_no,        -- int (section.priority_rank)
            #         materiality_type,-- varchar(20) (section.materiality_type: 'impact'|'financial')
            #         created_at,      -- timestamptz DEFAULT now()
            #         updated_at       -- timestamptz DEFAULT now()
            #     ) VALUES (
            #         :report_id,
            #         :section.issue_id,
            #         :section.issue_name,
            #         :section.section_html,
            #         NULL,
            #         :section.priority_rank,
            #         :section.materiality_type,
            #         now(),
            #         now()
            #     );
            #
            # ▶ 3. 응답 데이터 매핑:
            # - response.report_html → reports.report_html
            # - response.sections → report_sections 테이블
            # - response.metadata.processing_time_ms → 로그 또는 별도 메트릭 테이블
            # - response.metadata.ai_model → reports 테이블에 ai_model 컬럼 추가 권장
            # =================================================================

            return ReportGenerationResponse(
                success=True,
                report_html=full_html,
                sections=all_sections,
                metadata=ProcessingMetadata(
                    processing_time_ms=processing_time_ms,
                    ai_model="gpt-4",
                    tokens_used=None,
                    sources_used=["internal_kpi", "issue_pool"],
                ),
            )

        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}", exc_info=True)
            return ReportGenerationResponse(
                success=False,
                error=ErrorInfo(
                    code="ESG-AI-RPT-001",
                    message="보고서 생성 실패",
                    details=str(e),
                ),
            )

    async def _generate_impact_section(
        self,
        company_context,
        issue: IssueForReport,
        kpi_data: list[KPIData],
        priority_rank: int,
    ) -> SectionData:
        """
        영향 중대성 이슈 섹션 HTML 생성

        영향 중대성 관점:
        - 실질적/잠재적 영향
        - 대응 전략
        - 중장기 계획
        """
        _, missing_kpis = self._format_kpi_data(kpi_data)
        has_kpi_data = any(not kpi.is_null for kpi in kpi_data)

        category_kr = self._get_category_kr(issue.category)

        openai_client = get_openai_client()

        kpi_data_dicts = [
            {
                "kpi_name": kpi.kpi_name,
                "kpi_value": kpi.kpi_value,
                "unit": kpi.unit,
                "is_null": kpi.is_null,
            }
            for kpi in kpi_data
        ]

        logger.info(f"Generating impact section for issue: {issue.get_issue_name} (rank {priority_rank})")

        section_html = await openai_client.generate_impact_section(
            company_name=company_context.company_name,
            industry=company_context.industry,
            year=company_context.year,
            issue_id=issue.get_issue_id,
            issue_name=issue.get_issue_name,
            category=category_kr,
            impact_score=issue.impact_score,
            kpi_data=kpi_data_dicts,
            priority_rank=priority_rank,
        )

        # 섹션 HTML 래핑
        priority_badge = f'<span class="priority-badge">{priority_rank}.</span>'
        category_badge = f'<span class="category-badge category-{issue.category}">{category_kr}</span>'

        wrapped_html = f"""
<section class="impact-issue-detail" id="impact-{issue.get_issue_id}" data-issue-id="{issue.get_issue_id}" data-category="{issue.category}" data-priority="{priority_rank}">
    <h3 class="issue-title">{priority_badge}{issue.get_issue_name}{category_badge}</h3>
    {section_html}
</section>
"""

        return SectionData(
            issue_id=issue.get_issue_id,
            issue_name=issue.get_issue_name,
            category=issue.category,
            materiality_type="impact",
            priority_rank=priority_rank,
            section_html=wrapped_html,
            has_kpi_data=has_kpi_data,
            missing_kpis=missing_kpis,
        )

    async def _generate_financial_section(
        self,
        company_context,
        issue: IssueForReport,
        kpi_data: list[KPIData],
        priority_rank: int,
    ) -> SectionData:
        """
        재무 중대성 이슈 섹션 HTML 생성

        재무 중대성 관점:
        - 위험/기회 분석
        - 대응 전략
        - KPI
        - 중장기 계획
        """
        _, missing_kpis = self._format_kpi_data(kpi_data)
        has_kpi_data = any(not kpi.is_null for kpi in kpi_data)

        category_kr = self._get_category_kr(issue.category)

        openai_client = get_openai_client()

        kpi_data_dicts = [
            {
                "kpi_name": kpi.kpi_name,
                "kpi_value": kpi.kpi_value,
                "unit": kpi.unit,
                "is_null": kpi.is_null,
            }
            for kpi in kpi_data
        ]

        logger.info(f"Generating financial section for issue: {issue.get_issue_name} (rank {priority_rank})")

        section_html = await openai_client.generate_financial_section(
            company_name=company_context.company_name,
            industry=company_context.industry,
            year=company_context.year,
            issue_id=issue.get_issue_id,
            issue_name=issue.get_issue_name,
            category=category_kr,
            financial_score=issue.financial_score,
            kpi_data=kpi_data_dicts,
            priority_rank=priority_rank,
        )

        # 섹션 HTML 래핑
        priority_badge = f'<span class="priority-badge financial">{priority_rank}.</span>'
        category_badge = f'<span class="category-badge category-{issue.category}">{category_kr}</span>'

        wrapped_html = f"""
<section class="financial-issue-detail" id="financial-{issue.get_issue_id}" data-issue-id="{issue.get_issue_id}" data-category="{issue.category}" data-priority="{priority_rank}">
    <h3 class="issue-title">{priority_badge}{issue.get_issue_name}{category_badge}</h3>
    {section_html}
</section>
"""

        return SectionData(
            issue_id=issue.get_issue_id,
            issue_name=issue.get_issue_name,
            category=issue.category,
            materiality_type="financial",
            priority_rank=priority_rank,
            section_html=wrapped_html,
            has_kpi_data=has_kpi_data,
            missing_kpis=missing_kpis,
        )

    def _format_kpi_data(self, kpi_data: list[KPIData]) -> tuple[str, list[str]]:
        """
        KPI 데이터를 HTML 테이블로 포맷팅

        Returns:
            (kpi_html, missing_kpis)
        """
        if not kpi_data:
            return "", []

        missing_kpis = []
        rows = []

        for kpi in kpi_data:
            if kpi.is_null or kpi.kpi_value is None:
                missing_kpis.append(kpi.kpi_name)
                rows.append(
                    f'<tr><td>{kpi.kpi_name}</td>'
                    f'<td class="no-data">※ 내부 데이터 미등록</td>'
                    f'<td>{kpi.unit or "-"}</td></tr>'
                )
            else:
                rows.append(
                    f'<tr><td>{kpi.kpi_name}</td>'
                    f'<td>{kpi.kpi_value}</td>'
                    f'<td>{kpi.unit or "-"}</td></tr>'
                )

        kpi_html = f"""
        <div class="kpi-list">
            <h4>관련 KPI</h4>
            <table>
                <thead>
                    <tr>
                        <th>지표명</th>
                        <th>현재값</th>
                        <th>단위</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </div>
        """

        return kpi_html, missing_kpis

    def _get_category_kr(self, category: str) -> str:
        """카테고리 한글 변환"""
        mapping = {
            "E": "환경",
            "S": "사회",
            "G": "지배구조",
            "Cross": "복합",
        }
        return mapping.get(category, "기타")

    def _build_impact_analysis_table(self, issues: list[IssueForReport]) -> str:
        """영향 중대성 핵심 이슈 분석 표 생성"""
        rows = []
        for issue in issues:
            impact_level = "상" if issue.impact_score > 70 else "중" if issue.impact_score > 40 else "하"
            rows.append(f"""
            <tr>
                <td class="issue-name">{issue.get_issue_name}</td>
                <td><span class="no-data">※ 내부 데이터 미등록</span></td>
                <td>{impact_level}</td>
                <td><span class="no-data">※ 내부 데이터 미등록</span></td>
                <td><span class="no-data">※ 내부 데이터 미등록</span></td>
                <td><span class="no-data">※ 내부 데이터 미등록</span></td>
                <td><span class="no-data">※ 내부 데이터 미등록</span></td>
            </tr>
            """)
        return "\n".join(rows)

    def _build_financial_analysis_table(self, issues: list[IssueForReport]) -> str:
        """재무 중대성 핵심 이슈 분석 표 생성"""
        rows = []
        for issue in issues:
            risk_level = "상" if issue.financial_score > 70 else "중" if issue.financial_score > 40 else "하"
            rows.append(f"""
            <tr>
                <td class="issue-name">{issue.get_issue_name}</td>
                <td><span class="no-data">※ 내부 데이터 미등록</span></td>
                <td>{risk_level}</td>
                <td><span class="no-data">-</span></td>
                <td>{risk_level}</td>
                <td><span class="no-data">-</span></td>
                <td><span class="no-data">※ 내부 데이터 미등록</span></td>
                <td><span class="no-data">※ 내부 데이터 미등록</span></td>
            </tr>
            """)
        return "\n".join(rows)

    def _combine_sections_to_report(
        self,
        company_context,
        impact_sections: list[SectionData],
        financial_sections: list[SectionData],
        impact_issues: list[IssueForReport],
        financial_issues: list[IssueForReport],
    ) -> str:
        """
        개별 섹션을 전체 보고서 HTML로 통합
        """
        # 목차 생성
        impact_toc_items = []
        for section in impact_sections:
            impact_toc_items.append(
                f'<li><a href="#impact-{section.issue_id}">{section.priority_rank}. {section.issue_name}</a></li>'
            )

        financial_toc_items = []
        for section in financial_sections:
            financial_toc_items.append(
                f'<li><a href="#financial-{section.issue_id}">{section.priority_rank}. {section.issue_name}</a></li>'
            )

        impact_toc_html = "\n".join(impact_toc_items)
        financial_toc_html = "\n".join(financial_toc_items)

        # 핵심 이슈 분석 표 생성
        impact_table_rows = self._build_impact_analysis_table(impact_issues)
        financial_table_rows = self._build_financial_analysis_table(financial_issues)

        # 섹션 HTML 통합
        impact_sections_html = "\n".join([s.section_html for s in impact_sections])
        financial_sections_html = "\n".join([s.section_html for s in financial_sections])

        # 이슈 이름 목록
        impact_names = [s.issue_name for s in impact_sections[:3]]
        financial_names = [s.issue_name for s in financial_sections[:3]]

        # 전체 보고서 HTML
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{company_context.company_name} ESG 중대성 이슈 보고서 {company_context.year}</title>
    <style>
        body {{ font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; color: #1A1F2E; margin: 0; padding: 0; background: #F7F8FA; }}
        .report-container {{ max-width: 1200px; margin: 0 auto; padding: 40px; background: #FFFFFF; }}
        .report-header {{ text-align: center; margin-bottom: 40px; border-bottom: 3px solid #FF7A00; padding-bottom: 24px; }}
        .report-title {{ font-size: 32px; font-weight: 700; color: #1A1F2E; margin: 0; }}
        .report-subtitle {{ font-size: 18px; color: #6B7280; margin-top: 12px; }}

        /* 목차 */
        .toc {{ background: #F7F8FA; padding: 28px; border-radius: 12px; margin-bottom: 48px; }}
        .toc h3 {{ margin: 0 0 16px 0; color: #FF7A00; font-size: 18px; }}
        .toc-section {{ margin-bottom: 16px; }}
        .toc-section-title {{ font-weight: 600; color: #1A1F2E; margin-bottom: 8px; font-size: 14px; }}
        .toc-section-title.financial {{ color: #FF7A00; }}
        .toc ul {{ list-style: none; padding: 0; margin: 0 0 0 16px; }}
        .toc li {{ padding: 4px 0; }}
        .toc a {{ color: #374151; text-decoration: none; font-size: 13px; }}
        .toc a:hover {{ color: #FF7A00; }}

        /* 섹션 헤더 */
        .section-header {{ background: linear-gradient(135deg, #FF8F68, #F76D47); color: white; padding: 24px 32px; border-radius: 12px; margin: 48px 0 32px 0; }}
        .section-header.financial {{ background: linear-gradient(135deg, #FF8F68, #F76D47); }}
        .section-header h2 {{ margin: 0; font-size: 24px; }}
        .section-header p {{ margin: 8px 0 0 0; opacity: 0.9; font-size: 14px; }}

        /* 핵심 이슈 분석 표 */
        .analysis-section {{ margin: 32px 0; }}
        .analysis-section h3 {{ font-size: 18px; color: #1A1F2E; margin: 0 0 16px 0; border-left: 4px solid #FF7A00; padding-left: 12px; }}
        .analysis-section.financial h3 {{ border-left-color: #FF7A00; }}
        .analysis-table-container {{ overflow-x: auto; }}
        .analysis-table {{ width: 100%; border-collapse: collapse; font-size: 12px; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-radius: 12px; overflow: hidden; }}
        .analysis-table thead {{ background: linear-gradient(135deg, #FF8F68, #F76D47); color: white; }}
        .analysis-table.financial thead {{ background: linear-gradient(135deg, #FF8F68, #F76D47); }}
        .analysis-table th {{ padding: 14px 10px; text-align: center; font-weight: 600; font-size: 11px; border-right: 1px solid rgba(255,255,255,0.2); }}
        .analysis-table th:last-child {{ border-right: none; }}
        .analysis-table td {{ padding: 12px 10px; vertical-align: middle; border-bottom: 1px solid #E8EAED; border-right: 1px solid #E8EAED; text-align: center; font-size: 12px; }}
        .analysis-table td:last-child {{ border-right: none; }}
        .analysis-table td.issue-name {{ font-weight: 600; color: #1A1F2E; text-align: left; background: #FFF9F6; min-width: 120px; }}
        .analysis-table.financial td.issue-name {{ background: #FFF9F6; }}
        .analysis-table tbody tr:hover {{ background: #FAFBFC; }}
        .no-data {{ color: #9CA3AF; font-style: italic; font-size: 10px; }}

        /* 이슈 상세 카드 */
        .impact-issue-detail, .financial-issue-detail {{ margin: 32px 0; }}
        .issue-title {{ font-size: 18px; font-weight: 700; color: #1A1F2E; margin: 0 0 16px 0; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
        .priority-badge {{ display: inline-flex; align-items: center; background: linear-gradient(135deg, #FF8F68, #F76D47); color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
        .priority-badge.financial {{ background: linear-gradient(135deg, #FF8F68, #F76D47); }}
        .category-badge {{ display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 500; }}
        .category-E {{ background: #D1FAE5; color: #059669; }}
        .category-S {{ background: #DBEAFE; color: #2563EB; }}
        .category-G {{ background: #EDE9FE; color: #7C3AED; }}

        .issue-detail-card {{ background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); border: 1px solid #E8EAED; }}
        .issue-detail-card.impact {{ border-left: 4px solid #FF7A00; }}
        .issue-detail-card.financial {{ border-left: 4px solid #FF7A00; }}
        .issue-section {{ display: flex; border-bottom: 1px solid #E8EAED; }}
        .issue-section:last-child {{ border-bottom: none; }}
        .section-label {{ flex-shrink: 0; width: 140px; padding: 20px 24px; background: #F9FAFB; font-weight: 700; font-size: 14px; color: #1A1F2E; border-right: 1px solid #E8EAED; }}
        .section-content {{ flex: 1; padding: 20px 24px; }}
        .section-content p {{ margin: 0 0 12px 0; line-height: 1.8; font-size: 14px; color: #374151; }}
        .section-content p:last-child {{ margin-bottom: 0; }}
        .section-content ul, .section-content ol {{ margin: 8px 0; padding-left: 20px; }}
        .section-content li {{ margin: 6px 0; line-height: 1.6; font-size: 14px; color: #374151; }}

        /* 영향/위험 요약 */
        .impact-summary {{ margin-top: 16px; padding-top: 16px; border-top: 1px dashed #E8EAED; }}
        .impact-item {{ font-size: 13px; color: #6B7280; margin: 6px 0; }}
        .impact-item strong {{ color: #FF7A00; }}

        /* 위험/기회 박스 */
        .risk-opportunity-summary {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }}
        .risk-box, .opportunity-box {{ padding: 16px; border-radius: 8px; }}
        .risk-box {{ background: #FEF2F2; border: 1px solid #FECACA; }}
        .opportunity-box {{ background: #F0FDF4; border: 1px solid #BBF7D0; }}
        .risk-box h5, .opportunity-box h5 {{ margin: 0 0 12px 0; font-size: 14px; }}
        .risk-box h5 {{ color: #DC2626; }}
        .opportunity-box h5 {{ color: #16A34A; }}
        .risk-item, .opp-item {{ font-size: 12px; color: #374151; margin: 6px 0; }}

        /* KPI 테이블 */
        .kpi-list {{ margin-top: 16px; }}
        .kpi-list h4 {{ font-size: 14px; color: #374151; margin: 0 0 12px 0; }}
        .kpi-list table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        .kpi-list th, .kpi-list td {{ padding: 12px; text-align: left; border-bottom: 1px solid #E8EAED; }}
        .kpi-list th {{ background: #F7F8FA; font-weight: 600; color: #374151; }}

        /* 결론 */
        .conclusion {{ background: linear-gradient(135deg, #FFF9F5, #FFFFFF); padding: 32px; border-radius: 12px; border: 1px solid #FFE5D6; margin-top: 48px; }}
        .conclusion h3 {{ color: #FF7A00; margin: 0 0 16px 0; font-size: 20px; }}
        .conclusion p {{ margin: 0 0 12px 0; color: #374151; line-height: 1.8; }}

        @media print {{
            body {{ background: white; }}
            .report-container {{ box-shadow: none; }}
            .section-header, .issue-detail-card {{ break-inside: avoid; page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <header class="report-header">
            <h1 class="report-title">{company_context.company_name}</h1>
            <h1 class="report-title">ESG 중대성 이슈 보고서</h1>
            <p class="report-subtitle">{company_context.year}년 지속가능경영 · 이중 중대성 평가 결과</p>
        </header>

        <nav class="toc">
            <h3>목차</h3>
            <div class="toc-section">
                <div class="toc-section-title">I. 영향 중대성 (Impact Materiality)</div>
                <ul>
                    <li><a href="#impact-analysis">핵심 이슈 분석</a></li>
                    {impact_toc_html}
                </ul>
            </div>
            <div class="toc-section">
                <div class="toc-section-title financial">II. 재무 중대성 (Financial Materiality)</div>
                <ul>
                    <li><a href="#financial-analysis">핵심 이슈 분석</a></li>
                    {financial_toc_html}
                </ul>
            </div>
        </nav>

        <!-- I. 영향 중대성 섹션 -->
        <div class="section-header" id="impact-section">
            <h2>I. 영향 중대성 (Impact Materiality)</h2>
            <p>기업의 경영 활동이 환경 및 사회에 미치는 영향 관점의 중대 이슈</p>
        </div>

        <div class="analysis-section" id="impact-analysis">
            <h3>핵심 이슈 분석</h3>
            <div class="analysis-table-container">
                <table class="analysis-table">
                    <thead>
                        <tr>
                            <th>중요주제</th>
                            <th>영향받는<br>가치사슬 범위</th>
                            <th>영향도</th>
                            <th>영향받는<br>이해관계자</th>
                            <th>산출지표</th>
                            <th>환경·사회<br>영향 평가</th>
                            <th>영향 측정 지표</th>
                        </tr>
                    </thead>
                    <tbody>
                        {impact_table_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <main id="impact-details">
            {impact_sections_html}
        </main>

        <!-- II. 재무 중대성 섹션 -->
        <div class="section-header financial" id="financial-section">
            <h2>II. 재무 중대성 (Financial Materiality)</h2>
            <p>외부 환경이 기업의 재무적 성과와 사업 운영에 미치는 영향 관점의 중대 이슈</p>
        </div>

        <div class="analysis-section financial" id="financial-analysis">
            <h3>핵심 이슈 분석</h3>
            <div class="analysis-table-container">
                <table class="analysis-table financial">
                    <thead>
                        <tr>
                            <th>중요주제</th>
                            <th>영향받는<br>영역</th>
                            <th>위험<br>영향도</th>
                            <th>위험 영향<br>기간</th>
                            <th>기회<br>영향도</th>
                            <th>기회 영향<br>기간</th>
                            <th>중장기 목표</th>
                            <th>KPI</th>
                        </tr>
                    </thead>
                    <tbody>
                        {financial_table_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <main id="financial-details">
            {financial_sections_html}
        </main>

        <section class="conclusion">
            <h3>결론 및 향후 방향</h3>
            <p>
                본 보고서는 {company_context.company_name}의 {company_context.year}년 이중 중대성 평가 결과를 바탕으로
                영향 중대성 상위 5개 이슈와 재무 중대성 상위 5개 이슈에 대한 분석을 제시하였습니다.
            </p>
            <p>
                <strong>영향 중대성 핵심 이슈:</strong> {', '.join(impact_names)} 등
            </p>
            <p>
                <strong>재무 중대성 핵심 이슈:</strong> {', '.join(financial_names)} 등
            </p>
            <p>
                당사는 지속적인 이해관계자 소통과 성과 모니터링을 통해 ESG 경영을 고도화하고,
                지속가능한 기업 가치 창출을 위해 노력하겠습니다.
            </p>
        </section>
    </div>
</body>
</html>"""

    async def modify_report(
        self, request: ReportModifyRequest
    ) -> ReportModifyResponse:
        """
        자연어 명령으로 보고서 수정

        Args:
            request: 수정 요청 (현재 보고서 + 수정 지시)

        Returns:
            ReportModifyResponse
        """
        try:
            logger.info(
                f"Modifying report with instruction: {request.instruction[:50]}..."
            )

            openai_client = get_openai_client()

            modified_markdown = await openai_client.modify_report(
                current_report=request.current_report,
                instruction=request.instruction,
            )

            modified_html = self._markdown_to_html(modified_markdown)

            logger.info("Report modification completed successfully")

            return ReportModifyResponse(
                success=True,
                modified_report=modified_markdown,
                modified_html=modified_html,
                message="보고서가 성공적으로 수정되었습니다.",
            )

        except Exception as e:
            logger.error(f"Failed to modify report: {str(e)}", exc_info=True)
            return ReportModifyResponse(
                success=False,
                message=f"보고서 수정 실패: {str(e)}",
                error=ErrorInfo(
                    code="ESG-AI-RPT-002",
                    message="보고서 수정 실패",
                    details=str(e),
                ),
            )

    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        간단한 Markdown to HTML 변환

        실제 프로덕션에서는 marked.js나 python-markdown 사용 권장
        """
        import re

        html = markdown_text

        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'

        return html


# 서비스 인스턴스 생성을 위한 팩토리 함수
def get_report_assistant_service() -> ReportAssistantService:
    """Get or create ReportAssistantService instance"""
    return ReportAssistantService()
