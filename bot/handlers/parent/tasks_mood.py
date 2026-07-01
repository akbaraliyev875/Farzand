"""
Ota-ona vazifalar va kayfiyat handleri.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import crud

router = Router()


class TaskCreateStates(StatesGroup):
    choosing_child = State()
    entering_title = State()
    entering_points = State()


# ─── VAZIFALAR ───────────────────────────────────────────

@router.message(F.text == "📋 Vazifalar")
async def btn_tasks(message: Message, state: FSMContext):
    """Ota-ona vazifalar bo'limi."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "parent":
        return

    children = await crud.get_children_for_parent(message.from_user.id)
    if not children:
        await message.answer("📭 Hali farzand ulanmagan.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    # Vazifalar ro'yxati
    tasks = await crud.get_tasks_for_parent(message.from_user.id)
    active_tasks = [t for t in tasks if t.status in ("created", "done")]

    text = "📋 <b>Vazifalar</b>\n\n"
    if active_tasks:
        for t in active_tasks:
            status_emoji = {"created": "🔵", "done": "🟡", "approved": "✅"}.get(t.status, "⚪")
            text += f"{status_emoji} {t.title} ({t.points} ball) — #{t.id}\n"
    else:
        text += "<i>Hozircha faol vazifa yo'q.</i>\n"

    # Tasdiqlash kutayotgan vazifalar
    pending = [t for t in tasks if t.status == "done"]
    if pending:
        text += f"\n🟡 <b>Tasdiqlash kutayotgan: {len(pending)} ta</b>"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yangi vazifa qo'shish", callback_data="task_new")],
    ])

    # Tasdiqlash tugmalari
    for t in pending:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text=f"✅ Tasdiqlash: {t.title}", callback_data=f"task_approve_{t.id}")
        ])

    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "task_new")
async def process_task_new(callback: CallbackQuery, state: FSMContext):
    """Yangi vazifa yaratish boshlash."""
    children = await crud.get_children_for_parent(callback.from_user.id)

    if len(children) == 1:
        await state.update_data(child_id=children[0].child_id)
        await state.set_state(TaskCreateStates.entering_title)
        await callback.message.edit_text("✍️ Vazifa nomini yozing (masalan: Dars tayyorlash):")
    else:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        btns = []
        for c in children:
            btns.append([InlineKeyboardButton(
                text=f"👤 Farzand #{c.child_id}",
                callback_data=f"task_child_{c.child_id}"
            )])
        await state.set_state(TaskCreateStates.choosing_child)
        await callback.message.edit_text(
            "👶 Qaysi farzandga vazifa berasiz?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=btns)
        )
    await callback.answer()


@router.callback_query(TaskCreateStates.choosing_child, F.data.startswith("task_child_"))
async def process_task_child(callback: CallbackQuery, state: FSMContext):
    child_id = int(callback.data.split("_")[-1])
    await state.update_data(child_id=child_id)
    await state.set_state(TaskCreateStates.entering_title)
    await callback.message.edit_text("✍️ Vazifa nomini yozing (masalan: Dars tayyorlash):")
    await callback.answer()


@router.message(TaskCreateStates.entering_title, F.text)
async def process_task_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(TaskCreateStates.entering_points)
    await message.answer("🏆 Vazifa uchun mukofot ballini kiriting (masalan: 10):")


