from typing import Callable, Optional

from db.storage import get_last_entry, delete_entry


async def handle_undo(interaction, get_last_fn: Callable = None, delete_fn: Callable = None):
    if get_last_fn is None:
        get_last_fn = get_last_entry
    if delete_fn is None:
        delete_fn = delete_entry

    entry = get_last_fn()
    if entry is None:
        await interaction.response.send_message("❌ 沒有可以復原的記錄。")
        return

    delete_fn(entry["table"], entry["id"])
    await interaction.response.send_message(f"🗑️ 已刪除：{entry['summary']}")
