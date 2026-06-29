"""
Kontent tekshirish handleri.
Ota-ona skrinshot yuboradi → AI tahlil qiladi.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database import crud
from bot.config import FREE_LIMITS, PREMIUM_LIMITS
from bot.services.ai_analyzer import analyze_screenshot

router = Router()

RESULT_EMOJI = {
    "safe": "🟢 XAVFSIZ",
    "violence": "🔴 ZO'RAVONLIK",
    "adult": "🔴 18+ KONTENT",
    "gambling": "🔴 QIMOR",
    "unknown": "🟡 ANIQLANMADI",
}

RESULT_DESCRIPTION = {
    "safe": "Bu kontent farzandingiz uchun muammo emas deb baholandi.",
    "violence": "Bu kontentda zo'ravonlik belgilari aniqlandi. Farzandingiz bilan gaplashing.",
    "adult": "Bu kontentda 18+ materiallar aniqlandi. Darhol chora ko'ring.",
    "gambling": "Bu kontentda qimor/gambling belgilari aniqlandi.",
    "unknown": "Kontent aniq tahlil qilinmadi. O'zingiz ko'rib chiqing.",
}


@router.message(Command("check"))
async def cmd_check(message: Message):
    """/check — Kontent tekshirish haqida ma'lumot."""
    await message.answer(
        "🔍 <b>Kontent tekshirish</b>\n\n"
        "Farzandingiz ekranining skrinshotini yuboring — "
        "AI uni tahlil qilib, xavfsizlik darajasini aniqlaydi.\n\n"
        "📸 Rasmni shu chatga yuboring:",
        parse_mode="HTML"
    )


@router.message(F.text == "🔍 Kontent tekshirish")
async def btn_check(message: Message):
    """Kontent tekshirish tugmasi."""
    await cmd_check(message)


@router.message(F.photo)
async def on_photo_received(message: Message):
    """Rasm kelganda kontent tekshirish."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "parent":
        return  # Faqat ota-onalar uchun

    # Limitni tekshirish
    today_count = await crud.get_today_check_count(message.from_user.id)
    limit = PREMIUM_LIMITS["content_checks_per_day"] if user.is_premium else FREE_LIMITS["content_checks_per_day"]

    if today_count >= limit:
        await message.answer(
            f"⚠️ Bugungi limit tugadi ({limit} ta/kun).\n\n"
            "Premium obunaga o'tib cheksiz tekshiruv oling!",
            parse_mode="HTML"
        )
        return

    # Tahlil boshlash
    wait_msg = await message.answer("🔄 Tahlil qilinmoqda... Biroz kuting.")

    photo = message.photo[-1]  # Eng katta o'lcham
    result = await analyze_screenshot(message.bot, photo)

    emoji = RESULT_EMOJI.get(result, "🟡 ANIQLANMADI")
    description = RESULT_DESCRIPTION.get(result, "Kontent aniqlanmadi.")

    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    await wait_msg.edit_text(
        f"🔍 <b>Kontent tahlil natijasi:</b>\n\n"
        f"{emoji}\n\n"
        f"{description}\n\n"
        f"📁 Tekshirilgan: {now}\n"
        f"📊 Bugungi tekshiruvlar: {today_count + 1}/{limit}",
        parse_mode="HTML"
    )

    # Natijani saqlash
    await crud.save_content_check(message.from_user.id, photo.file_id, result)
