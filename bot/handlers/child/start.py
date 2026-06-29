"""
Farzand start handleri.
Farzand uchun /start va asosiy interaksiyalar.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from database import crud
from bot.keyboards.child_kb import child_main_kb, connect_kb

router = Router()


LEARNING_MATERIALS = [
    {
        "title": "🔐 Parol xavfsizligi",
        "content": (
            "🔐 <b>Kuchli parol yaratish qoidalari:</b>\n\n"
            "1️⃣ Kamida 8 belgidan iborat bo'lsin\n"
            "2️⃣ Katta va kichik harflar aralashtiring\n"
            "3️⃣ Raqam va maxsus belgilar qo'shing (!@#$)\n"
            "4️⃣ Ismingiz yoki tug'ilgan kuningizni ishlatmang\n"
            "5️⃣ Har bir akkaunt uchun alohida parol\n\n"
            "❌ Yomon parol: <code>ali2010</code>\n"
            "✅ Yaxshi parol: <code>K!tob_0qish#2024</code>"
        )
    },
    {
        "title": "🎣 Fishing hujumlar",
        "content": (
            "🎣 <b>Fishing (phishing) nima?</b>\n\n"
            "Bu — firibgarlar sizni aldab, parolingizni "
            "olishga harakat qiladigan usul.\n\n"
            "⚠️ <b>Qanday aniqlash:</b>\n"
            "• Noma'lum linklar yuboriladi\n"
            "• 'Tabriklaymiz, siz yutdingiz!' degan xabarlar\n"
            "• Tezda pul yuborishni so'rashadi\n\n"
            "🛡️ <b>Nima qilish kerak:</b>\n"
            "• Noma'lum linkni OCHMANG\n"
            "• Parolni hech kimga bermang\n"
            "• Shubhali xabar kelsa — ota-onangizga ayting"
        )
    },
    {
        "title": "👥 Onlayn bulling",
        "content": (
            "👥 <b>Onlayn bulling (kiberbulling) nima?</b>\n\n"
            "Bu — internetda biror kishini haqorat qilish, "
            "qo'rqitish yoki kamsitish.\n\n"
            "😢 <b>Misollar:</b>\n"
            "• Guruhda birovni masxara qilish\n"
            "• Shaxsiy rasm/videoni ruxsatsiz tarqatish\n"
            "• Doimiy yomon xabarlar yozish\n\n"
            "💪 <b>Nima qilish kerak:</b>\n"
            "• Javob bermang va blokga oling\n"
            "• Skrinshotni saqlang\n"
            "• Ota-onangiz yoki o'qituvchingizga ayting\n"
            "• Bu sizning aybingiz EMAS!"
        )
    },
    {
        "title": "📱 Ekran vaqti",
        "content": (
            "📱 <b>Ekran vaqtini boshqarish:</b>\n\n"
            "⏰ <b>Tavsiya etilgan vaqt:</b>\n"
            "• Maktab kunlari: 1-2 soat\n"
            "• Dam olish kunlari: 2-3 soat\n\n"
            "🌟 <b>Foydali odatlar:</b>\n"
            "• Dars qilishdan oldin telefon ishlatmang\n"
            "• Uxlashdan 1 soat oldin ekranni o'chiring\n"
            "• Har 30 daqiqada 5 daqiqa dam oling\n"
            "• Jismoniy faoliyat bilan almashtirib turing"
        )
    },
]


@router.message(F.text == "📚 O'quv materiallar")
async def btn_learn(message: Message):
    """O'quv materiallar — xavfsizlik darsliklari."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        return

    for material in LEARNING_MATERIALS:
        await message.answer(material["content"], parse_mode="HTML")


@router.message(F.text == "📊 Mening statistikam")
async def btn_my_stats(message: Message):
    """Farzandning o'z statistikasi."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        return

    # Kunlik faollik
    daily_min = await crud.get_daily_activity(message.from_user.id)
    hours = daily_min // 60
    mins = daily_min % 60

    # Oxirgi test
    last_test = await crud.get_latest_test(message.from_user.id)
    test_info = "📝 Hali test yechilmagan"
    if last_test:
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        risk_text = {"low": "Past", "medium": "O'rtacha", "high": "Yuqori"}
        test_info = (
            f"📝 Oxirgi test: {risk_emoji.get(last_test.risk_level, '⚪')} "
            f"{risk_text.get(last_test.risk_level, 'Noma\'lum')} xavf darajasi\n"
            f"   Ball: {last_test.score}"
        )

    await message.answer(
        f"📊 <b>Mening statistikam</b>\n\n"
        f"📱 Bugungi ekran vaqti: <b>{hours} soat {mins} daqiqa</b>\n\n"
        f"{test_info}\n\n"
        f"💡 Ekran vaqtini kamaytirib, kitob o'qing! 📚",
        parse_mode="HTML"
    )
