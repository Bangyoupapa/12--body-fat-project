import pytest
from unittest.mock import AsyncMock, MagicMock
from services.exercise import ExerciseEntry, Exercise, ExerciseParseError
from handlers.exercise import handle_exercise


def _make_interaction(text: str = None):
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.namespace.text = text
    return interaction


FAKE_ENTRY = ExerciseEntry(
    exercises=[
        Exercise(name="深蹲", sets=5, reps=5, weight_kg=100),
        Exercise(name="臥推", sets=4, reps=8, weight_kg=80),
    ],
    raw_text="深蹲 5×5 100kg，臥推 4×8 80kg",
)


@pytest.mark.asyncio
async def test_exercise_handler_responds_with_exercise_summary():
    interaction = _make_interaction(text="深蹲 5×5 100kg，臥推 4×8 80kg")

    async def fake_parse(text, api_key):
        return FAKE_ENTRY

    await handle_exercise(interaction, api_key="test-key", parse_fn=fake_parse, save_fn=lambda e: None)

    interaction.followup.send.assert_called_once()
    response_text = interaction.followup.send.call_args[0][0]
    assert "深蹲" in response_text
    assert "臥推" in response_text


@pytest.mark.asyncio
async def test_exercise_handler_saves_entry_after_parsing():
    interaction = _make_interaction(text="深蹲 5×5 100kg")
    saved = []

    async def fake_parse(text, api_key):
        return FAKE_ENTRY

    await handle_exercise(interaction, api_key="test-key", parse_fn=fake_parse, save_fn=saved.append)

    assert saved == [FAKE_ENTRY]


@pytest.mark.asyncio
async def test_exercise_handler_responds_with_error_when_no_text():
    interaction = _make_interaction(text=None)

    await handle_exercise(interaction, api_key="test-key")

    interaction.response.send_message.assert_called_once()
    error_text = interaction.response.send_message.call_args[0][0]
    assert "❌" in error_text


@pytest.mark.asyncio
async def test_exercise_handler_responds_with_error_on_parse_failure():
    interaction = _make_interaction(text="asdfghjkl")

    async def failing_parse(text, api_key):
        raise ExerciseParseError("無法解析")

    await handle_exercise(interaction, api_key="test-key", parse_fn=failing_parse, save_fn=lambda e: None)

    interaction.followup.send.assert_called_once()
    error_text = interaction.followup.send.call_args[0][0]
    assert "❌" in error_text
