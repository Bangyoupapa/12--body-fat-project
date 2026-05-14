import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.nutrition import FoodEstimate, FoodAnalysisError
from handlers.food import handle_food


def _make_interaction(image_url: str = None):
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()

    if image_url:
        attachment = MagicMock()
        attachment.url = image_url
        interaction.namespace.photo = attachment
    else:
        interaction.namespace.photo = None

    return interaction


FAKE_ESTIMATE = FoodEstimate(
    description="雞胸肉炒飯",
    calories=520,
    protein_g=35,
    carbs_g=60,
    fat_g=12,
)


@pytest.mark.asyncio
async def test_food_handler_responds_with_nutritional_summary():
    interaction = _make_interaction(image_url="http://fake/food.jpg")

    async def fake_analyse(image_url, api_key):
        return FAKE_ESTIMATE

    await handle_food(interaction, api_key="test-key", analyse_fn=fake_analyse, save_fn=lambda e: None)

    interaction.followup.send.assert_called_once()
    response_text = interaction.followup.send.call_args[0][0]
    assert "雞胸肉炒飯" in response_text
    assert "520" in response_text
    assert "35" in response_text  # protein


@pytest.mark.asyncio
async def test_food_handler_responds_with_error_when_no_photo():
    interaction = _make_interaction(image_url=None)

    await handle_food(interaction, api_key="test-key")

    interaction.response.send_message.assert_called_once()
    error_text = interaction.response.send_message.call_args[0][0]
    assert "照片" in error_text


@pytest.mark.asyncio
async def test_food_handler_saves_entry_after_analysis():
    interaction = _make_interaction(image_url="http://fake/food.jpg")
    saved = []

    async def fake_analyse(image_url, api_key):
        return FAKE_ESTIMATE

    def fake_save(estimate):
        saved.append(estimate)

    await handle_food(interaction, api_key="test-key", analyse_fn=fake_analyse, save_fn=fake_save)

    assert saved == [FAKE_ESTIMATE]



@pytest.mark.asyncio
async def test_food_handler_responds_with_error_when_image_unrecognisable():
    interaction = _make_interaction(image_url="http://fake/food.jpg")

    async def failing_analyse(image_url, api_key):
        raise FoodAnalysisError("無法辨識")

    await handle_food(interaction, api_key="test-key", analyse_fn=failing_analyse, save_fn=lambda e: None)

    interaction.followup.send.assert_called_once()
    error_text = interaction.followup.send.call_args[0][0]
    assert "❌" in error_text
