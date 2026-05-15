import pytest
from unittest.mock import AsyncMock, MagicMock
from handlers.undo import handle_undo


def _make_interaction():
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()
    return interaction


@pytest.mark.asyncio
async def test_undo_responds_with_deleted_entry_summary():
    interaction = _make_interaction()
    last_entry = {"table": "food_entries", "id": "abc-123", "summary": "雞胸肉飯（450 kcal）"}
    deleted = []

    await handle_undo(
        interaction,
        get_last_fn=lambda: last_entry,
        delete_fn=lambda table, entry_id: deleted.append((table, entry_id)),
    )

    interaction.response.send_message.assert_called_once()
    msg = interaction.response.send_message.call_args[0][0]
    assert "雞胸肉飯（450 kcal）" in msg
    assert deleted == [("food_entries", "abc-123")]


@pytest.mark.asyncio
async def test_undo_responds_with_error_when_nothing_to_delete():
    interaction = _make_interaction()

    await handle_undo(
        interaction,
        get_last_fn=lambda: None,
        delete_fn=lambda table, entry_id: None,
    )

    interaction.response.send_message.assert_called_once()
    msg = interaction.response.send_message.call_args[0][0]
    assert "❌" in msg
