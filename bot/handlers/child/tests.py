"""
Qaramlik testi handleri.
/test — Mantiqiy savollar va AI orqali tahlil.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import crud
from bot.services.ai_analyzer import analyze_text_addiction

router = Router()

# ─── TEST SAVOLLARI (Mantiqiy) ──────────────────────────

LOGICAL_QUESTIONS = [
    "1️⃣ Tasavvur qiling, telefoningiz 1 kunga yo'qolib qoldi. O'sha kuni nima bilan shug'ullanardingiz va o'zingizni qanday his qilardingiz?",
    "2️⃣ Qiziqarli o'yin o'ynayapsiz yoki video ko'ryapsiz va shu payt ota-onangiz sizni ishga yordam berishga chaqirdi. Odatda qanday reaksiya qilasiz va nima qilasiz?",
    "3️⃣ Hozirgi kunda internetda siz uchun eng muhim va qiziqarli narsa nima? Agar u bo'lmasa hayotingiz qanday o'zgarardi?"
]

class TestStates(StatesGroup):
    taking_test = State()

def get_risk_report(risk_level: str, analysis: str) -> str:
    """Test natijasi xabarini yaratish."""
    risk_data = {
        "low": {"emoji": "🟢", "title": "Past xavf darajasi"},
        "medium": {"emoji": "🟡", "title": "O'rtacha xavf darajasi"},
        "high": {"emoji": "🔴", "title": "Yuqori xavf darajasi"}
    }
    data = risk_data.get(risk_level, risk_data["medium"])

    return (
        f"📊 <b>Test natijasi:</b>\n\n"
        f"{data['emoji']} <b>{data['title']}</b>\n\n"
        f"💬 <b>Psixolog (AI) xulosasi:</b>\n{analysis}"
    )

def get_parent_report(child_name: str, risk_level: str, analysis: str) -> str:
    """Ota-ona uchun test natijasi xabari."""
    risk_data = {
        "low": ("🟢", "Past"),
        "medium": ("🟡", "O'rtacha"),
        "high": ("🔴", "Yuqori"),
    }
    emoji, level_text = risk_data.get(risk_level, ("⚪", "Noma'lum"))

    return (
        f"📊 <b>Farzandingiz testi natijasi:</b>\n\n"
        f"👤 Farzand: <b>{child_name}</b>\n"
        f"{emoji} <b>{level_text} xavf darajasi</b>\n\n"
        f"💡 <b>Psixolog (AI) xulosasi:</b>\n{analysis}"
    )

@router.message(Command("test"))
async def cmd_test(message: Message, state: FSMContext):
    """/test — Qaramlik testini boshlash."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        await message.answer("⚠️ Bu buyruq faqat farzandlar uchun.")
        return

    # Testni boshlash
    await state.set_state(TestStates.taking_test)
    await state.update_data(current_question=0, answers=[])

    await message.answer(
        f"📝 <b>Mantiqiy test</b> (1/{len(LOGICAL_QUESTIONS)})\n\n"
        f"{LOGICAL_QUESTIONS[0]}\n\n"
        f"<i>Iltimos, o'z so'zlaringiz bilan batafsil javob yozing.</i>",
        parse_mode="HTML"
    )

@router.message(F.text == "📝 Test yechish")
async def btn_test(message: Message, state: FSMContext):
    """Test yechish tugmasi."""
    await cmd_test(message, state)

@router.message(TestStates.taking_test, F.text)
async def process_test_answer(message: Message, state: FSMContext):
    """Bolaning matnli javobini qabul qilish."""
    data = await state.get_data()
    current = data.get("current_question", 0)
    answers = data.get("answers", [])

    # Javobni qo'shish
    answers.append(message.text)
    next_q = current + 1

    if next_q < len(LOGICAL_QUESTIONS):
        # Keyingi savol
        await state.update_data(current_question=next_q, answers=answers)
        await message.answer(
            f"📝 <b>Mantiqiy test</b> ({next_q + 1}/{len(LOGICAL_QUESTIONS)})\n\n"
            f"{LOGICAL_QUESTIONS[next_q]}\n\n"
            f"<i>Iltimos, o'z so'zlaringiz bilan batafsil javob yozing.</i>",
            parse_mode="HTML"
        )
    else:
        # Test tugadi
        wait_msg = await message.answer("⏳ <i>Javoblaringiz sun'iy intellekt tomonidan tahlil qilinmoqda, kuting...</i>", parse_mode="HTML")
        
        # AI tahlili
        risk_level, analysis = await analyze_text_addiction(answers)
        
        # Risk ni int score ga o'tkazish (baza talabi)
        score_map = {"low": 0, "medium": 10, "high": 20}
        total_score = score_map.get(risk_level, 10)

        # Natijani saqlash
        await crud.save_test_result(
            message.from_user.id, "general_addiction", total_score, risk_level
        )

        # Farzandga natija
        report = get_risk_report(risk_level, analysis)
        await wait_msg.delete()
        await message.answer(report, parse_mode="HTML")

        # Ota-onaga xabar yuborish
        parent_id = await crud.get_parent_for_child(message.from_user.id)
        if parent_id:
            child_name = message.from_user.full_name or "Farzand"
            parent_report = get_parent_report(child_name, risk_level, analysis)
            try:
                await message.bot.send_message(parent_id, parent_report, parse_mode="HTML")
            except Exception:
                pass

        await state.clear()
