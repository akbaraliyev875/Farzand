"""
Hisobot handleri.
/report — Farzandning kunlik hisoboti.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database import crud
from bot.keyboards.parent_kb import children_list_kb
from bot.services.report_generator import generate_report_text

router = Router()


@router.message(Command("report"))
async def cmd_report(message: Message):
    """/report — Farzandlar ro'yxatini ko'rsatish va hisobot tanlash."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "parent":
        await message.answer("⚠️ Bu buyruq faqat ota-onalar uchun.")
        return

    children = await crud.get_children_for_parent(message.from_user.id)
    if not children:
        await message.answer(
            "📭 Hali farzand ulanmagan.\n\n"
            "🔗 Farzandni ulash uchun /link buyrug'ini yozing.",
            parse_mode="HTML"
        )
        return

    if len(children) == 1:
        # Bitta farzand — to'g'ridan-to'g'ri hisobot
        report = await generate_report_text(children[0].child_id)
        await message.answer(report, parse_mode="HTML")
    else:
        # Bir nechta farzand — tanlash
        await message.answer(
            "👶 Qaysi farzandning hisobotini ko'rmoqchisiz?",
            reply_markup=children_list_kb(children),
            parse_mode="HTML"
        )


@router.message(F.text == "📊 Hisobot")
async def btn_report(message: Message):
    """Hisobot tugmasi."""
    await cmd_report(message)


@router.callback_query(F.data.startswith("child_report_"))
async def on_child_report(callback: CallbackQuery):
    """Tanlangan farzand uchun hisobot."""
    child_id = int(callback.data.split("_")[-1])
    report = await generate_report_text(child_id)
    await callback.message.edit_text(report, parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "👤 Farzand profili")
async def btn_child_profile(message: Message):
    """Farzand profili tugmasi ota-ona uchun."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "parent":
        return

    children = await crud.get_children_for_parent(message.from_user.id)
    if not children:
        await message.answer("📭 Hali farzand ulanmagan.")
        return

    from bot.keyboards.parent_kb import children_profile_list_kb
    if len(children) == 1:
        child_id = children[0].child_id
        await send_child_profile_to_parent(message, child_id)
    else:
        await message.answer(
            "👶 Qaysi farzandning profilini ko'rmoqchisiz?",
            reply_markup=children_profile_list_kb(children),
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("child_profile_"))
async def on_child_profile(callback: CallbackQuery):
    """Tanlangan farzandning profilini ko'rsatish."""
    child_id = int(callback.data.split("_")[-1])
    await send_child_profile_to_parent(callback.message, child_id, is_edit=True)
    await callback.answer()


async def send_child_profile_to_parent(message: Message, child_id: int, is_edit: bool = False):
    profile = await crud.get_child_profile(child_id)
    
    text = f"👤 <b>Farzand #{child_id} Profili</b>\n\n"
    if profile:
        text += f"🎂 <b>Tug'ilgan kun:</b> {profile.birthday or 'Kiritilmagan'}\n"
        text += f"🌟 <b>Qobiliyatlari:</b> {profile.abilities or 'Kiritilmagan'}\n"
        text += f"🎯 <b>Maqsadlari:</b> {profile.goals or 'Kiritilmagan'}\n"
        text += f"✨ <b>Istaklari:</b> {profile.wishes or 'Kiritilmagan'}\n"
        text += f"📅 <b>Rejalari:</b> {profile.plans or 'Kiritilmagan'}\n"
    else:
        text += "Hali profil to'ldirilmagan."

    if is_edit:
        await message.edit_text(text, parse_mode="HTML")
    else:
        await message.answer(text, parse_mode="HTML")
