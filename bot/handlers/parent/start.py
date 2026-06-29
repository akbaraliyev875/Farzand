"""
Ota-ona start handleri.
/start, rol tanlash, ro'yxatdan o'tish, /help
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from database import crud
from bot.keyboards.parent_kb import role_selection_kb, parent_main_kb
from bot.keyboards.child_kb import child_main_kb

router = Router()


WELCOME_TEXT = """
🛡️ <b>Farzand Nazorati</b> botiga xush kelibsiz!

Bu bot orqali farzandingizning internet xavfsizligini nazorat qilishingiz mumkin.

👇 <b>Rolni tanlang:</b>
"""

PRIVACY_TEXT = """
ℹ️ <b>Maxfiylik siyosati:</b>

✅ Bot ichidagi xabarlarni filtrlash
✅ Faollik vaqtini hisoblash
✅ Siz yuborgan skrinshot'larni tahlil qilish

❌ Shaxsiy chatlarni o'qish
❌ Ma'lumotlarni uchinchi shaxslarga sotish
❌ Farzand bilimisiz uni kuzatish
"""

HELP_PARENT = """
❓ <b>Yordam — Ota-ona uchun</b>

📊 <b>Hisobot</b> — Farzandingizning kunlik ekran vaqti va ogohlantirishlar
🔗 <b>Farzand ulash</b> — Ulanish kodi orqali farzandni qo'shish
🔍 <b>Kontent tekshirish</b> — Skrinshot yuborib xavfsizligini tekshirish
💡 <b>Bugungi maslahat</b> — Xavfsizlik bo'yicha kunlik maslahat
⚙️ <b>Sozlamalar</b> — Bot sozlamalari

<b>Komandalar:</b>
/start — Botni qayta ishga tushirish
/link — Farzand ulash kodi olish
/report — Hisobot ko'rish
/check — Kontent tekshirish
/tips — Bugungi maslahat
/help — Yordam
"""

HELP_CHILD = """
❓ <b>Yordam — Farzand uchun</b>

📝 <b>Test yechish</b> — Internet qaramlik testini yechish
📚 <b>O'quv materiallar</b> — Xavfsizlik bo'yicha darsliklar
📊 <b>Mening statistikam</b> — O'z faolligingizni ko'rish

<b>Komandalar:</b>
/start — Botni qayta ishga tushirish
/connect — Ota-onaga ulanish
/test — Qaramlik testini boshlash
/help — Yordam
"""


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    /start — Xush kelibsiz xabari va rol tanlash.
    Agar foydalanuvchi allaqachon ro'yxatdan o'tgan bo'lsa, asosiy menyuni ko'rsatish.
    """
    user = await crud.get_user(message.from_user.id)

    if user:
        # Allaqachon ro'yxatdan o'tgan
        if user.role == "parent":
            await message.answer(
                f"👋 Qaytib kelganingizdan xursandmiz, <b>{user.full_name}</b>!\n\n"
                "📱 Asosiy menyudan foydalaning:",
                reply_markup=parent_main_kb(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f"👋 Salom, <b>{user.full_name}</b>!\n\n"
                "📱 Menyudan foydalaning:",
                reply_markup=child_main_kb(),
                parse_mode="HTML"
            )
        return

    # Yangi foydalanuvchi — rol tanlash
    await message.answer(
        WELCOME_TEXT,
        reply_markup=role_selection_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "role_parent")
async def on_role_parent(callback: CallbackQuery):
    """Ota-ona sifatida ro'yxatdan o'tish."""
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name or "Ota-ona"
    username = callback.from_user.username

    # Foydalanuvchi yaratish
    existing = await crud.get_user(user_id)
    if not existing:
        await crud.create_user(user_id, "parent", full_name, username)

    await callback.message.edit_text(
        f"✅ <b>{full_name}</b>, siz ota-ona sifatida ro'yxatdan o'tdingiz!\n\n"
        "Endi farzandingizni ulash uchun <b>🔗 Farzand ulash</b> tugmasini bosing.\n\n"
        f"{PRIVACY_TEXT}",
        parse_mode="HTML"
    )
    await callback.message.answer(
        "📱 Asosiy menyu:",
        reply_markup=parent_main_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "role_child")
async def on_role_child(callback: CallbackQuery):
    """Farzand sifatida ro'yxatdan o'tish."""
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name or "Farzand"
    username = callback.from_user.username

    existing = await crud.get_user(user_id)
    if not existing:
        await crud.create_user(user_id, "child", full_name, username)

    await callback.message.edit_text(
        f"✅ <b>{full_name}</b>, siz farzand sifatida ro'yxatdan o'tdingiz!\n\n"
        "Endi ota-onangizga ulanish uchun <b>🔗 Ota-onaga ulanish</b> tugmasini bosing.\n\n"
        "Ulanish kodini ota-onangizdan so'rang.",
        parse_mode="HTML"
    )
    await callback.message.answer(
        "📱 Menyu:",
        reply_markup=child_main_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """/help — Yordam xabari."""
    user = await crud.get_user(message.from_user.id)
    if user and user.role == "child":
        await message.answer(HELP_CHILD, parse_mode="HTML")
    else:
        await message.answer(HELP_PARENT, parse_mode="HTML")


@router.message(F.text == "❓ Yordam")
async def btn_help(message: Message):
    """Yordam tugmasi."""
    await cmd_help(message)


@router.message(Command("tips"))
async def cmd_tips(message: Message):
    """/tips — Bugungi maslahat."""
    tip = await crud.get_random_tip()
    if tip:
        await message.answer(
            f"💡 <b>Bugungi maslahat:</b>\n\n{tip.tip_uz}",
            parse_mode="HTML"
        )
    else:
        await message.answer("📭 Hozircha maslahatlar mavjud emas.")


@router.message(F.text == "💡 Bugungi maslahat")
async def btn_tips(message: Message):
    """Bugungi maslahat tugmasi."""
    await cmd_tips(message)


@router.message(F.text == "⚙️ Sozlamalar")
async def btn_settings(message: Message):
    """Sozlamalar tugmasi."""
    user = await crud.get_user(message.from_user.id)
    if not user:
        return

    premium_status = "✅ Premium" if user.is_premium else "❌ Bepul"
    children = await crud.get_children_for_parent(message.from_user.id)

    await message.answer(
        f"⚙️ <b>Sozlamalar</b>\n\n"
        f"👤 Ism: <b>{user.full_name}</b>\n"
        f"📦 Tarif: <b>{premium_status}</b>\n"
        f"👶 Farzandlar soni: <b>{len(children)}</b>\n"
        f"🌐 Til: <b>O'zbek</b>\n\n"
        f"ℹ️ Premium obuna uchun /premium buyrug'ini yozing.",
        parse_mode="HTML"
    )
