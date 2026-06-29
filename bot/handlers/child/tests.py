"""
Qaramlik testi handleri.
/test — 8 ta savollik test.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import crud
from bot.keyboards.child_kb import test_answer_kb

router = Router()


# ─── TEST SAVOLLARI ──────────────────────────────────────────

ADDICTION_TEST = [
    {
        "id": 1,
        "question": "📱 Kun davomida TikTok/YouTube ko'rishga qancha vaqt sarflaysiz?",
        "options": ["1 soatdan kam", "1-3 soat", "3-5 soat", "5 soatdan ko'p"],
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 2,
        "question": "📵 Telefonsiz 1 kun o'tkaza olasizmi?",
        "options": ["Osonlik bilan", "Qiyin, lekin mumkin", "Juda qiyin", "Mumkin emas"],
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 3,
        "question": "😴 Uxlashdan oldin telefon ishlatish vaqtingiz?",
        "options": ["Ishlatmayman", "15-30 daqiqa", "1-2 soat", "2 soatdan ko'p"],
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 4,
        "question": "📚 Dars/uy vazifasi paytida telefon ko'rasizmi?",
        "options": ["Hech qachon", "Kamdan-kam", "Tez-tez", "Doimiy ravishda"],
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 5,
        "question": "🎮 O'yinlardan ajrala olmay qolganmisiz?",
        "options": ["Hech qachon", "1-2 marta", "Ko'p marta", "Har doim"],
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 6,
        "question": "😠 Telefon olib qo'yilganda qanday his qilasiz?",
        "options": ["Normal", "Biroz noqulay", "Juda yomon", "G'azablanaman"],
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 7,
        "question": "👥 Do'stlaringiz bilan ko'proq qayerda muloqot qilasiz?",
        "options": [
            "Yuzma-yuz",
            "Teng darajada",
            "Ko'proq onlayn",
            "Faqat onlayn"
        ],
        "scores": [0, 1, 2, 3]
    },
    {
        "id": 8,
        "question": "🏃 Jismoniy faoliyat (sport, yurish) bilan kun davomida qancha shug'ullanasiz?",
        "options": ["1 soatdan ko'p", "30 daqiqa - 1 soat", "30 daqiqadan kam", "Deyarli yo'q"],
        "scores": [0, 1, 2, 3]
    },
]


class TestStates(StatesGroup):
    taking_test = State()


def calculate_risk(total_score: int) -> str:
    """Xavf darajasini hisoblash."""
    if total_score <= 5:
        return "low"
    elif total_score <= 12:
        return "medium"
    else:
        return "high"


def get_risk_report(score: int, risk_level: str) -> str:
    """Test natijasi xabarini yaratish."""
    risk_data = {
        "low": {
            "emoji": "🟢",
            "title": "Past xavf darajasi",
            "description": (
                "Ajoyib natija! Siz internetdan sog'lom foydalanayapsiz. "
                "Shu odatlaringizni davom ettiring! 👏"
            )
        },
        "medium": {
            "emoji": "🟡",
            "title": "O'rtacha xavf darajasi",
            "description": (
                "Ehtiyot bo'ling — ekran vaqtingiz biroz ko'paygan. "
                "Kun tartibini tuzib, jismoniy faoliyatni oshiring."
            )
        },
        "high": {
            "emoji": "🔴",
            "title": "Yuqori xavf darajasi",
            "description": (
                "Diqqat! Internet qaramlik belgilari mavjud. "
                "Ota-onangiz bilan gaplashib, birga reja tuzishingiz tavsiya etiladi."
            )
        }
    }

    data = risk_data.get(risk_level, risk_data["medium"])

    return (
        f"📊 <b>Test natijasi:</b>\n\n"
        f"{data['emoji']} <b>{data['title']}</b>\n\n"
        f"📈 Umumiy ball: <b>{score}</b>/24\n\n"
        f"💬 {data['description']}"
    )


def get_parent_report(child_name: str, score: int, risk_level: str) -> str:
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
        f"📈 Umumiy ball: <b>{score}</b>/24\n\n"
        f"💡 <b>Tavsiya:</b> "
        + (
            "Yaxshi natija! Farzandingizni rag'batlantiring."
            if risk_level == "low"
            else "Kun tartibini tuzib, ekran vaqtini cheklang. Jismoniy faoliyatni oshiring."
            if risk_level == "medium"
            else "Darhol chora ko'ring. Farzandingiz bilan ochiq suhbat quring va mutaxassisga murojaat qilishni o'ylang."
        )
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
    await state.update_data(current_question=0, scores=[])

    q = ADDICTION_TEST[0]
    await message.answer(
        f"📝 <b>Qaramlik testi</b> (1/{len(ADDICTION_TEST)})\n\n"
        f"{q['question']}",
        reply_markup=test_answer_kb(q["options"], q["id"]),
        parse_mode="HTML"
    )


@router.message(F.text == "📝 Test yechish")
async def btn_test(message: Message, state: FSMContext):
    """Test yechish tugmasi."""
    await cmd_test(message, state)


@router.callback_query(F.data.startswith("test_"))
async def on_test_answer(callback: CallbackQuery, state: FSMContext):
    """Test javobini qabul qilish."""
    parts = callback.data.split("_")
    question_id = int(parts[1])
    answer_idx = int(parts[2])

    data = await state.get_data()
    current = data.get("current_question", 0)
    scores = data.get("scores", [])

    # Ballni qo'shish
    q = ADDICTION_TEST[current]
    score = q["scores"][answer_idx]
    scores.append(score)

    next_q = current + 1

    if next_q < len(ADDICTION_TEST):
        # Keyingi savol
        await state.update_data(current_question=next_q, scores=scores)
        nq = ADDICTION_TEST[next_q]
        await callback.message.edit_text(
            f"📝 <b>Qaramlik testi</b> ({next_q + 1}/{len(ADDICTION_TEST)})\n\n"
            f"{nq['question']}",
            reply_markup=test_answer_kb(nq["options"], nq["id"]),
            parse_mode="HTML"
        )
    else:
        # Test tugadi
        total_score = sum(scores)
        risk_level = calculate_risk(total_score)

        # Natijani saqlash
        await crud.save_test_result(
            callback.from_user.id, "general_addiction", total_score, risk_level
        )

        # Farzandga natija
        report = get_risk_report(total_score, risk_level)
        await callback.message.edit_text(report, parse_mode="HTML")

        # Ota-onaga xabar yuborish
        parent_id = await crud.get_parent_for_child(callback.from_user.id)
        if parent_id:
            child_name = callback.from_user.full_name or "Farzand"
            parent_report = get_parent_report(child_name, total_score, risk_level)
            try:
                await callback.bot.send_message(parent_id, parent_report, parse_mode="HTML")
            except Exception:
                pass

        await state.clear()

    await callback.answer()
