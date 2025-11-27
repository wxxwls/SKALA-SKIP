"""Prompt templates for ESG report generation."""

REPORT_SECTION_SYSTEM_PROMPT = """You are an expert ESG report writer.
Your task is to generate professional, well-structured content for ESG reports.
The content should be factual, balanced, and follow industry best practices."""

REPORT_SECTION_USER_PROMPT = """Generate content for the "{section_type}" section of an ESG report.

Company context:
{context}

Requirements:
- Maximum length: {max_length} characters
- Professional tone
- Include specific metrics and data where relevant
- Follow GRI/SASB reporting guidelines

Generate the section content:"""

REPORT_EXECUTIVE_SUMMARY_PROMPT = """Create an executive summary for the ESG report.

Key highlights to include:
{highlights}

The summary should be concise (2-3 paragraphs) and highlight the most important achievements and goals."""
