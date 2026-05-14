import pytest
from unittest.mock import AsyncMock, MagicMock
from services.body_composition import InBodyResult, CompositionEntry, InBodyParseError
from handlers.body import handle_inbody, handle_weight


def _make_interaction(photo_url: str = None, weight: float = None, height: float = None):
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    if photo_url:
        attachment = MagicMock()
        attachment.url = photo_url
        interaction.namespace.photo = attachment
    else:
        interaction.namespace.photo = None

    interaction.namespace.weight = weight
    interaction.namespace.height = height
    return interaction


FAKE_INBODY = InBodyResult(body_fat_pct=18.5, muscle_mass_kg=65.2, weight_kg=79.8, bmi=24.1)
FAKE_ENTRY = CompositionEntry(weight_kg=75.0, height_cm=175.0, bmi=24.5)


@pytest.mark.asyncio
async def test_inbody_handler_responds_with_body_composition():
    interaction = _make_interaction(photo_url="http://fake/inbody.jpg")

    async def fake_analyse(image_url, api_key):
        return FAKE_INBODY

    await handle_inbody(interaction, api_key="test-key", analyse_fn=fake_analyse, save_fn=lambda r: None)

    interaction.followup.send.assert_called_once()
    response_text = interaction.followup.send.call_args[0][0]
    assert "18.5" in response_text
    assert "65.2" in response_text


@pytest.mark.asyncio
async def test_inbody_handler_saves_result_after_analysis():
    interaction = _make_interaction(photo_url="http://fake/inbody.jpg")
    saved = []

    async def fake_analyse(image_url, api_key):
        return FAKE_INBODY

    await handle_inbody(interaction, api_key="test-key", analyse_fn=fake_analyse, save_fn=saved.append)

    assert saved == [FAKE_INBODY]


@pytest.mark.asyncio
async def test_inbody_handler_responds_with_error_when_no_photo():
    interaction = _make_interaction()

    await handle_inbody(interaction, api_key="test-key")

    interaction.response.send_message.assert_called_once()
    assert "❌" in interaction.response.send_message.call_args[0][0]


@pytest.mark.asyncio
async def test_weight_handler_responds_with_bmi():
    interaction = _make_interaction(weight=75.0, height=175.0)

    await handle_weight(interaction, save_fn=lambda e: None)

    interaction.response.send_message.assert_called_once()
    response_text = interaction.response.send_message.call_args[0][0]
    assert "75" in response_text
    assert "BMI" in response_text


@pytest.mark.asyncio
async def test_weight_handler_saves_entry_when_height_provided():
    interaction = _make_interaction(weight=75.0, height=175.0)
    saved = []

    await handle_weight(interaction, save_fn=saved.append)

    assert len(saved) == 1
    assert saved[0].weight_kg == 75.0
