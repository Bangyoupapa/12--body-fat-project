import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from services.nutrition import analyse_food, FoodEstimate, FoodAnalysisError


def _mock_openai_response(content: str):
    mock_msg = MagicMock()
    mock_msg.content = content
    mock_choice = MagicMock()
    mock_choice.message = mock_msg
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    return mock_resp


MOCK_RESPONSE = '{"description":"雞胸肉炒飯","calories":520,"protein_g":35,"carbs_g":60,"fat_g":12}'


@pytest.mark.asyncio
async def test_analyse_food_returns_food_estimate():
    with patch("services.nutrition.openai.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(
            return_value=_mock_openai_response(MOCK_RESPONSE)
        )
        result = await analyse_food(image_url="http://fake/img.jpg", api_key="test-key")

    assert isinstance(result, FoodEstimate)
    assert result.calories == 520
    assert result.protein_g == 35
    assert result.carbs_g == 60
    assert result.fat_g == 12
    assert result.description == "雞胸肉炒飯"
    assert result.is_estimate is True


@pytest.mark.asyncio
async def test_analyse_food_is_always_marked_as_estimate():
    # Even if GPT returns a confident-sounding response, is_estimate must be True
    with patch("services.nutrition.openai.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(
            return_value=_mock_openai_response(MOCK_RESPONSE)
        )
        result = await analyse_food(image_url="http://fake/img.jpg", api_key="test-key")
    assert result.is_estimate is True


@pytest.mark.asyncio
async def test_analyse_food_raises_on_unrecognised_image():
    with patch("services.nutrition.openai.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(
            return_value=_mock_openai_response("無法辨識這張圖片中的食物")
        )
        with pytest.raises(FoodAnalysisError):
            await analyse_food(image_url="http://fake/not-food.jpg", api_key="test-key")
