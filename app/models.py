from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class Action(BaseModel):
    action_type: str
    message: Optional[str] = ""
    category: Optional[str] = None
    priority: Optional[str] = None
    resolution: Optional[str] = None
    escalation_team: Optional[str] = None

class Observation(BaseModel):
    task_id: str
    difficulty: str
    customer_message: str
    current_status: str
    known_facts: Dict[str, Any]
    missing_fields: List[str]
    action_history: List[Dict[str, Any]]
    remaining_steps: int
    done: bool

class RewardModel(BaseModel):
    value: float
    reason: str
    progress: Dict[str, float]

class TaskMetadata(BaseModel):
    task_id: str
    difficulty: str
    title: str
    objective: str

class TicketState(BaseModel):
    task_id: str
    difficulty: str
    title: str
    objective: str
    customer_message: str
    true_category: str
    true_priority: str
    expected_resolution: Optional[str] = None
    expected_escalation_team: Optional[str] = None
    required_info_request: bool = False
    required_missing_fields: List[str] = Field(default_factory=list)
    unsafe_to_close_early: bool = False
    max_steps: int = 6

    classified_category: Optional[str] = None
    assigned_priority: Optional[str] = None
    asked_info_fields: List[str] = Field(default_factory=list)
    resolution_given: Optional[str] = None
    escalated_to: Optional[str] = None
    closed: bool = False
    done: bool = False
    step_count: int = 0
    history: List[Dict[str, Any]] = Field(default_factory=list)

class GraderResult(BaseModel):
    task_id: str
    score: float
    details: Dict[str, float]