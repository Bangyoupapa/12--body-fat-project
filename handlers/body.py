from typing import Callable

from services.body_composition import (
    analyse_inbody, create_composition_entry, InBodyParseError
)


async def handle_inbody(interaction, api_key: str, analyse_fn: Callable = None):
    if analyse_fn is None:
        analyse_fn = analyse_inbody

    attachment = interaction.namespace.photo
    if attachment is None:
        await interaction.response.send_message("❌ 請附上 InBody 報告照片。")
        return

    await interaction.response.defer()

    try:
        result = await analyse_fn(image_url=attachment.url, api_key=api_key)
        msg = (
            f"📊 **InBody 數據已記錄**\n"
            f"體重：{result.weight_kg} kg　BMI：{result.bmi}\n"
            f"體脂率：{result.body_fat_pct}%　肌肉量：{result.muscle_mass_kg} kg"
        )
        await interaction.followup.send(msg)
    except InBodyParseError:
        await interaction.followup.send("❌ 無法解析 InBody 報告，請確認照片清晰可讀。")


async def handle_weight(interaction):
    weight = interaction.namespace.weight
    height = interaction.namespace.height

    if not weight:
        await interaction.response.send_message("❌ 請輸入體重（kg）。")
        return

    if height:
        entry = create_composition_entry(weight_kg=weight, height_cm=height)
        msg = (
            f"⚖️ **體重已記錄**\n"
            f"體重：{entry.weight_kg} kg　BMI：{entry.bmi}"
        )
    else:
        msg = f"⚖️ **體重已記錄**\n體重：{weight} kg"

    await interaction.response.send_message(msg)
