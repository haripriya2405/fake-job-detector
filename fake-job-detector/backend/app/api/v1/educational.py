"""Educational API Endpoints: 25 Job Scam Red Flags Matrix & Interactive Scam Simulator."""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from app.services.educational_service import EducationalService, RED_FLAGS_25

router = APIRouter(prefix="/educational", tags=["Educational & Scam Simulator"])


class EvaluationRequest(BaseModel):
    scenario_id: str
    user_choice_is_scam: bool
    user_flagged_clues: Optional[List[str]] = Field(default_factory=list)


class EvaluationResponse(BaseModel):
    scenario_id: str
    is_correct: bool
    actual_verdict: str
    actual_is_scam: bool
    red_flags: List[str]
    clue_phrases: List[str]
    forensic_explanation: str
    matched_clues: List[str]
    base_xp: int
    bonus_xp: int
    total_xp: int


@router.get("/red-flags")
def get_red_flags(
    category: Optional[str] = Query(None, description="Category filter (e.g., Financial, Communication, Interview)"),
    search: Optional[str] = Query(None, description="Free text keyword search"),
    severity: Optional[str] = Query(None, description="Severity filter: CRITICAL, HIGH, MEDIUM")
):
    """Retrieve curated list of the 25 Job Scam Red Flags with threat severity and safety protocols."""
    items = EducationalService.get_red_flags(category=category, search=search, severity=severity)
    return {
        "total_red_flags": len(RED_FLAGS_25),
        "count": len(items),
        "red_flags": items
    }


@router.get("/simulator/scenarios")
def get_simulator_scenarios(
    difficulty: Optional[str] = Query(None, description="Filter by difficulty: Beginner, Intermediate, Advanced")
):
    """Retrieve training scenarios for the Interactive Scam Hunter Simulator."""
    scenarios = EducationalService.get_simulator_scenarios(difficulty=difficulty)
    return {
        "count": len(scenarios),
        "scenarios": scenarios
    }


@router.post("/simulator/evaluate", response_model=EvaluationResponse)
def evaluate_scenario_attempt(payload: EvaluationRequest):
    """Evaluate a user's guess and clue highlights on a simulator scenario."""
    result = EducationalService.evaluate_scenario(
        scenario_id=payload.scenario_id,
        user_choice_is_scam=payload.user_choice_is_scam,
        user_flagged_clues=payload.user_flagged_clues
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
