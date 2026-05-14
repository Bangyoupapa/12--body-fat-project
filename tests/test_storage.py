from unittest.mock import MagicMock, call
from services.nutrition import FoodEstimate
from services.exercise import Exercise, ExerciseEntry
from services.body_composition import InBodyResult, CompositionEntry
from db.storage import save_food_entry, save_exercise_entry, save_inbody_entry, save_weight_entry


def _mock_client(entry_id="abc-123"):
    client = MagicMock()
    execute_result = MagicMock()
    execute_result.data = [{"id": entry_id}]
    client.table.return_value.insert.return_value.execute.return_value = execute_result
    return client


def test_save_food_entry_inserts_correct_columns():
    client = _mock_client()
    estimate = FoodEstimate(
        description="雞胸肉飯",
        calories=450,
        protein_g=40.0,
        carbs_g=50.0,
        fat_g=8.0,
    )

    save_food_entry(estimate, client=client)

    client.table.assert_called_once_with("food_entries")
    client.table.return_value.insert.assert_called_once_with({
        "description": "雞胸肉飯",
        "calories": 450,
        "protein_g": 40.0,
        "carbs_g": 50.0,
        "fat_g": 8.0,
        "is_estimate": True,
    })


def test_save_exercise_entry_inserts_entry_then_exercises():
    client = _mock_client(entry_id="entry-999")
    entry = ExerciseEntry(
        raw_text="深蹲 3x5 100kg",
        exercises=[Exercise(name="深蹲", sets=3, reps=5, weight_kg=100.0)],
    )

    save_exercise_entry(entry, client=client)

    assert client.table.call_args_list == [
        call("exercise_entries"),
        call("exercises"),
    ]
    first_insert = client.table.return_value.insert.call_args_list[0]
    assert first_insert == call({"raw_text": "深蹲 3x5 100kg"})

    second_insert = client.table.return_value.insert.call_args_list[1]
    assert second_insert == call([{
        "entry_id": "entry-999",
        "name": "深蹲",
        "sets": 3,
        "reps": 5,
        "weight_kg": 100.0,
    }])


def test_save_inbody_entry_uses_inbody_source():
    client = _mock_client()
    result = InBodyResult(body_fat_pct=18.5, muscle_mass_kg=65.0, weight_kg=75.0, bmi=23.1)

    save_inbody_entry(result, client=client)

    client.table.assert_called_once_with("composition_entries")
    client.table.return_value.insert.assert_called_once_with({
        "weight_kg": 75.0,
        "bmi": 23.1,
        "body_fat_pct": 18.5,
        "muscle_mass_kg": 65.0,
        "source": "inbody",
    })


def test_save_weight_entry_uses_manual_source():
    client = _mock_client()
    entry = CompositionEntry(weight_kg=75.0, height_cm=175.0, bmi=24.5)

    save_weight_entry(entry, client=client)

    client.table.assert_called_once_with("composition_entries")
    client.table.return_value.insert.assert_called_once_with({
        "weight_kg": 75.0,
        "height_cm": 175.0,
        "bmi": 24.5,
        "source": "manual",
    })
