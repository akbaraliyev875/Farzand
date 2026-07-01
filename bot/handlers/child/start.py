"""
Farzand start handleri.
Farzand uchun /start va asosiy interaksiyalar.
"""

import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import crud
from bot.keyboards.child_kb import child_main_kb, connect_kb, guide_pagination_kb
from bot.services.ai_analyzer import generate_dynamic_guide

router = Router()

class GuideStates(StatesGroup):
    viewing_guide = State()

@router.message(F.text == "📚 O'quv materiallar")
async def btn_learn(message: Message, state: FSMContext):
    """O'quv materiallar — dinamik generatsiya qilinadi."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        return

    wait_msg = await message.answer("⏳ <i>Qiziqarli qo'llanma tayyorlanmoqda, kuting...</i>", parse_mode="HTML")
    
    guide_data = await generate_dynamic_guide()
    if not guide_data:
        await wait_msg.edit_text("⚠️ Xatolik yuz berdi yoki API ishlamayapti.")
        return

    await state.set_state(GuideStates.viewing_guide)
    await state.update_data(guide=guide_data, current_page=0)

    page = guide_data[0]
    image_name = page.get("image", "online_learning")
    # Fallback agar noto'g'ri nom berilsa
    valid_images = ["time_management", "cyber_security", "online_learning", "cyber_bullying"]
    if image_name not in valid_images:
        image_name = "online_learning"
        
    photo_path = os.path.join(os.getcwd(), "bot", "assets", f"{image_name}.png")
    
    # Rasmni topmasa text o'zini yuborish uchun
    content_text = page['content'].replace('<br>', '\n').replace('<br/>', '\n').replace('</br>', '\n')
    try:
        photo = FSInputFile(photo_path)
        await message.answer_photo(
            photo=photo,
            caption=f"<b>{page['title']}</b>\n\n{content_text}",
            parse_mode="HTML",
            reply_markup=guide_pagination_kb(0, len(guide_data))
        )
    except Exception:
        await message.answer(
            f"<b>{page['title']}</b>\n\n{content_text}",
            parse_mode="HTML",
            reply_markup=guide_pagination_kb(0, len(guide_data))
        )
        
    await wait_msg.delete()


@router.callback_query(F.data.startswith("guide_"))
async def process_guide_pagination(callback: CallbackQuery, state: FSMContext):
    """Qo'llanmani varaqlash."""
    if callback.data == "guide_ignore":
        await callback.answer()
        return

    data = await state.get_data()
    guide_data = data.get("guide", [])
    if not guide_data:
        await callback.answer("⏳ Vaqt tugadi, menyudan qaytadan tanlang.", show_alert=True)
        return

    action, page_str = callback.data.split("_")[1], callback.data.split("_")[2]
    current_page = int(page_str)

    if action == "prev":
        new_page_idx = current_page - 1
    elif action == "next":
        new_page_idx = current_page + 1
    else:
        new_page_idx = current_page

    if 0 <= new_page_idx < len(guide_data):
        page = guide_data[new_page_idx]
        image_name = page.get("image", "online_learning")
        
        valid_images = ["time_management", "cyber_security", "online_learning", "cyber_bullying"]
        if image_name not in valid_images:
            image_name = "online_learning"
            
        photo_path = os.path.join(os.getcwd(), "bot", "assets", f"{image_name}.png")
        
        await state.update_data(current_page=new_page_idx)
        content_text = page['content'].replace('<br>', '\n').replace('<br/>', '\n').replace('</br>', '\n')
        try:
            photo = FSInputFile(photo_path)
            media = InputMediaPhoto(
                media=photo,
                caption=f"<b>{page['title']}</b>\n\n{content_text}",
                parse_mode="HTML"
            )
            await callback.message.edit_media(
                media=media,
                reply_markup=guide_pagination_kb(new_page_idx, len(guide_data))
            )
        except Exception:
            await callback.message.edit_text(
                text=f"<b>{page['title']}</b>\n\n{content_text}",
                parse_mode="HTML",
                reply_markup=guide_pagination_kb(new_page_idx, len(guide_data))
            )
    
    await callback.answer()


@router.message(F.text == "📊 Mening statistikam")
async def btn_my_stats(message: Message):
    """Farzandning o'z statistikasi."""
    user = await crud.get_user(message.from_user.id)
    if not user or user.role != "child":
        return

    # Kunlik faollik
    daily_min = await crud.get_daily_activity(message.from_user.id)
    hours = daily_min // 60
    mins = daily_min % 60

    # Oxirgi test
    last_test = await crud.get_latest_test(message.from_user.id)
    test_info = "📝 Hali test yechilmagan"
    if last_test:
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        risk_text = {"low": "Past", "medium": "O'rtacha", "high": "Yuqori"}
        test_info = (
            f"📝 Oxirgi test: {risk_emoji.get(last_test.risk_level, '⚪')} "
            f"{risk_text.get(last_test.risk_level, 'Noma\'lum')} xavf darajasi\n"
            f"   Ball: {last_test.score}"
        )

    await message.answer(
        f"📊 <b>Mening statistikam</b>\n\n"
        f"📱 Bugungi ekran vaqti: <b>{hours} soat {mins} daqiqa</b>\n\n"
        f"{test_info}\n\n"
        f"💡 Ekran vaqtini kamaytirib, kitob o'qing! 📚",
        parse_mode="HTML"
    )
