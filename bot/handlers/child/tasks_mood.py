"""
Farzand vazifalar va kayfiyat handleri.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import crud

router = Router()


# ─── VAZIFALARIM ─────────────────────────────────────────

@router.message(F.text == "📋 Vazifalarim")
async def btn_my_tasks(message: Message):
    """Farzandning o'z vazifalarini ko'rsatish."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        return

    tasks = await crud.get_tasks_for_child(message.from_user.id)
    active = [t for t in tasks if t.status == "created"]
    pending = [t for t in tasks if t.status == "done"]
    approved = [t for t in tasks if t.status == "approved"]

    text = f"📋 <b>Vazifalarim</b>\n🏆 Jami ballarim: <b>{user.points or 0}</b>\n\n"

    if active:
        text += "🔵 <b>Faol vazifalar:</b>\n"
        for t in active:
            text += f"  • {t.title} ({t.points} ball)\n"
        text += "\n"

    if pending:
        text += "🟡 <b>Tasdiqlash kutilmoqda:</b>\n"
        for t in pending:
            text += f"  • {t.title} ({t.points} ball)\n"
        text += "\n"

    if approved[:5]:
        text += "✅ <b>Bajarilgan (oxirgi 5):</b>\n"
        for t in approved[:5]:
            text += f"  • {t.title} (+{t.points} ball)\n"
        text += "\n"

    if not tasks:
        text += "<i>Hozircha vazifa yo'q. Ota-onangiz sizga vazifa berishi mumkin.</i>"

    # Faol vazifalar uchun "Bajardim" tugmalari
    kb_btns = []
    for t in active:
        kb_btns.append([InlineKeyboardButton(
            text=f"✅ Bajardim: {t.title}",
            callback_data=f"task_done_{t.id}"
        )])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_btns) if kb_btns else None
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("task_done_"))
async def process_task_done(callback: CallbackQuery):
    """Farzand vazifani bajarganini e'lon qilish."""
    task_id = int(callback.data.split("_")[-1])
    task = await crud.get_task_by_id(task_id)

    if not task or task.status != "created":
        await callback.answer("⚠️ Vazifa topilmadi yoki allaqachon belgilangan.")
        return

    await crud.update_task_status(task_id, "done")

    await callback.message.edit_text(
        f"🟡 <b>Ajoyib!</b> Vazifa «{task.title}» bajargansiz deb belgilandi.\n\n"
        f"Endi ota-onangiz buni tasdiqlashi kerak. Tasdiqlanganidan so'ng <b>{task.points} ball</b> olasiz!",
        parse_mode="HTML"
    )

    # Ota-onaga xabar
    try:
        await callback.bot.send_message(
            task.parent_id,
            f"🔔 <b>Vazifa bajrildi!</b>\n\n"
            f"Farzandingiz «{task.title}» vazifasini bajarganini bildirdi.\n\n"
            f"📋 <b>Vazifalar</b> bo'limidan tasdiqlashingiz mumkin.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer("✅ Belgilandi!")


# ─── KAYFIYAT KUNDALIGI ─────────────────────────────────

MOOD_OPTIONS = {
    "mood_great": "😊 Ajoyib",
    "mood_good": "🙂 Yaxshi",
    "mood_normal": "😐 O'rtacha",
    "mood_sad": "😔 Ma'yus",
    "mood_angry": "😠 G'azabda",
}


@router.message(F.text == "🎭 Kayfiyatim")
async def btn_my_mood(message: Message):
    """Farzandning kayfiyat kundaligi."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        return

    # So'nggi kayfiyatlar
    moods = await crud.get_latest_moods(message.from_user.id, 7)

    text = "🎭 <b>Kayfiyat kundaligim</b>\n\n"
    if moods:
        text += "<b>So'nggi yozuvlarim:</b>\n"
        for m in reversed(moods):
            date_str = m.created_at.strftime("%d.%m %H:%M")
            text += f"  {date_str} — {m.mood}\n"
        text += "\n"

    text += "Bugun o'zingizni qanday his qilayapsiz?"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="😊", callback_data="mood_great"),
            InlineKeyboardButton(text="🙂", callback_data="mood_good"),
            InlineKeyboardButton(text="😐", callback_data="mood_normal"),
        ],
        [
            InlineKeyboardButton(text="😔", callback_data="mood_sad"),
            InlineKeyboardButton(text="😠", callback_data="mood_angry"),
        ]
    ])

    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("mood_"))
async def process_mood(callback: CallbackQuery):
    """Kayfiyatni saqlash."""
    mood_key = callback.data
    mood_text = MOOD_OPTIONS.get(mood_key, mood_key)

    await crud.log_mood(callback.from_user.id, mood_text)

    await callback.message.edit_text(
        f"✅ Kayfiyatingiz saqlandi: {mood_text}\n\n"
        f"<i>Har kuni o'z kayfiyatingizni belgilab boring! Bu ota-onangizga sizning ruhiy holatingizni tushunishda yordam beradi.</i>",
        parse_mode="HTML"
    )
    await callback.answer("✅ Saqlandi!")


# ─── KUNDALIK YUTUQLAR (GRATITUDE JOURNAL) ───────────────

class GratitudeStates(StatesGroup):
    entering_gratitude = State()

@router.message(F.text == "📖 Kundalik Yutuqlar")
async def btn_my_gratitude(message: Message, state: FSMContext):
    """Kundalik yutuqlarni yozish."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        return

    logs = await crud.get_gratitude_logs(message.from_user.id, 3)
    text = "📖 <b>Kundalik Yutuqlarim (Gratitude Journal)</b>\n\n"
    
    if logs:
        text += "<i>So'nggi yozuvlaringiz:</i>\n"
        for log in reversed(logs):
            date_str = log.created_at.strftime("%d.%m")
            text += f"🔹 {date_str}: {log.text}\n"
        text += "\n"

    text += (
        "<b>Bugun nimalardan xursand bo'ldingiz?</b> Kimgadir yordam berdingizmi "
        "yoki qandaydir yangi narsa o'rgandingizmi?\n\n"
        "<i>Fikrlaringizni shu yerga yozing:</i> (Bekor qilish uchun /cancel)"
    )

    await state.set_state(GratitudeStates.entering_gratitude)
    await message.answer(text, parse_mode="HTML")

@router.message(GratitudeStates.entering_gratitude, F.text)
async def process_gratitude_text(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Bekor qilindi.")
        return
        
    await crud.add_gratitude_log(message.from_user.id, message.text)
    await state.clear()
    
    # Kichik rag'bat
    await crud.update_user_points(message.from_user.id, 1)
    
    await message.answer(
        "🌟 <b>Ajoyib!</b> Yozuvingiz saqlandi.\n\n"
        "Har kuni o'z yutuqlaringizni yozib borish sizni yanada ijobiy inson bo'lishingizga yordam beradi!\n"
        "<i>(+1 ball oldingiz)</i>",
        parse_mode="HTML"
    )
