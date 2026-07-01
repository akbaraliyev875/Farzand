"""
Farzand profili handleri.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import crud
from bot.keyboards.child_kb import child_profile_kb

router = Router()

class ProfileStates(StatesGroup):
    waiting_for_birthday = State()
    waiting_for_abilities = State()
    waiting_for_goals = State()
    waiting_for_wishes = State()
    waiting_for_plans = State()


@router.message(F.text == "👤 Mening profilim")
async def show_profile(message: Message, state: FSMContext):
    """Farzand profilini ko'rsatish."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        return

    profile = await crud.get_child_profile(message.from_user.id)
    
    text = f"👤 <b>Mening profilim</b>\n🏆 <b>To'plagan ballarim:</b> {user.points or 0}\n\n"
    if profile:
        text += f"🎂 <b>Tug'ilgan kun:</b> {profile.birthday or 'Kiritilmagan'}\n"
        text += f"🌟 <b>Qobiliyatlarim:</b> {profile.abilities or 'Kiritilmagan'}\n"
        text += f"🎯 <b>Maqsadlarim:</b> {profile.goals or 'Kiritilmagan'}\n"
        text += f"✨ <b>Istaklarim:</b> {profile.wishes or 'Kiritilmagan'}\n"
        text += f"📅 <b>Rejalarim:</b> {profile.plans or 'Kiritilmagan'}\n"
    else:
        text += "Hali profil to'ldirilmagan. Iltimos, ma'lumotlaringizni kiriting!"

    await message.answer(text, reply_markup=child_profile_kb(), parse_mode="HTML")


@router.callback_query(F.data.startswith("edit_"))
async def process_edit_profile(callback: CallbackQuery, state: FSMContext):
    """Profilni tahrirlash tugmalari ushlagichi."""
    action = callback.data.split("_")[1]
    
    prompts = {
        "birthday": ("Tug'ilgan kuningizni kiriting (masalan: 15.05.2010):", ProfileStates.waiting_for_birthday),
        "abilities": ("O'zingizdagi eng yaxshi qobiliyat va qiziqishlaringiz nima? Nimalarga qiziqasiz? (masalan: rasm chizish, dasturlash...):", ProfileStates.waiting_for_abilities),
        "goals": ("Kelajakdagi maqsadlaringiz nima? Kim bo'lmoqchisiz?", ProfileStates.waiting_for_goals),
        "wishes": ("Hozirgi vaqtdagi eng katta istaklaringiz nima? Nima xohlaysiz?", ProfileStates.waiting_for_wishes),
        "plans": ("Yaqin kunlar yoki kelajak uchun qanday rejalaringiz bor?", ProfileStates.waiting_for_plans)
    }
    
    if action in prompts:
        text, next_state = prompts[action]
        await state.set_state(next_state)
        await callback.message.edit_text(f"✍️ {text}")
    
    await callback.answer()


@router.message(ProfileStates.waiting_for_birthday, F.text)
async def process_birthday(message: Message, state: FSMContext):
    await crud.update_child_profile(message.from_user.id, birthday=message.text)
    await state.clear()
    await message.answer("✅ Tug'ilgan kuningiz saqlandi!")
    await show_profile(message, state)


@router.message(ProfileStates.waiting_for_abilities, F.text)
async def process_abilities(message: Message, state: FSMContext):
    await crud.update_child_profile(message.from_user.id, abilities=message.text)
    await state.clear()
    await message.answer("✅ Qobiliyatlaringiz saqlandi!")
    await show_profile(message, state)


@router.message(ProfileStates.waiting_for_goals, F.text)
async def process_goals(message: Message, state: FSMContext):
    await crud.update_child_profile(message.from_user.id, goals=message.text)
    await state.clear()
    await message.answer("✅ Maqsadlaringiz saqlandi!")
    await show_profile(message, state)


@router.message(ProfileStates.waiting_for_wishes, F.text)
async def process_wishes(message: Message, state: FSMContext):
    await crud.update_child_profile(message.from_user.id, wishes=message.text)
    await state.clear()
    await message.answer("✅ Istaklaringiz saqlandi!")
    await show_profile(message, state)


@router.message(ProfileStates.waiting_for_plans, F.text)
async def process_plans(message: Message, state: FSMContext):
    await crud.update_child_profile(message.from_user.id, plans=message.text)
    await state.clear()
    await message.answer("✅ Rejalaringiz saqlandi!")
    await show_profile(message, state)
