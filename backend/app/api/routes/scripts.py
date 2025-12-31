"""AI Script management API endpoints."""

import re
from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/scripts", tags=["scripts"])


class VoiceSettings(BaseModel):
    voice: str = "Rachel"
    speed: float = Field(1.0, ge=0.5, le=2.0)
    pitch: float = Field(1.0, ge=0.5, le=2.0)


class CreateScriptRequest(BaseModel):
    name: str
    type: str
    prompt: str
    voice_settings: Optional[VoiceSettings] = None
    tags: Optional[List[str]] = None


class UpdateScriptRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    prompt: Optional[str] = None
    voice_settings: Optional[VoiceSettings] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


scripts_db = {}
script_counter = 1


def extract_variables(prompt: str) -> List[str]:
    """Extract variables from prompt in {variable} format."""
    return re.findall(r'\{(\w+)\}', prompt)


@router.get("")
async def list_scripts(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
):
    """List all scripts with optional filtering."""
    scripts = list(scripts_db.values())
    
    if type:
        scripts = [s for s in scripts if s["type"] == type]
    
    if status:
        scripts = [s for s in scripts if s["status"] == status]
    
    scripts = scripts[:limit]
    
    return {
        "scripts": scripts,
        "count": len(scripts),
        "total": len(scripts_db)
    }


@router.post("")
async def create_script(req: CreateScriptRequest):
    """Create a new script."""
    global script_counter
    
    script_id = f"script-{script_counter:04d}"
    script_counter += 1
    
    variables = extract_variables(req.prompt)
    
    script = {
        "id": script_id,
        "name": req.name,
        "type": req.type,
        "prompt": req.prompt,
        "variables": variables,
        "voice_settings": req.voice_settings.model_dump() if req.voice_settings else None,
        "tags": req.tags or [],
        "status": "draft",
        "usage_count": 0,
        "created_at": datetime.now().isoformat(),
    }
    
    scripts_db[script_id] = script
    
    return {
        **script,
        "message": "Script created successfully",
    }


@router.get("/{script_id}")
async def get_script(script_id: str):
    """Get script by ID."""
    script = scripts_db.get(script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@router.put("/{script_id}")
async def update_script(script_id: str, req: UpdateScriptRequest):
    """Update a script."""
    script = scripts_db.get(script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    update_data = req.model_dump(exclude_unset=True)
    
    # Re-extract variables if prompt is updated
    if "prompt" in update_data:
        update_data["variables"] = extract_variables(update_data["prompt"])
    
    # Convert voice_settings if present
    if "voice_settings" in update_data and update_data["voice_settings"]:
        update_data["voice_settings"] = update_data["voice_settings"].model_dump()
    
    for key, value in update_data.items():
        script[key] = value
    
    script["updated_at"] = datetime.now().isoformat()
    scripts_db[script_id] = script
    
    return {
        **script,
        "message": "Script updated successfully",
    }


@router.delete("/{script_id}")
async def delete_script(script_id: str):
    """Delete a script."""
    script = scripts_db.get(script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    del scripts_db[script_id]
    
    return {
        "id": script_id,
        "message": "Script deleted successfully",
    }


@router.post("/{script_id}/test")
async def test_script(script_id: str, test_data: Dict[str, str]):
    """Test a script with sample data."""
    script = scripts_db.get(script_id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    # Replace variables in prompt with test data
    rendered_prompt = script["prompt"]
    for var in script["variables"]:
        if var in test_data:
            rendered_prompt = rendered_prompt.replace(f"{{{var}}}", test_data[var])
    
    return {
        "script_id": script_id,
        "rendered_prompt": rendered_prompt,
        "variables_provided": list(test_data.keys()),
        "variables_required": script["variables"],
    }


@router.get("/stats/summary")
async def get_script_stats():
    """Get script statistics."""
    scripts = list(scripts_db.values())
    
    total = len(scripts)
    active = sum(1 for s in scripts if s["status"] == "active")
    draft = sum(1 for s in scripts if s["status"] == "draft")
    archived = sum(1 for s in scripts if s["status"] == "archived")
    
    total_usage = sum(s["usage_count"] for s in scripts)
    
    return {
        "total": total,
        "active": active,
        "draft": draft,
        "archived": archived,
        "totalUsage": total_usage,
    }
