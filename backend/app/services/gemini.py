"""
Google Gemini AI Integration Service
=====================================
Smart AI features using Gemini for:
- Transcript summarization
- Call analysis and insights
- Lead scoring
- Sentiment analysis
- Script generation
- Response suggestions
"""

from typing import Optional, Any
from pydantic import BaseModel
import json
import httpx

from app.core.config import settings
from app.core.logging import logger

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


class CallSummary(BaseModel):
    """Summary of a call transcript."""
    brief: str  # 1-2 sentence summary
    key_points: list[str]  # Bullet points of important items
    customer_sentiment: str  # positive, neutral, negative
    action_items: list[str]  # Follow-up actions needed
    outcome: str  # booked, callback, voicemail, not_interested, etc.
    confidence_score: float  # 0-1 confidence in the analysis


class LeadScore(BaseModel):
    """AI-generated lead scoring."""
    score: int  # 1-100
    reasoning: str
    priority: str  # high, medium, low
    best_time_to_call: Optional[str] = None
    suggested_approach: str


class ScriptSuggestion(BaseModel):
    """AI-generated script suggestion."""
    opening: str
    key_talking_points: list[str]
    objection_handlers: dict[str, str]
    closing: str
    tone_recommendation: str


class GeminiService:
    """
    Gemini AI service for intelligent call center features.
    
    Features:
    - Summarize call transcripts
    - Analyze customer sentiment
    - Score and prioritize leads
    - Generate personalized scripts
    - Suggest responses for objections
    """

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _call_gemini(
        self,
        prompt: str,
        temperature: float = 0.3,
    ) -> Optional[str]:
        """Make a call to Gemini API via HTTP."""
        api_key = settings.gemini_api_key
        
        if not api_key:
            logger.warning("GEMINI_API_KEY not set - AI features disabled")
            if settings.mock_mode:
                return '{"mock": true}'
            return None
        
        try:
            client = await self._get_client()
            
            url = f"{GEMINI_API_URL}?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 2048,
                }
            }
            
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract text from response
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
            
            logger.error(f"Unexpected Gemini response format: {data}")
            return None
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None

    async def summarize_transcript(
        self,
        transcript: str,
        context: Optional[dict] = None,
    ) -> CallSummary:
        """
        Summarize a call transcript with key insights.
        
        Args:
            transcript: The full call transcript
            context: Optional context (customer info, campaign, etc.)
        """
        if settings.mock_mode or not transcript:
            return CallSummary(
                brief="Customer expressed interest in scheduling a pickup for their vehicle service.",
                key_points=[
                    "Vehicle service completed",
                    "Customer available tomorrow morning",
                    "Prefers 10 AM slot",
                ],
                customer_sentiment="positive",
                action_items=["Confirm appointment", "Send reminder SMS"],
                outcome="booked",
                confidence_score=0.92,
            )
        
        context_str = ""
        if context:
            context_str = f"\n\nContext: {json.dumps(context)}"
        
        prompt = f"""You are an expert call analyst for an automotive service center. 
Analyze call transcripts and provide structured summaries.

IMPORTANT: Respond with ONLY valid JSON matching this exact structure:
{{
    "brief": "1-2 sentence summary",
    "key_points": ["point 1", "point 2"],
    "customer_sentiment": "positive|neutral|negative",
    "action_items": ["action 1", "action 2"],
    "outcome": "booked|callback|voicemail|not_interested|wrong_number|busy|no_answer",
    "confidence_score": 0.85
}}

Analyze this call transcript and provide a summary:{context_str}

Transcript:
{transcript}"""
        
        response = await self._call_gemini(prompt)
        
        if not response:
            return CallSummary(
                brief="Unable to analyze transcript",
                key_points=[],
                customer_sentiment="neutral",
                action_items=[],
                outcome="unknown",
                confidence_score=0.0,
            )
        
        try:
            # Clean up response if it has markdown code blocks
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()
            
            data = json.loads(response_clean)
            return CallSummary(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            return CallSummary(
                brief=response[:200] if response else "Analysis failed",
                key_points=[],
                customer_sentiment="neutral",
                action_items=[],
                outcome="unknown",
                confidence_score=0.0,
            )

    async def analyze_sentiment(self, text: str) -> dict[str, Any]:
        """
        Analyze sentiment of text (transcript, message, notes).
        
        Returns:
            Dict with sentiment, confidence, and emotional indicators
        """
        if settings.mock_mode or not text:
            return {
                "sentiment": "neutral",
                "confidence": 0.85,
                "emotions": ["calm"],
                "urgency": "normal",
            }
        
        prompt = f"""Analyze the sentiment and emotional tone of this text.

IMPORTANT: Respond with ONLY valid JSON:
{{
    "sentiment": "positive|neutral|negative",
    "confidence": 0.85,
    "emotions": ["calm", "interested"],
    "urgency": "low|normal|high"
}}

Text to analyze:
{text}"""
        
        response = await self._call_gemini(prompt, temperature=0.1)
        
        if not response:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotions": [],
                "urgency": "normal",
            }
        
        try:
            # Clean up response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()
            
            return json.loads(response_clean)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse sentiment response: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotions": [],
                "urgency": "normal",
            }

    async def score_lead(
        self,
        customer_data: dict[str, Any],
        call_history: list[dict] = None,
    ) -> LeadScore:
        """
        Score a lead based on customer data and call history.
        
        Args:
            customer_data: Customer information
            call_history: Previous call records
        """
        if settings.mock_mode:
            return LeadScore(
                score=75,
                reasoning="Customer has shown consistent interest and has the means to proceed.",
                priority="high",
                best_time_to_call="10 AM - 12 PM weekdays",
                suggested_approach="Focus on convenience and time-saving benefits",
            )
        
        call_history_str = ""
        if call_history:
            call_history_str = f"\n\nCall History:\n{json.dumps(call_history, indent=2)}"
        
        prompt = f"""You are an expert lead scoring analyst for automotive services.
Score this lead on a scale of 1-100 based on their likelihood to convert.

IMPORTANT: Respond with ONLY valid JSON:
{{
    "score": 75,
    "reasoning": "explain why",
    "priority": "high|medium|low",
    "best_time_to_call": "suggested time window",
    "suggested_approach": "recommended approach"
}}

Customer Data:
{json.dumps(customer_data, indent=2)}{call_history_str}"""
        
        response = await self._call_gemini(prompt, temperature=0.2)
        
        if not response:
            return LeadScore(
                score=50,
                reasoning="Unable to analyze",
                priority="medium",
                best_time_to_call=None,
                suggested_approach="Standard approach",
            )
        
        try:
            # Clean up response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()
            
            data = json.loads(response_clean)
            return LeadScore(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse lead score response: {e}")
            return LeadScore(
                score=50,
                reasoning="Analysis error",
                priority="medium",
                best_time_to_call=None,
                suggested_approach="Standard approach",
            )

    async def generate_script(
        self,
        campaign_type: str,
        customer_profile: dict[str, Any],
        context: Optional[str] = None,
    ) -> ScriptSuggestion:
        """
        Generate a personalized call script.
        
        Args:
            campaign_type: Type of campaign (pickup, appointment, follow-up)
            customer_profile: Customer information
            context: Additional context
        """
        if settings.mock_mode:
            return ScriptSuggestion(
                opening="Hello, this is calling from [Dealership]. Is this [Customer Name]?",
                key_talking_points=[
                    "Your vehicle service was completed",
                    "We offer free pickup and delivery",
                    "Available slots this week",
                ],
                objection_handlers={
                    "too busy": "We can work around your schedule - even after hours pickup",
                    "not interested": "This is a complimentary service - no extra charge",
                },
                closing="Great! I'll confirm your appointment for [time]. You'll receive an SMS reminder.",
                tone_recommendation="friendly, efficient, respectful of their time",
            )
        
        context_str = context if context else ""
        
        prompt = f"""Generate a personalized call script for an automotive service center.

Campaign Type: {campaign_type}
Customer Profile:
{json.dumps(customer_profile, indent=2)}

Additional Context: {context_str}

IMPORTANT: Respond with ONLY valid JSON:
{{
    "opening": "script opening",
    "key_talking_points": ["point 1", "point 2", "point 3"],
    "objection_handlers": {{
        "too busy": "response",
        "not interested": "response",
        "too expensive": "response"
    }},
    "closing": "script closing",
    "tone_recommendation": "tone guidance"
}}"""
        
        response = await self._call_gemini(prompt, temperature=0.7)
        
        if not response:
            return ScriptSuggestion(
                opening="Hello, this is calling from the service center.",
                key_talking_points=["Service update", "Schedule appointment"],
                objection_handlers={},
                closing="Thank you for your time.",
                tone_recommendation="professional and friendly",
            )
        
        try:
            # Clean up response
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            response_clean = response_clean.strip()
            
            data = json.loads(response_clean)
            return ScriptSuggestion(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse script response: {e}")
            return ScriptSuggestion(
                opening="Hello, this is calling from the service center.",
                key_talking_points=["Service update"],
                objection_handlers={},
                closing="Thank you.",
                tone_recommendation="professional",
            )

    async def suggest_response(
        self,
        customer_message: str,
        conversation_context: Optional[list[dict]] = None,
    ) -> str:
        """
        Suggest a response to customer message.
        
        Args:
            customer_message: What the customer said
            conversation_context: Previous conversation turns
        """
        if settings.mock_mode or not customer_message:
            return "I understand. Let me help you with that right away."
        
        context_str = ""
        if conversation_context:
            context_str = "\n\nPrevious conversation:\n"
            for turn in conversation_context:
                role = turn.get("role", "unknown")
                content = turn.get("content", "")
                context_str += f"{role}: {content}\n"
        
        prompt = f"""You are a helpful customer service representative for an automotive service center.
The customer just said: "{customer_message}"

{context_str}

Suggest a brief, professional, and helpful response (1-2 sentences max).
Be friendly, efficient, and solution-oriented."""
        
        response = await self._call_gemini(prompt, temperature=0.7)
        
        if not response:
            return "Thank you for reaching out. How can I assist you today?"
        
        return response.strip()


# Global instance
gemini_service = GeminiService()
