import json
import re
from dataclasses import dataclass, field

import openai

_PROMPT = (
    "你是一位健身記錄助手。解析以下運動記錄文字，提取每個動作的名稱、組數、次數和重量。"
    "只回傳 JSON，格式如下："
    '{{"exercises":[{{"name":"動作名稱","sets":數字,"reps":數字,"weight_kg":數字}}]}}'
    "如果沒有重量（如有氧運動），weight_kg 填 0。"
)


class ExerciseParseError(Exception):
    pass


@dataclass
class Exercise:
    name: str
    sets: int
    reps: int
    weight_kg: float


@dataclass
class ExerciseEntry:
    exercises: list[Exercise]
    raw_text: str


async def parse_exercise(text: str, api_key: str) -> ExerciseEntry:
    client = openai.AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"{_PROMPT}\n\n{text}"}],
        max_tokens=512,
    )
    try:
        content = re.sub(r"```[a-z]*\n?|\n?```", "", response.choices[0].message.content).strip()
        data = json.loads(content)
        exercises = [Exercise(**e) for e in data["exercises"]]
        return ExerciseEntry(exercises=exercises, raw_text=text)
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        raise ExerciseParseError("無法解析運動記錄") from exc
