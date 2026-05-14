from typing import Callable

from services.exercise import parse_exercise, ExerciseParseError
from db.storage import save_exercise_entry


async def handle_exercise(interaction, api_key: str, parse_fn: Callable = None, save_fn: Callable = None):
    if parse_fn is None:
        parse_fn = parse_exercise
    if save_fn is None:
        save_fn = save_exercise_entry

    text = interaction.namespace.text
    if not text:
        await interaction.response.send_message("❌ 請輸入運動記錄，例如：深蹲 5×5 100kg")
        return

    await interaction.response.defer()

    try:
        entry = await parse_fn(text=text, api_key=api_key)
        lines = ["💪 **運動記錄已儲存**\n"]
        for ex in entry.exercises:
            weight = f"　{ex.weight_kg}kg" if ex.weight_kg > 0 else ""
            lines.append(f"• {ex.name}　{ex.sets}組 × {ex.reps}下{weight}")
        save_fn(entry)
        await interaction.followup.send("\n".join(lines))
    except ExerciseParseError:
        await interaction.followup.send("❌ 無法解析運動記錄，請用「動作 組數×次數 重量kg」的格式。")