@router.message(TaskCreateStates.entering_points, F.text)
async def process_task_points(message: Message, state: FSMContext):
    try:
        points = int(message.text)
    except ValueError:
        await message.answer("⚠️ Iltimos, raqam kiriting (masalan: 10):")
        return

    data = await state.get_data()
    child_id = data["child_id"]
    title = data["title"]
    await state.clear()

    task = await crud.create_task(message.from_user.id, child_id, title, points)

    await message.answer(
        f"✅ Vazifa yaratildi!\n\n"
        f"📋 <b>{title}</b>\n"
        f"🏆 Mukofot: <b>{points} ball</b>\n"
        f"👶 Farzand: #{child_id}",
        parse_mode="HTML"
    )

    # Farzandga xabar yuborish
    try:
        await message.bot.send_message(
            child_id,
            f"📋 <b>Yangi vazifa!</b>\n\n"
            f"{title}\n"
            f"🏆 Mukofot: <b>{points} ball</b>\n\n"
            f"Vazifani bajargach, <b>📋 Vazifalarim</b> tugmasini bosib tasdiqlang!",
            parse_mode="HTML"
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("task_approve_"))
async def process_task_approve(callback: CallbackQuery):
    """Vazifani tasdiqlash."""
    task_id = int(callback.data.split("_")[-1])
    task = await crud.get_task_by_id(task_id)

    if not task or task.status != "done":
        await callback.answer("⚠️ Vazifa topilmadi yoki allaqachon tasdiqlangan.")
        return

    await crud.update_task_status(task_id, "approved")
    await crud.update_user_points(task.child_id, task.points)

    await callback.message.edit_text(
        f"✅ Tasdiqlandi!\n\n"
        f"📋 {task.title}\n"
        f"🏆 Farzandga <b>{task.points} ball</b> berildi!",
        parse_mode="HTML"
    )

    # Farzandga xabar
    try:
        await callback.bot.send_message(
            task.child_id,
            f"🎉 <b>Ajoyib!</b>\n\n"
            f"Vazifa «{task.title}» tasdiqlandi!\n"
            f"🏆 Sizga <b>{task.points} ball</b> berildi!",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer("✅ Tasdiqlandi!")


# ─── FARZAND KAYFIYATI (OTA-ONA TOMONI) ─────────────────

@router.message(F.text == "🎭 Farzand kayfiyati")
async def btn_child_mood(message: Message):
    """Farzandning kayfiyat tarixini ko'rsatish."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "parent":
        return

    children = await crud.get_children_for_parent(message.from_user.id)
    if not children:
        await message.answer("📭 Hali farzand ulanmagan.")
        return

    text = "🎭 <b>Farzand kayfiyatlari (so'nggi 7 kun)</b>\n\n"
    for link in children:
        moods = await crud.get_latest_moods(link.child_id, 7)
        text += f"👤 <b>Farzand #{link.child_id}:</b>\n"
        if moods:
            for m in reversed(moods):
                date_str = m.created_at.strftime("%d.%m")
                text += f"  {date_str} — {m.mood}\n"
        else:
            text += "  <i>Hali kayfiyat belgilanmagan</i>\n"
        text += "\n"

    await message.answer(text, parse_mode="HTML")


# ─── XULQ-ATVOR REYTINGI ────────────────────────────────

class BehaviorStates(StatesGroup):
    choosing_child = State()
    entering_stars = State()
    entering_reason = State()

@router.message(F.text == "⭐️ Xulq-atvor")
async def btn_behavior(message: Message, state: FSMContext):
    """Xulq-atvor baholash boshlash."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "parent":
        return

    children = await crud.get_children_for_parent(message.from_user.id)
    if not children:
        await message.answer("📭 Hali farzand ulanmagan.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    if len(children) == 1:
        await state.update_data(child_id=children[0].child_id)
        await state.set_state(BehaviorStates.entering_stars)
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ 1", callback_data="star_1"),
             InlineKeyboardButton(text="⭐⭐ 2", callback_data="star_2"),
             InlineKeyboardButton(text="⭐⭐⭐ 3", callback_data="star_3")],
            [InlineKeyboardButton(text="⭐⭐⭐⭐ 4", callback_data="star_4"),
             InlineKeyboardButton(text="⭐⭐⭐⭐⭐ 5", callback_data="star_5")]
        ])
        await message.answer("Farzandingizning bugungi xulq-atvorini baholang (1-5 yulduz):", reply_markup=kb)
    else:
        btns = []
        for c in children:
            btns.append([InlineKeyboardButton(text=f"👤 Farzand #{c.child_id}", callback_data=f"beh_child_{c.child_id}")])
        await state.set_state(BehaviorStates.choosing_child)
        await message.answer("Qaysi farzandni baholaysiz?", reply_markup=InlineKeyboardMarkup(inline_keyboard=btns))

