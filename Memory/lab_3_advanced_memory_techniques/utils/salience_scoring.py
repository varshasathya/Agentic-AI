"""Salience scoring for memory writes."""
import json
from typing import Dict, Optional
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from utils.extract_json import extract_json_from_response


class SalienceScorer:
    """Compute importance, novelty, contradiction, and risk scores for memory writes."""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def compute_salience(self, conversation: str, tool_result: Optional[Dict] = None) -> Dict[str, float]:
        """Compute salience scores for the conversation."""
        # Format tool_result outside the prompt
        tool_result_text = json.dumps(tool_result, indent=2) if tool_result else 'None'
        
        prompt = f"""
        Analyze this conversation and compute salience scores (0.0-1.0) for:
        1. importance: How critical is this information? (ticket creation, escalation, resolution = high)
        2. novelty: Is this new information not already stored? (contradictions, corrections = high)
        3. contradiction: Does this contradict existing memories? (user corrections = high)
        4. risk: Could storing this cause harm? (PII, sensitive data = high risk, low score)

        Conversation:
        {conversation}

        Tool Result:
        {tool_result_text}

        Return JSON:
        {{"importance": 0.0-1.0, "novelty": 0.0-1.0, "contradiction": 0.0-1.0, "risk": 0.0-1.0}}
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        content = extract_json_from_response(response.content)
        
        try:
            scores = json.loads(content)
            return {
                "importance": float(scores.get("importance", 0.0)),
                "novelty": float(scores.get("novelty", 0.0)),
                "contradiction": float(scores.get("contradiction", 0.0)),
                "risk": float(scores.get("risk", 0.0))
            }
        except:
            return {"importance": 0.5, "novelty": 0.5, "contradiction": 0.0, "risk": 0.0}
    
    def should_write(self, scores: Dict[str, float], threshold: float = 0.6, explicit_trigger: bool = False) -> bool:
        """Determine if memory should be written."""
        if explicit_trigger:
            return True
        
        # Weighted combined score
        combined = (
            0.4 * scores["importance"] +
            0.3 * scores["novelty"] +
            0.2 * scores["contradiction"] -
            0.1 * scores["risk"]  # Risk reduces score
        )
        
        return combined >= threshold
