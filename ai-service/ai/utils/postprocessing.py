"""Output postprocessing utilities."""
from typing import List, Dict, Any
import json


def format_llm_output(output: str) -> str:
    """Format LLM output for presentation."""
    return output.strip()


def parse_json_output(output: str) -> Dict[str, Any]:
    """Parse JSON from LLM output."""
    try:
        json_match = output
        if "```json" in output:
            json_match = output.split("```json")[1].split("```")[0]
        elif "```" in output:
            json_match = output.split("```")[1].split("```")[0]
        return json.loads(json_match.strip())
    except (json.JSONDecodeError, IndexError):
        return {}


def deduplicate_results(results: List[Dict], key: str) -> List[Dict]:
    """Remove duplicate results based on key."""
    seen = set()
    unique = []
    for item in results:
        if item.get(key) not in seen:
            seen.add(item.get(key))
            unique.append(item)
    return unique
