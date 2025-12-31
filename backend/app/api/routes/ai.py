"""
AI / Claude API Routes
======================
Smart AI features using Anthropic Claude for:
- Transcript summarization
- Sentiment analysis
- Lead scoring
- Script generation
- Entity extraction
"""

from typing import Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.claude import claude, CallSummary, LeadScore, ScriptSuggestion
from app.core.logging import logger

router = APIRouter(prefix="/api/ai", tags=["ai"])


# =============================================================================
# Request/Response Models
# =============================================================================

class SummarizeRequest(BaseModel):
    """Request to summarize a transcript."""
    transcript: str
    context: Optional[dict] = None


class SentimentRequest(BaseModel):
    """Request to analyze sentiment."""
    text: str


class LeadScoreRequest(BaseModel):
    """Request to score a lead."""
    lead_data: dict[str, Any]
    call_history: Optional[list[dict]] = None


class ScriptRequest(BaseModel):
    """Request to generate a script."""
    purpose: str
    customer_context: Optional[dict] = None
    tone: str = "professional"


class ResponseSuggestionRequest(BaseModel):
    """Request for a response suggestion."""
    customer_message: str
    context: Optional[str] = None


class EntityExtractionRequest(BaseModel):
    """Request to extract entities."""
    text: str


class QuickSummaryRequest(BaseModel):
    """Request for a quick summary."""
    text: str
    max_length: int = 100


class ClassifyOutcomeRequest(BaseModel):
    """Request to classify call outcome."""
    transcript: str


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/summarize", response_model=CallSummary)
async def summarize_transcript(req: SummarizeRequest):
    """
    Summarize a call transcript with key insights.
    
    Returns:
    - Brief 1-2 sentence summary
    - Key points as bullet points
    - Customer sentiment (positive/neutral/negative)
    - Action items for follow-up
    - Call outcome classification
    - Confidence score
    """
    try:
        summary = claude.summarize_transcript(
            transcript=req.transcript,
            context=req.context,
        )
        return summary
    except Exception as e:
        logger.error(f"Failed to summarize transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment")
async def analyze_sentiment(req: SentimentRequest):
    """
    Analyze sentiment and emotions in text.
    
    Returns:
    - Sentiment (positive/neutral/negative)
    - Confidence score
    - Detected emotions
    - Urgency level
    """
    try:
        result = claude.analyze_sentiment(req.text)
        return {"success": True, **result}
    except Exception as e:
        logger.error(f"Failed to analyze sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/score-lead", response_model=LeadScore)
async def score_lead(req: LeadScoreRequest):
    """
    Score a lead based on available data.
    
    Returns:
    - Score (1-100)
    - Reasoning for the score
    - Priority level (high/medium/low)
    - Best time to call suggestion
    - Suggested approach
    """
    try:
        score = claude.score_lead(
            lead_data=req.lead_data,
            call_history=req.call_history,
        )
        return score
    except Exception as e:
        logger.error(f"Failed to score lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-script", response_model=ScriptSuggestion)
async def generate_script(req: ScriptRequest):
    """
    Generate a personalized call script.
    
    Args:
    - purpose: What the call is for (e.g., "pickup_notification", "follow_up")
    - customer_context: Customer info for personalization
    - tone: Desired tone (professional, friendly, urgent)
    
    Returns:
    - Opening statement
    - Key talking points
    - Objection handlers
    - Closing statement
    - Tone recommendation
    """
    try:
        script = claude.generate_script(
            purpose=req.purpose,
            customer_context=req.customer_context,
            tone=req.tone,
        )
        return script
    except Exception as e:
        logger.error(f"Failed to generate script: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-response")
async def suggest_response(req: ResponseSuggestionRequest):
    """
    Suggest a response to a customer message or objection.
    
    Returns a concise, professional response suggestion.
    """
    try:
        response = claude.suggest_response(
            customer_message=req.customer_message,
            context=req.context,
        )
        return {"success": True, "suggested_response": response}
    except Exception as e:
        logger.error(f"Failed to suggest response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-entities")
async def extract_entities(req: EntityExtractionRequest):
    """
    Extract named entities from text.
    
    Returns:
    - Names (person names)
    - Dates (dates and times)
    - Vehicles (makes/models)
    - Phone numbers
    - Amounts (monetary values)
    """
    try:
        entities = claude.extract_entities(req.text)
        return {"success": True, "entities": entities}
    except Exception as e:
        logger.error(f"Failed to extract entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-summary")
async def quick_summary(req: QuickSummaryRequest):
    """
    Create a very brief summary of text.
    
    Useful for generating short descriptions or previews.
    """
    try:
        summary = claude.quick_summary(
            text=req.text,
            max_length=req.max_length,
        )
        return {"success": True, "summary": summary}
    except Exception as e:
        logger.error(f"Failed to create summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-outcome")
async def classify_outcome(req: ClassifyOutcomeRequest):
    """
    Classify the outcome of a call from its transcript.
    
    Returns one of:
    - booked
    - callback
    - voicemail
    - not_interested
    - wrong_number
    - busy
    - no_answer
    - transferred
    - unknown
    """
    try:
        outcome = claude.classify_call_outcome(req.transcript)
        return {"success": True, "outcome": outcome}
    except Exception as e:
        logger.error(f"Failed to classify outcome: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Batch Operations
# =============================================================================

@router.post("/batch/summarize")
async def batch_summarize(transcripts: list[SummarizeRequest]):
    """Summarize multiple transcripts at once."""
    results = []
    for req in transcripts:
        try:
            summary = claude.summarize_transcript(
                transcript=req.transcript,
                context=req.context,
            )
            results.append({"success": True, "summary": summary.model_dump()})
        except Exception as e:
            results.append({"success": False, "error": str(e)})
    return {"results": results}


@router.post("/batch/score-leads")
async def batch_score_leads(leads: list[LeadScoreRequest]):
    """Score multiple leads at once."""
    results = []
    for req in leads:
        try:
            score = claude.score_lead(
                lead_data=req.lead_data,
                call_history=req.call_history,
            )
            results.append({"success": True, "score": score.model_dump()})
        except Exception as e:
            results.append({"success": False, "error": str(e)})
    return {"results": results}


# =============================================================================
# Health Check
# =============================================================================

@router.get("/health")
async def ai_health():
    """Check if AI service is available."""
    try:
        # Try a simple operation
        result = claude.analyze_sentiment("test")
        return {
            "status": "healthy",
            "service": "anthropic-claude",
            "mock_mode": result.get("confidence", 0) == 0.85,  # Mock returns 0.85
        }
    except Exception as e:
        return {
            "status": "degraded",
            "service": "anthropic-claude",
            "error": str(e),
        }
