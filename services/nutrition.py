import json
from dataclasses import dataclass

import openai

_PROMPT = (
    "你是一位營養師。分析這張食物照片，估算其熱量和三大營養素。"
    "只回傳 JSON，格式如下："
    '{{"description":"食物名稱","calories":數字,"protein_g":數字,"carbs_g":數字,"fat_g":數字}}'
)


class FoodAnalysisError(Exception):
    pass


@dataclass
class FoodEstimate:
    description: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    is_estimate: bool = True


async def analyse_food(image_url: str, api_key: str) -> FoodEstimate:
    client = openai.AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _PROMPT},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        max_tokens=256,
    )
    try:
        data = json.loads(response.choices[0].message.content)
        return FoodEstimate(**data)
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        raise FoodAnalysisError("無法辨識圖片中的食物") from exc
