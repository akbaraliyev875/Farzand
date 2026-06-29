"""
Farzand ulash handleri.
/link — ulanish kodi generatsiya qilish.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database import crud

router = Router()


@router.message(Command("link"))
async def cmd_link(message: Message):
    """/link — Farzand uchun ulanish kodi yaratish."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "parent":
        await message.answer(
            "⚠️ Bu buyruq faqat ota-onalar uchun. "
            "/start buyrug'i orqali ota-ona sifatida ro'yxatdan o'ting.",
            parse_mode="HTML"
        )
        return

    # Ulanish kodi yaratish
    code = await crud.create_family_link(message.from_user.id)

    await message.answer(
        f"🔗 <b>Ulanish kodi tayyor!</b>\n\n"
        f"📋 Kod: <code>{code}</code>\n\n"
        f"👆 Kodni bosib nusxa oling va farzandingizga yuboring.\n\n"
        f"Farzandingiz botda /connect buyrug'ini yozib, "
        f"shu kodni kiritishi kerak.\n\n"
        f"⏰ Kod <b>24 soat</b> amal qiladi.",
        parse_mode="HTML"
    )


@router.message(F.text == "🔗 Farzand ulash")
async def btn_link(message: Message):
    """Farzand ulash tugmasi."""
    await cmd_link(message)
