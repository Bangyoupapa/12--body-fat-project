import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

import openai

_INBODY_PROMPT = (
    "你是一位 InBody 掃描報告解析助手。從這張 InBody 報告照片中提取以下數據。"
    "只回傳 JSON，格式如下："
    '{{"body_fat_pct":數字,"muscle_mass_kg":數字,"weight_kg":數字,"bmi":數字}}'
    "如果某個欄位在報告中找不到，填 null。"
)


class InBodyParseError(Exception):
    pass


@dataclass
class InBodyResult:
    body_fat_pct: float
    muscle_mass_kg: float
    weight_kg: float
    bmi: float
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CompositionEntry:
    weight_kg: float
    height_cm: float
    bmi: float
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


async def analyse_inbody(image_url: str, api_key: str) -> InBodyResult:
    client = openai.AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _INBODY_PROMPT},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        max_tokens=256,
    )
    try:
        data = json.loads(response.choices[0].message.content)
        return InBodyResult(**{k: v for k, v in data.items() if v is not None})
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        raise InBodyParseError("無法從照片中解析 InBody 數據") from exc


def create_composition_entry(weight_kg: float, height_cm: float) -> CompositionEntry:
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)
    return CompositionEntry(weight_kg=weight_kg, height_cm=height_cm, bmi=bmi)
