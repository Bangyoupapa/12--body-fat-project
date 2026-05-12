import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from services.body_composition import (
    analyse_inbody, InBodyResult, InBodyParseError,
    create_composition_entry, CompositionEntry,
)


def _mock_openai_response(content: str):
    mock_msg = MagicMock()
    mock_msg.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    return mock_resp


INBODY_RESPONSE = '{"body_fat_pct":18.5,"muscle_mass_kg":65.2,"weight_kg":79.8,"bmi":24.1}'


@pytest.mark.asyncio
async def test_analyse_inbody_returns_inbody_result():
    with patch("services.body_composition.openai.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(
            return_value=_mock_openai_response(INBODY_RESPONSE)
        )
        result = await analyse_inbody(image_url="http://fake/inbody.jpg", api_key="test-key")

    assert isinstance(result, InBodyResult)
    assert result.body_fat_pct == 18.5
    assert result.muscle_mass_kg == 65.2
    assert result.weight_kg == 79.8
    assert result.bmi == 24.1


@pytest.mark.asyncio
async def test_analyse_inbody_raises_on_unrecognised_image():
    with patch("services.body_composition.openai.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(
            return_value=_mock_openai_response("這不是 InBody 報告")
        )
        with pytest.raises(InBodyParseError):
            await analyse_inbody(image_url="http://fake/not-inbody.jpg", api_key="test-key")


def test_create_composition_entry_calculates_bmi():
    result = create_composition_entry(weight_kg=75.0, height_cm=175.0)

    assert isinstance(result, CompositionEntry)
    assert result.weight_kg == 75.0
    assert result.height_cm == 175.0
    assert result.bmi == round(75.0 / (1.75 ** 2), 1)
