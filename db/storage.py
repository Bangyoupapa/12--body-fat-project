import os
from typing import Optional

from services.nutrition import FoodEstimate
from services.exercise import ExerciseEntry
from services.body_composition import InBodyResult, CompositionEntry


def _default_client():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def save_food_entry(estimate: FoodEstimate, client=None) -> None:
    if client is None:
        client = _default_client()
    client.table("food_entries").insert({
        "description": estimate.description,
        "calories": estimate.calories,
        "protein_g": estimate.protein_g,
        "carbs_g": estimate.carbs_g,
        "fat_g": estimate.fat_g,
        "is_estimate": estimate.is_estimate,
    }).execute()


def save_exercise_entry(entry: ExerciseEntry, client=None) -> None:
    if client is None:
        client = _default_client()
    result = client.table("exercise_entries").insert({
        "raw_text": entry.raw_text,
    }).execute()
    entry_id = result.data[0]["id"]
    rows = [
        {
            "entry_id": entry_id,
            "name": ex.name,
            "sets": ex.sets,
            "reps": ex.reps,
            "weight_kg": ex.weight_kg,
        }
        for ex in entry.exercises
    ]
    if rows:
        client.table("exercises").insert(rows).execute()


def save_inbody_entry(result: InBodyResult, client=None) -> None:
    if client is None:
        client = _default_client()
    client.table("composition_entries").insert({
        "weight_kg": result.weight_kg,
        "bmi": result.bmi,
        "body_fat_pct": result.body_fat_pct,
        "muscle_mass_kg": result.muscle_mass_kg,
        "source": "inbody",
    }).execute()


def save_weight_entry(entry: CompositionEntry, client=None) -> None:
    if client is None:
        client = _default_client()
    client.table("composition_entries").insert({
        "weight_kg": entry.weight_kg,
        "height_cm": entry.height_cm,
        "bmi": entry.bmi,
        "source": "manual",
    }).execute()


def save_health_metrics(steps: Optional[int], sleep_hours: Optional[float], client=None) -> None:
    if client is None:
        client = _default_client()
    client.table("health_metrics").insert({
        "steps": steps,
        "sleep_hours": sleep_hours,
    }).execute()