@router.callback_query(BehaviorStates.choosing_child, F.data.startswith("beh_child_"))
async def process_beh_child(callback: CallbackQuery, state: FSMContext):
    child_id = int(callback.data.split("_")[-1])
    await state.update_data(child_id=child_id)
    await state.set_state(BehaviorStates.entering_stars)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 1", callback_data="star_1"),
         InlineKeyboardButton(text="⭐⭐ 2", callback_data="star_2"),
         InlineKeyboardButton(text="⭐⭐⭐ 3", callback_data="star_3")],
        [InlineKeyboardButton(text="⭐⭐⭐⭐ 4", callback_data="star_4"),
         InlineKeyboardButton(text="⭐⭐⭐⭐⭐ 5", callback_data="star_5")]
    ])
    await callback.message.edit_text("Farzandingizning bugungi xulq-atvorini baholang (1-5 yulduz):", reply_markup=kb)
    await callback.answer()

@router.callback_query(BehaviorStates.entering_stars, F.data.startswith("star_"))
async def process_beh_stars(callback: CallbackQuery, state: FSMContext):
    stars = int(callback.data.split("_")[1])
    await state.update_data(stars=stars)
    await state.set_state(BehaviorStates.entering_reason)
    await callback.message.edit_text(f"{stars} yulduzcha tanladingiz!\n\nIltimos, sababini yozib yuboring (masalan: 'Bugun ukasiga juda mehribon bo'ldi'):")
    await callback.answer()

@router.message(BehaviorStates.entering_reason, F.text)
async def process_beh_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    child_id = data["child_id"]
    stars = data["stars"]
    reason = message.text
    
    await state.clear()
    
    await crud.add_behavior_log(child_id, message.from_user.id, stars, reason)
    
    # Give points (e.g. 2 points per star)
    points_reward = stars * 2
    await crud.update_user_points(child_id, points_reward)
    
    await message.answer(f"✅ Baholandi! Farzandga +{points_reward} ball berildi.")
    
    try:
        await message.bot.send_message(
            child_id,
            f"⭐️ <b>Sizga yulduzcha berildi!</b>\n\n"
            f"Ota-onangiz bugungi xulq-atvoringizni <b>{stars}/5</b> baholadi.\n"
            f"📝 Izoh: <i>{reason}</i>\n\n"
            f"Sizga <b>+{points_reward} ball</b> qo'shildi!",
            parse_mode="HTML"
        )
    except Exception:
        pass


# ─── FARZAND YUTUQLARI (GRATITUDE) ──────────────────────

@router.message(F.text == "📖 Farzand yutuqlari")
async def btn_child_gratitude(message: Message):
    """Farzandning gratitude jurnalini ko'rish."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "parent":
        return

    children = await crud.get_children_for_parent(message.from_user.id)
    if not children:
        await message.answer("📭 Hali farzand ulanmagan.")
        return

    text = "📖 <b>Farzandning so'nggi yutuqlari va quvonchlari</b>\n\n"
    for link in children:
        logs = await crud.get_gratitude_logs(link.child_id, 5)
        text += f"👤 <b>Farzand #{link.child_id}:</b>\n"
        if logs:
            for log in reversed(logs):
                date_str = log.created_at.strftime("%d.%m %H:%M")
                text += f"  🔹 {date_str}: <i>{log.text}</i>\n"
        else:
            text += "  <i>Hali yutuqlar yozilmagan</i>\n"
        text += "\n"

    await message.answer(text, parse_mode="HTML")
