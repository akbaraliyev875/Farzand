"""
Xavfli so'zlar filtri middleware.
Farzand bot ichida yozgan xabarlarni tekshiradi.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from database import crud

# Xavfli so'zlar kategoriyalari
DANGER_KEYWORDS = {
    "gambling": [
        "bet", "casino", "stavka", "bukmekerlik", "qimor",
        "1xbet", "mostbet", "linebet", "melbet", "pin-up",
    ],
    "adult": [
        "porno", "18+", "xxx", "erotika", "onlyfans",
    ],
    "drugs": [
        "dori", "narkotik", "giyohvand", "gashish", "geroin",
    ],
    "violence": [
        "urush", "zo'ravonlik", "o'ldirish", "qon", "jang",
    ],
    "scam": [
        "skam", "kripto invest", "tez pul", "piramida",
        "daromad kafolat", "100% foyda",
    ],
}

CATEGORY_NAMES = {
    "gambling": "🎰 Qimor",
    "adult": "🔞 18+ kontent",
    "drugs": "💊 Giyohvandlik",
    "violence": "⚔️ Zo'ravonlik",
    "scam": "🚨 Firibgarlik",
}


class KeywordFilterMiddleware(BaseMiddleware):
    """Farzand xabarlarida xavfli so'zlarni tekshirish."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user or not event.text:
            return await handler(event, data)

        user_id = event.from_user.id
        text = event.text.lower()

        # Faqat farzandlar uchun
        user = await crud.get_user(user_id)
        if not user or user.role != "child":
            return await handler(event, data)

        # So'zlarni tekshirish
        for category, keywords in DANGER_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    # Signalni saqlash
                    await crud.save_alert(user_id, keyword, category)

                    # Ota-onaga xabar
                    parent_id = await crud.get_parent_for_child(user_id)
                    if parent_id:
                        child_name = event.from_user.full_name or "Farzandingiz"
                        cat_name = CATEGORY_NAMES.get(category, category)
                        try:
                            await event.bot.send_message(
                                parent_id,
                                f"⚠️ <b>OGOHLANTIRISH!</b>\n\n"
                                f"👤 <b>{child_name}</b> botda xavfli so'z ishlatdi.\n\n"
                                f"📌 Kategoriya: {cat_name}\n"
                                f"🔑 So'z: <code>{keyword}</code>\n\n"
                                f"💬 Farzandingiz bilan gaplashishni tavsiya etamiz.",
                                parse_mode="HTML"
                            )
                        except Exception:
                            pass
                    break  # Bitta kategoriyadan bitta ogohlantirish yetarli

        return await handler(event, data)
