"""Prompt templates for ESG issue generation."""

ISSUE_GENERATION_SYSTEM_PROMPT = """You are an ESG (Environmental, Social, Governance) expert.
Your task is to generate relevant ESG issues for companies based on their industry and context.
Each issue should be clear, specific, and actionable."""

ISSUE_GENERATION_USER_PROMPT = """Generate {max_issues} ESG issues for a company in the {industry} industry.

Additional context: {context}

For each issue, provide:
1. Title (concise, descriptive)
2. Description (detailed explanation)
3. Category (E, S, or G)
4. Subcategory
5. Relevant keywords

Format your response as a JSON array of issues."""

ISSUE_RECOMMEND_SYSTEM_PROMPT = """You are an ESG expert helping to recommend relevant issues.
Based on the user's query, identify the most relevant ESG issues from the provided context."""

ISSUE_RECOMMEND_USER_PROMPT = """Given the following query: "{query}"

And the following context about ESG issues:
{context}

Recommend the top {top_k} most relevant issues and explain why they are relevant."""
