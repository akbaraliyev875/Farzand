"""
Farzand uchun hayotiy vaziyatlar (axloqiy) simulyatori.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import crud
from bot.services.ai_analyzer import generate_moral_situation, evaluate_moral_answer

router = Router()

class SimulatorStates(StatesGroup):
    answering_situation = State()

@router.message(F.text == "🎭 Hayotiy Vaziyat")
async def btn_simulator(message: Message, state: FSMContext):
    """Simulyatorni ishga tushirish."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        return

    wait_msg = await message.answer("⏳ <i>Siz uchun qiziqarli hayotiy vaziyat o'ylanmoqda...</i>", parse_mode="HTML")
    
    situation = await generate_moral_situation()
    
    await state.update_data(situation=situation)
    await state.set_state(SimulatorStates.answering_situation)
    
    await wait_msg.delete()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="sim_cancel")]
    ])
    
    await message.answer(
        f"🤔 <b>Hayotiy Vaziyat:</b>\n\n{situation}\n\n<i>Javobingizni xabar orqali yozib yuboring:</i>",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data == "sim_cancel")
async def process_sim_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Simulyator to'xtatildi. Istalgan vaqt qayta urinib ko'rishingiz mumkin.")
    await callback.answer()

@router.message(SimulatorStates.answering_situation, F.text)
async def process_sim_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    situation = data.get("situation", "")
    answer = message.text
    
    await state.clear()
    wait_msg = await message.answer("⏳ <i>Javobingiz tahlil qilinmoqda...</i>", parse_mode="HTML")
    
    feedback = await evaluate_moral_answer(situation, answer)
    
    # Har bir javob uchun 2 ball bonus
    await crud.update_user_points(message.from_user.id, 2)
    
    await wait_msg.delete()
    await message.answer(
        f"🎙 <b>Ustozning fikri:</b>\n\n{feedback}\n\n<i>🎉 Ishtirokingiz uchun +2 ball berildi!</i>",
        parse_mode="HTML"
    )
