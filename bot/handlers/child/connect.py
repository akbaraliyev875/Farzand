"""
Farzandni ota-onaga ulash handleri.
/connect — ulanish kodi kiritish.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import crud
from bot.keyboards.child_kb import child_main_kb

router = Router()


class ConnectStates(StatesGroup):
    waiting_code = State()


@router.message(Command("connect"))
async def cmd_connect(message: Message, state: FSMContext):
    """/connect — Ota-onaga ulanish."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        await message.answer(
            "⚠️ Bu buyruq faqat farzandlar uchun. "
            "/start buyrug'i orqali farzand sifatida ro'yxatdan o'ting."
        )
        return

    # Allaqachon ulangan mi?
    parent_id = await crud.get_parent_for_child(message.from_user.id)
    if parent_id:
        await message.answer(
            "✅ Siz allaqachon ota-onangizga ulangansiz!",
            parse_mode="HTML"
        )
        return

    await state.set_state(ConnectStates.waiting_code)
    await message.answer(
        "🔗 <b>Ota-onaga ulanish</b>\n\n"
        "Ota-onangizdan olgan 6 raqamli kodni kiriting:",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "connect_parent")
async def on_connect_btn(callback: CallbackQuery, state: FSMContext):
    """Ulanish tugmasi bosilganda."""
    await state.set_state(ConnectStates.waiting_code)
    await callback.message.answer(
        "🔗 <b>Ota-onaga ulanish</b>\n\n"
        "Ota-onangizdan olgan 6 raqamli kodni kiriting:",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ConnectStates.waiting_code)
async def on_code_entered(message: Message, state: FSMContext):
    """Ulanish kodi kiritilganda."""
    code = message.text.strip()

    # Kod formatini tekshirish
    if not code.isdigit() or len(code) != 6:
        await message.answer(
            "❌ Noto'g'ri format. 6 raqamli kodni kiriting.\n"
            "Masalan: <code>123456</code>",
            parse_mode="HTML"
        )
        return

    # Kodni tekshirish va ulash
    link = await crud.connect_child(message.from_user.id, code)

    if not link:
        await message.answer(
            "❌ Bu kod topilmadi yoki muddati tugagan.\n\n"
            "Ota-onangizdan yangi kod so'rang (/link buyrug'i orqali).",
            parse_mode="HTML"
        )
        await state.clear()
        return

    await state.clear()

    # Farzandga xabar
    await message.answer(
        "✅ <b>Muvaffaqiyatli ulandi!</b>\n\n"
        "Endi ota-onangiz sizning faolligingizni kuzatib boradi.\n"
        "Bu sizning xavfsizligingiz uchun! 🛡️",
        reply_markup=child_main_kb(),
        parse_mode="HTML"
    )

    # Ota-onaga xabar
    child_name = message.from_user.full_name or "Farzand"
    try:
        await message.bot.send_message(
            link.parent_id,
            f"🎉 <b>Farzandingiz ulandi!</b>\n\n"
            f"👤 Ism: <b>{child_name}</b>\n\n"
            f"Endi /report buyrug'i orqali hisobotlarni olishingiz mumkin.",
            parse_mode="HTML"
        )
    except Exception:
        pass  # Ota-ona botni bloklagan bo'lishi mumkin
