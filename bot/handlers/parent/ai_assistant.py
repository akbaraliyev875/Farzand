import os
import json

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import crud
from bot.keyboards.parent_kb import ai_faq_kb
from bot.services.ai_analyzer import answer_parent_question

router = Router()


class AIStates(StatesGroup):
    waiting_for_question = State()


FAQ_TOPICS = {
    "faq_fishing": "Fishing (phishing) nima? Bolani undan qanday himoya qilish mumkin?",
    "faq_bulling": "Onlayn bulling (kiberbulling) nima? Belgilari qanday va bola shikoyat qilsa nima qilish kerak?",
    "faq_addiction": "Ekran qaramligi nima? Belgilari qanday va uni qanday kamaytirish mumkin?",
    "faq_password": "Bolaga xavfsiz parol yaratishni qanday o'rgatish mumkin?",
    "faq_protection": "Bolani internetda xavflardan (firibgarlar, nojo'ya kontent, notanish odamlar) qanday himoya qilish mumkin?",
    "faq_gaming": "O'yin qaramligi (gaming addiction) belgilari qanday va uni qanday bartaraf etish mumkin?"
}


def _get_static_answer(faq_key: str) -> str:
    """JSON fayldan statik javobni yuklab beradi."""
    try:
        json_path = os.path.join(os.getcwd(), "bot", "assets", "faq_answers.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get(faq_key)
    except Exception:
        pass
    return None


@router.message(F.text == "🤖 AI yordamchi")
async def btn_ai_assistant(message: Message, state: FSMContext):
    """AI yordamchi tugmasi."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "parent":
        return

    await message.answer(
        "🤖 <b>AI Yordamchi</b>\n\n"
        "Quyidagi ko'p beriladigan savollardan birini tanlang yoki "
        "o'zingiz xohlagan savolni yozing:\n",
        reply_markup=ai_faq_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("faq_"))
async def process_faq(callback: CallbackQuery, state: FSMContext):
    """FAQ tugmalari ushlagichi."""
    faq_key = callback.data

    if faq_key == "faq_custom":
        await state.set_state(AIStates.waiting_for_question)
        await callback.message.edit_text(
            "💬 <b>Savolingizni yozing</b>\n\n"
            "Internetda bolalar xavfsizligi haqida istalgan savolingizni yozing, "
            "AI javob beradi.",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    # Statik javobni olishga urinish
    static_answer = _get_static_answer(faq_key)
    if static_answer:
        await callback.message.edit_text(
            f"🤖 <b>AI Javob:</b>\n\n{static_answer}\n\n"
            f"<i>Yana savol bormi?</i>",
            reply_markup=ai_faq_kb(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    question = FAQ_TOPICS.get(faq_key)
    if not question:
        await callback.answer("Savol topilmadi.")
        return

    await callback.answer("⏳ Javob tayyorlanmoqda...")
    await callback.message.edit_text("⏳ <i>AI javob tayyorlamoqda...</i>", parse_mode="HTML")

    answer = await answer_parent_question(question)

    await callback.message.edit_text(
        f"🤖 <b>AI Javob:</b>\n\n{answer}\n\n"
        f"<i>Yana savol bormi?</i>",
        reply_markup=ai_faq_kb(),
        parse_mode="HTML"
    )


@router.message(AIStates.waiting_for_question, F.text)
async def process_custom_question(message: Message, state: FSMContext):
    """Erkin savolni qabul qilish va AI ga jo'natish."""
    await state.clear()

    wait_msg = await message.answer("⏳ <i>AI javob tayyorlamoqda...</i>", parse_mode="HTML")

    answer = await answer_parent_question(message.text)

    await wait_msg.edit_text(
        f"🤖 <b>AI Javob:</b>\n\n{answer}\n\n"
        f"<i>Yana savol bormi?</i>",
        reply_markup=ai_faq_kb(),
        parse_mode="HTML"
    )
