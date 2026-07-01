"""
Farzand uchun Pomodoro taymeri.
"""

import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import crud

router = Router()

# Pomodoro sessiyalari uchun (oddiy xotira)
# Aslida buni DB da saqlash yaxshiroq, lekin hozircha xotirada saqlaymiz.
active_timers = {}


@router.message(F.text == "⏱️ Pomodoro")
async def btn_pomodoro(message: Message):
    """Pomodoro asosiy menyusi."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        return

    text = (
        "⏱️ <b>Pomodoro taymeri</b>\n\n"
        "Pomodoro usuli diqqatni jamlab dars qilishga yordam beradi. "
        "25 daqiqa dars qilib, so'ngra 5 daqiqa dam oling!\n\n"
        "<i>Har bir muvaffaqiyatli Pomodoro (25 daqiqa) uchun 5 ball olasiz!</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ 25 daqiqa (Dars)", callback_data="pomodoro_start_25")],
        [InlineKeyboardButton(text="⏸️ 5 daqiqa (Tanaffus)", callback_data="pomodoro_break_5")],
    ])

    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("pomodoro_start_"))
async def process_pomodoro_start(callback: CallbackQuery):
    """Pomodoro taymerini boshlash."""
    minutes = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    if user_id in active_timers:
        await callback.answer("⚠️ Sizda allaqachon faol taymer bor!", show_alert=True)
        return

    await callback.message.edit_text(
        f"⏱️ <b>{minutes} daqiqalik Pomodoro boshlandi!</b>\n\n"
        f"Diqqatni jamlang va ishingizga kirishing. Vaqt tugagach xabar beraman.",
        parse_mode="HTML"
    )
    await callback.answer(f"{minutes} daqiqa ketdi!")

    # Taymerni fonda ishga tushirish
    task = asyncio.create_task(run_timer(callback.bot, user_id, minutes * 60, is_break=False))
    active_timers[user_id] = task


@router.callback_query(F.data.startswith("pomodoro_break_"))
async def process_pomodoro_break(callback: CallbackQuery):
    """Pomodoro tanaffusini boshlash."""
    minutes = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    if user_id in active_timers:
        await callback.answer("⚠️ Sizda allaqachon faol taymer bor!", show_alert=True)
        return

    await callback.message.edit_text(
        f"⏸️ <b>{minutes} daqiqalik tanaffus boshlandi!</b>\n\n"
        f"Ko'zlaringizni dam oldiring, suv ichib oling.",
        parse_mode="HTML"
    )
    await callback.answer(f"{minutes} daqiqa dam!")

    # Taymerni fonda ishga tushirish
    task = asyncio.create_task(run_timer(callback.bot, user_id, minutes * 60, is_break=True))
    active_timers[user_id] = task


async def run_timer(bot, user_id, seconds, is_break=False):
    """Taymer jarayoni."""
    try:
        await asyncio.sleep(seconds)
        
        # Vaqt tugadi
        if is_break:
            msg = "🔔 <b>Tanaffus tugadi!</b>\n\nYangi Pomodoro boshlashga tayyormisiz?"
        else:
            msg = "🎉 <b>Pomodoro tugadi! Barakalla!</b>\n\nSiz diqqat bilan ishladingiz va <b>5 ball</b> ishlab topdingiz! Endi 5 daqiqa dam oling."
            # Ball qo'shish
            await crud.update_user_points(user_id, 5)

        await bot.send_message(user_id, msg, parse_mode="HTML")
    except asyncio.CancelledError:
        pass
    finally:
        if user_id in active_timers:
            del active_timers[user_id]
