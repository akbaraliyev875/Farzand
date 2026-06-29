"""
Ekran vaqti kuzatish middleware.
Farzandning har bir xabarida faollik vaqtini hisoblaydi.
"""

from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from database import crud

# In-memory sessiya cache (Redis o'rniga)
_sessions: Dict[int, datetime] = {}

# 30 daqiqadan ko'p bo'lsa, yangi sessiya boshlanadi
SESSION_TIMEOUT_MIN = 30


class ActivityTrackerMiddleware(BaseMiddleware):
    """Farzandlarning faollik vaqtini kuzatish."""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        now = datetime.utcnow()

        # Faqat farzandlar uchun
        user = await crud.get_user(user_id)
        if user and user.role == "child":
            last_seen = _sessions.get(user_id)

            if last_seen:
                diff_min = (now - last_seen).total_seconds() / 60

                if diff_min <= SESSION_TIMEOUT_MIN:
                    # Sessiya davom etmoqda — logga yozish
                    duration = int(diff_min)
                    if duration > 0:
                        await crud.log_activity(user_id, last_seen, now, duration)

            # Sessiyani yangilash
            _sessions[user_id] = now

        return await handler(event, data)
