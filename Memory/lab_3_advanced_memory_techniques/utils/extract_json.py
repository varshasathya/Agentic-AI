"""Utility function to extract JSON from LLM responses."""
import re
import json


def extract_json_from_response(content: str) -> str:
    """Extract JSON from LLM response, handling markdown code blocks and nested objects."""
    # Try to extract JSON from markdown code blocks first
    code_block_match = re.search(r'```(?:json)?', content, re.IGNORECASE)
    if code_block_match:
        # Find the start of JSON after ```
        json_start = content.find('{', code_block_match.end())
        if json_start == -1:
            json_start = content.find('[', code_block_match.end())
        if json_start != -1:
            # Use brace counting to find the end
            json_str = _extract_complete_json(content, json_start)
            if json_str:
                return json_str.strip()
    
    # If no code block, find JSON object/array using brace counting
    json_start = content.find('{')
    if json_start == -1:
        json_start = content.find('[')
    
    if json_start != -1:
        json_str = _extract_complete_json(content, json_start)
        if json_str:
            return json_str.strip()
    
    # Fallback: return content as-is
    return content.strip()


def _extract_complete_json(content: str, start_idx: int) -> str:
    """Extract complete JSON object/array using brace/bracket counting."""
    brace_count = 0
    bracket_count = 0
    in_string = False
    escape_next = False
    
    for i in range(start_idx, len(content)):
        char = content[i]
        if escape_next:
            escape_next = False
            continue
        if char == '\\':
            escape_next = True
            continue
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and bracket_count == 0:
                    return content[start_idx:i+1]
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if brace_count == 0 and bracket_count == 0:
                    return content[start_idx:i+1]
    
    return None
