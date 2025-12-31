"""
Anthropic Claude AI Integration Service
=======================================
Smart AI features using Claude for:
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

from app.core.config import settings
from app.core.logging import logger

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic package not installed. AI features will be limited.")


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


class ClaudeService:
    """
    Claude AI service for intelligent call center features.
    
    Features:
    - Summarize call transcripts
    - Analyze customer sentiment
    - Score and prioritize leads
    - Generate personalized scripts
    - Suggest responses for objections
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        """Get or create Anthropic client."""
        if self._client is None:
            if not ANTHROPIC_AVAILABLE:
                return None
            
            api_key = settings.anthropic_api_key
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not set - AI features disabled")
                return None
            
            self._client = anthropic.Anthropic(api_key=api_key)
        
        return self._client

    def _call_claude(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> Optional[str]:
        """Make a call to Claude API."""
        client = self._get_client()
        
        if not client:
            if settings.mock_mode:
                return '{"mock": true}'
            return None
        
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return None

    def summarize_transcript(
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
        
        system_prompt = """You are an expert call analyst for an automotive service center. 
Analyze call transcripts and provide structured summaries.

IMPORTANT: Respond with ONLY valid JSON matching this exact structure:
{
    "brief": "1-2 sentence summary",
    "key_points": ["point 1", "point 2"],
    "customer_sentiment": "positive|neutral|negative",
    "action_items": ["action 1", "action 2"],
    "outcome": "booked|callback|voicemail|not_interested|wrong_number|busy|no_answer",
    "confidence_score": 0.85
}"""

        context_str = ""
        if context:
            context_str = f"\n\nContext: {json.dumps(context)}"
        
        user_message = f"Analyze this call transcript and provide a summary:{context_str}\n\nTranscript:\n{transcript}"
        
        response = self._call_claude(system_prompt, user_message)
        
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
            data = json.loads(response)
            return CallSummary(**data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse Claude response: {e}")
            return CallSummary(
                brief=response[:200] if response else "Analysis failed",
                key_points=[],
                customer_sentiment="neutral",
                action_items=[],
                outcome="unknown",
                confidence_score=0.0,
            )

    def analyze_sentiment(self, text: str) -> dict[str, Any]:
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
                "urgency": "low",
            }
        
        system_prompt = """Analyze the sentiment and emotions in this text.
Respond with ONLY valid JSON:
{
    "sentiment": "positive|neutral|negative",
    "confidence": 0.0-1.0,
    "emotions": ["emotion1", "emotion2"],
    "urgency": "high|medium|low"
}"""
        
        response = self._call_claude(system_prompt, text, max_tokens=256)
        
        if not response:
            return {"sentiment": "neutral", "confidence": 0.0, "emotions": [], "urgency": "low"}
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"sentiment": "neutral", "confidence": 0.0, "emotions": [], "urgency": "low"}

    def score_lead(
        self,
        lead_data: dict[str, Any],
        call_history: Optional[list[dict]] = None,
    ) -> LeadScore:
        """
        Score a lead based on available data.
        
        Args:
            lead_data: Lead information (name, vehicle, etc.)
            call_history: Previous call attempts and outcomes
        """
        if settings.mock_mode:
            return LeadScore(
                score=75,
                reasoning="Customer has recent service history and showed interest in follow-up calls.",
                priority="high",
                best_time_to_call="Morning (9-11 AM)",
                suggested_approach="Mention completed service and offer convenient pickup times.",
            )
        
        system_prompt = """You are a lead scoring expert for an automotive service center.
Analyze lead data and provide a score with reasoning.

Respond with ONLY valid JSON:
{
    "score": 1-100,
    "reasoning": "explanation",
    "priority": "high|medium|low",
    "best_time_to_call": "suggested time or null",
    "suggested_approach": "recommended approach"
}"""
        
        user_message = f"Score this lead:\n{json.dumps(lead_data, indent=2)}"
        if call_history:
            user_message += f"\n\nCall History:\n{json.dumps(call_history, indent=2)}"
        
        response = self._call_claude(system_prompt, user_message)
        
        if not response:
            return LeadScore(
                score=50,
                reasoning="Unable to analyze lead",
                priority="medium",
                suggested_approach="Standard outreach",
            )
        
        try:
            data = json.loads(response)
            return LeadScore(**data)
        except (json.JSONDecodeError, ValueError):
            return LeadScore(
                score=50,
                reasoning="Analysis failed",
                priority="medium",
                suggested_approach="Standard outreach",
            )

    def generate_script(
        self,
        purpose: str,
        customer_context: Optional[dict] = None,
        tone: str = "professional",
    ) -> ScriptSuggestion:
        """
        Generate a personalized call script.
        
        Args:
            purpose: What the call is for (pickup_notification, follow_up, etc.)
            customer_context: Customer information for personalization
            tone: Desired tone (professional, friendly, urgent)
        """
        if settings.mock_mode:
            return ScriptSuggestion(
                opening="Good morning! This is [Name] from [Company]. I'm calling with great news about your vehicle.",
                key_talking_points=[
                    "Inform about completed service",
                    "Discuss any additional findings",
                    "Offer convenient pickup times",
                ],
                objection_handlers={
                    "busy": "I completely understand. When would be a better time to discuss this?",
                    "cost_concern": "I'd be happy to go over the details. Would you like me to email you a breakdown?",
                },
                closing="Thank you for your time. We look forward to seeing you!",
                tone_recommendation="Warm and professional, focus on convenience",
            )
        
        system_prompt = f"""You are an expert call script writer for automotive service centers.
Create a {tone} script for: {purpose}

Respond with ONLY valid JSON:
{{
    "opening": "greeting text",
    "key_talking_points": ["point 1", "point 2", "point 3"],
    "objection_handlers": {{"objection": "response"}},
    "closing": "closing text",
    "tone_recommendation": "guidance for delivery"
}}"""
        
        user_message = "Generate a call script"
        if customer_context:
            user_message += f" for this customer:\n{json.dumps(customer_context, indent=2)}"
        
        response = self._call_claude(system_prompt, user_message, max_tokens=1500)
        
        if not response:
            return ScriptSuggestion(
                opening="Hello, this is [Name] from [Company].",
                key_talking_points=["Introduce purpose", "Address needs", "Offer solution"],
                objection_handlers={},
                closing="Thank you for your time.",
                tone_recommendation="Professional",
            )
        
        try:
            data = json.loads(response)
            return ScriptSuggestion(**data)
        except (json.JSONDecodeError, ValueError):
            return ScriptSuggestion(
                opening="Hello, this is [Name] from [Company].",
                key_talking_points=["Introduce purpose"],
                objection_handlers={},
                closing="Thank you.",
                tone_recommendation="Professional",
            )

    def suggest_response(
        self,
        customer_message: str,
        context: Optional[str] = None,
    ) -> str:
        """
        Suggest a response to a customer message/objection.
        
        Args:
            customer_message: What the customer said
            context: Additional context about the conversation
        """
        if settings.mock_mode:
            return "I completely understand your concern. Let me see what options we have available to address that for you."
        
        system_prompt = """You are a helpful customer service AI for an automotive service center.
Suggest a professional, empathetic response to the customer's message.
Keep it concise (2-3 sentences max) and actionable."""
        
        user_message = f"Customer said: \"{customer_message}\""
        if context:
            user_message += f"\n\nContext: {context}"
        
        response = self._call_claude(system_prompt, user_message, max_tokens=200, temperature=0.5)
        
        return response or "I understand. Let me help you with that."

    def extract_entities(self, text: str) -> dict[str, list[str]]:
        """
        Extract named entities from text (names, dates, vehicles, etc.).
        
        Args:
            text: Text to analyze
        
        Returns:
            Dict of entity_type -> list of extracted values
        """
        if settings.mock_mode or not text:
            return {
                "names": ["John Smith"],
                "dates": ["tomorrow", "10 AM"],
                "vehicles": ["Toyota Camry"],
                "phone_numbers": [],
                "amounts": [],
            }
        
        system_prompt = """Extract named entities from the text.
Respond with ONLY valid JSON:
{
    "names": ["person names"],
    "dates": ["dates and times mentioned"],
    "vehicles": ["vehicle models/makes"],
    "phone_numbers": ["phone numbers"],
    "amounts": ["monetary amounts"]
}"""
        
        response = self._call_claude(system_prompt, text, max_tokens=512)
        
        if not response:
            return {"names": [], "dates": [], "vehicles": [], "phone_numbers": [], "amounts": []}
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"names": [], "dates": [], "vehicles": [], "phone_numbers": [], "amounts": []}

    def quick_summary(self, text: str, max_length: int = 100) -> str:
        """
        Create a very brief summary of text.
        
        Args:
            text: Text to summarize
            max_length: Maximum characters in summary
        """
        if settings.mock_mode or not text:
            return text[:max_length] if text else ""
        
        if len(text) <= max_length:
            return text
        
        system_prompt = f"Summarize this text in {max_length} characters or less. Be concise and capture the key point."
        
        response = self._call_claude(system_prompt, text, max_tokens=100, temperature=0.2)
        
        return response[:max_length] if response else text[:max_length]

    def classify_call_outcome(self, transcript: str) -> str:
        """
        Classify the outcome of a call from its transcript.
        
        Returns one of: booked, callback, voicemail, not_interested, 
        wrong_number, busy, no_answer, transferred, unknown
        """
        if settings.mock_mode or not transcript:
            return "unknown"
        
        system_prompt = """Classify the outcome of this call transcript.
Respond with ONLY one of these exact words:
booked, callback, voicemail, not_interested, wrong_number, busy, no_answer, transferred, unknown"""
        
        response = self._call_claude(system_prompt, transcript, max_tokens=20, temperature=0.1)
        
        valid_outcomes = ["booked", "callback", "voicemail", "not_interested", 
                        "wrong_number", "busy", "no_answer", "transferred", "unknown"]
        
        if response:
            outcome = response.strip().lower()
            if outcome in valid_outcomes:
                return outcome
        
        return "unknown"


# Singleton instance
claude = ClaudeService()
