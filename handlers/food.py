from typing import Callable

from services.nutrition import analyse_food, FoodAnalysisError


async def handle_food(interaction, api_key: str, analyse_fn: Callable = None):
    if analyse_fn is None:
        analyse_fn = analyse_food

    attachment = interaction.namespace.photo
    if attachment is None:
        await interaction.response.send_message("❌ 請附上食物照片。")
        return

    await interaction.response.defer()

    try:
        estimate = await analyse_fn(image_url=attachment.url, api_key=api_key)
        msg = (
            f"🍽️ **{estimate.description}** （估算值）\n"
            f"熱量：{estimate.calories} kcal\n"
            f"蛋白質：{estimate.protein_g}g　碳水：{estimate.carbs_g}g　脂肪：{estimate.fat_g}g"
        )
        await interaction.followup.send(msg)
    except FoodAnalysisError:
        await interaction.followup.send("❌ 無法辨識圖片中的食物，請換一張照片試試。")
