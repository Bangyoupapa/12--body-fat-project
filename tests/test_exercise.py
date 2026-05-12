import pytest
from unittest.mock import patch, AsyncMock
from services.exercise import parse_exercise, ExerciseEntry, Exercise, ExerciseParseError


def _mock_openai_response(content: str):
    from unittest.mock import MagicMock
    mock_msg = MagicMock()
    mock_msg.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    return mock_resp


SINGLE_EXERCISE_RESPONSE = '{"exercises":[{"name":"深蹲","sets":5,"reps":5,"weight_kg":100}]}'
MULTI_EXERCISE_RESPONSE = '{"exercises":[{"name":"深蹲","sets":5,"reps":5,"weight_kg":100},{"name":"臥推","sets":4,"reps":8,"weight_kg":80}]}'


@pytest.mark.asyncio
async def test_parse_exercise_returns_exercise_entry():
    with patch("services.exercise.openai.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(
            return_value=_mock_openai_response(SINGLE_EXERCISE_RESPONSE)
        )
        result = await parse_exercise("深蹲 5×5 100kg", api_key="test-key")

    assert isinstance(result, ExerciseEntry)
    assert len(result.exercises) == 1
    ex = result.exercises[0]
    assert isinstance(ex, Exercise)
    assert ex.name == "深蹲"
    assert ex.sets == 5
    assert ex.reps == 5
    assert ex.weight_kg == 100
    assert result.raw_text == "深蹲 5×5 100kg"


@pytest.mark.asyncio
async def test_parse_exercise_handles_multiple_exercises():
    with patch("services.exercise.openai.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(
            return_value=_mock_openai_response(MULTI_EXERCISE_RESPONSE)
        )
        result = await parse_exercise("深蹲 5×5 100kg，臥推 4×8 80kg", api_key="test-key")

    assert len(result.exercises) == 2
    assert result.exercises[0].name == "深蹲"
    assert result.exercises[1].name == "臥推"
    assert result.exercises[1].weight_kg == 80


@pytest.mark.asyncio
async def test_parse_exercise_raises_on_unrecognisable_text():
    with patch("services.exercise.openai.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(
            return_value=_mock_openai_response("這不是運動記錄")
        )
        with pytest.raises(ExerciseParseError):
            await parse_exercise("asdfghjkl", api_key="test-key")
