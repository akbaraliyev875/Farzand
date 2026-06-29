"""
Ota-onaga xabar yuborish xizmati.
"""

import logging
from aiogram import Bot

logger = logging.getLogger(__name__)


async def notify_parent(bot: Bot, parent_id: int, text: str):
    """Ota-onaga xabar yuborish."""
    try:
        await bot.send_message(parent_id, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ota-onaga xabar yuborishda xato (ID: {parent_id}): {e}")
