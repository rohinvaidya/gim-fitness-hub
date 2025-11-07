from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic import field_validator

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

class Exercise(BaseModel):
    name: str
    sets: int = Field(ge=1, le=6)
    reps: str  # "5", "8-12", "45s"
    # NOTE: Optional so yoga/flows can use None. If provided, must be >=15 (after normalization).
    rest_sec: Optional[int] = Field(default=None, ge=15, le=240)

    @field_validator("rest_sec", mode="before")
    @classmethod
    def normalize_rest(cls, v):
        """
        Convert bad values to safe ones:
        - None/"" -> None
        - non-numeric -> None
        - <=0 -> None (represents 'no explicit rest')
        - clamp into [15, 240] when numeric and >0
        """
        if v is None or v == "":
            return None
        try:
            iv = int(v)
        except Exception:
            return None
        if iv <= 0:
            return None
        if iv < 15:
            return 15
        if iv > 240:
            return 240
        return iv

    @field_validator("sets", mode="before")
    @classmethod
    def normalize_sets(cls, v):
        """Claude may send strings; coerce and clamp to [1,6]."""
        try:
            iv = int(v)
        except Exception:
            iv = 3
        return max(1, min(6, iv))

    @field_validator("reps", mode="before")
    @classmethod
    def reps_to_str(cls, v):
        """Ensure reps is a string (Claude may emit numbers)."""
        return str(v)

class WorkoutDay(BaseModel):
    day: str
    focus: str
    exercises: List[Exercise]

class Meal(BaseModel):
    name: str
    notes: Optional[str] = ""

class DietDay(BaseModel):
    day: str
    meals: List[Meal]

class Plan(BaseModel):
    workout_plan: List[WorkoutDay]
    diet_plan: List[DietDay]
    notes: Optional[str] = ""

def _order_days(items):
    order = {d:i for i,d in enumerate(DAYS)}
    return sorted(items, key=lambda x: order.get(x.day, 99))

def validate_plan_dict(plan_dict: dict) -> dict:
    """
    Validate and normalize the plan:
    - Coerce odd types (via validators)
    - Drop duplicate days (keep first)
    - Order Monday..Sunday
    """
    plan = Plan.model_validate(plan_dict)

    seen = set()
    wdays = []
    for d in plan.workout_plan:
        if d.day not in seen:
            wdays.append(d)
            seen.add(d.day)
    wdays = _order_days(wdays)

    seen = set()
    ddays = []
    for d in plan.diet_plan:
        if d.day not in seen:
            ddays.append(d)
            seen.add(d.day)
    ddays = _order_days(ddays)

    plan_norm = Plan(workout_plan=wdays, diet_plan=ddays, notes=plan.notes)
    return plan_norm.model_dump()
