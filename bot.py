import os
import discord
from discord import app_commands
from dotenv import load_dotenv

from handlers.food import handle_food
from handlers.exercise import handle_exercise
from handlers.body import handle_inbody, handle_weight

load_dotenv()

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="food", description="上傳食物照片，分析熱量和營養素")
@app_commands.describe(photo="食物照片")
async def food_command(interaction: discord.Interaction, photo: discord.Attachment):
    interaction.namespace.photo = photo
    await handle_food(interaction, api_key=OPENAI_API_KEY)


@tree.command(name="exercise", description="記錄今天的運動，例如：深蹲 5×5 100kg")
@app_commands.describe(text="運動記錄")
async def exercise_command(interaction: discord.Interaction, text: str):
    interaction.namespace.text = text
    await handle_exercise(interaction, api_key=OPENAI_API_KEY)


@tree.command(name="inbody", description="上傳 InBody 報告照片，記錄體脂和肌肉量")
@app_commands.describe(photo="InBody 報告照片")
async def inbody_command(interaction: discord.Interaction, photo: discord.Attachment):
    interaction.namespace.photo = photo
    await handle_inbody(interaction, api_key=OPENAI_API_KEY)


@tree.command(name="weight", description="記錄今天的體重")
@app_commands.describe(weight="體重（kg）", height="身高（cm），首次使用請填寫")
async def weight_command(interaction: discord.Interaction, weight: float, height: float = None):
    interaction.namespace.weight = weight
    interaction.namespace.height = height
    await handle_weight(interaction)


@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot 已上線：{client.user}")


client.run(DISCORD_TOKEN)
