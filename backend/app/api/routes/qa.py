"""QA and Review API endpoints."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/qa", tags=["qa"])


class CallScores(BaseModel):
    greeting: int = Field(..., ge=0, le=100)
    clarity: int = Field(..., ge=0, le=100)
    persuasion: int = Field(..., ge=0, le=100)
    objectionHandling: int = Field(..., ge=0, le=100)
    closing: int = Field(..., ge=0, le=100)


class SubmitReviewRequest(BaseModel):
    scores: CallScores
    feedback: Optional[str] = None
    flagged: bool = False


qa_calls_db = {}
qa_counter = 1


@router.get("/calls")
async def list_calls_for_review(
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
):
    """List calls that need review."""
    calls = list(qa_calls_db.values())
    
    if status == "pending":
        calls = [c for c in calls if not c["reviewed"]]
    elif status == "reviewed":
        calls = [c for c in calls if c["reviewed"]]
    elif status == "flagged":
        calls = [c for c in calls if c["flagged"]]
    
    calls = calls[:limit]
    
    return {"calls": calls, "count": len(calls)}


@router.get("/calls/{call_id}")
async def get_call_for_review(call_id: str):
    """Get call details for review."""
    call = qa_calls_db.get(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call


@router.post("/calls/{call_id}/review")
async def submit_review(call_id: str, req: SubmitReviewRequest):
    """Submit a review for a call."""
    call = qa_calls_db.get(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    overall_score = int(sum([
        req.scores.greeting,
        req.scores.clarity,
        req.scores.persuasion,
        req.scores.objectionHandling,
        req.scores.closing,
    ]) / 5)
    
    call["reviewed"] = True
    call["scores"] = {
        **req.scores.model_dump(),
        "overall": overall_score,
    }
    call["feedback"] = req.feedback
    call["flagged"] = req.flagged
    call["reviewed_at"] = datetime.now().isoformat()
    
    qa_calls_db[call_id] = call
    
    return {
        "id": call_id,
        "reviewed": True,
        "scores": call["scores"],
        "feedback": req.feedback,
        "flagged": req.flagged,
        "message": "Review submitted successfully",
    }


@router.post("/calls/{call_id}/flag")
async def flag_call(call_id: str):
    """Flag a call for attention."""
    call = qa_calls_db.get(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    call["flagged"] = True
    qa_calls_db[call_id] = call
    
    return {"id": call_id, "flagged": True, "message": "Call flagged successfully"}


@router.post("/calls/{call_id}/unflag")
async def unflag_call(call_id: str):
    """Remove flag from a call."""
    call = qa_calls_db.get(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    call["flagged"] = False
    qa_calls_db[call_id] = call
    
    return {"id": call_id, "flagged": False, "message": "Flag removed successfully"}


@router.get("/stats/summary")
async def get_qa_stats():
    """Get QA statistics."""
    calls = list(qa_calls_db.values())
    
    pending = sum(1 for c in calls if not c["reviewed"])
    reviewed = sum(1 for c in calls if c["reviewed"])
    flagged = sum(1 for c in calls if c["flagged"])
    
    scores = [c["scores"]["overall"] for c in calls if c.get("scores")]
    avg_score = int(sum(scores) / len(scores)) if scores else 0
    
    score_distribution = {
        "excellent": sum(1 for s in scores if s >= 90),
        "good": sum(1 for s in scores if 70 <= s < 90),
        "fair": sum(1 for s in scores if 50 <= s < 70),
        "poor": sum(1 for s in scores if s < 50),
    }
    
    return {
        "pendingReview": pending,
        "reviewed": reviewed,
        "flagged": flagged,
        "avgScore": avg_score,
        "totalCalls": len(calls),
        "scoreDistribution": score_distribution,
    }


@router.get("/trends")
async def get_qa_trends():
    """Get QA score trends over time."""
    return {
        "daily": [
            {"date": "2024-01-20", "avgScore": 82},
            {"date": "2024-01-21", "avgScore": 85},
            {"date": "2024-01-22", "avgScore": 83},
            {"date": "2024-01-23", "avgScore": 86},
            {"date": "2024-01-24", "avgScore": 84},
        ],
        "byCampaign": [
            {"campaign": "Service Reminder Q1", "avgScore": 85, "totalReviewed": 67},
            {"campaign": "Appointment Confirmation", "avgScore": 88, "totalReviewed": 45},
            {"campaign": "Follow-Up Calls", "avgScore": 82, "totalReviewed": 30},
        ],
    }
