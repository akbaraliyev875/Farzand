"""
Farzand uchun klaviaturalar (keyboards).
"""

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


def child_main_kb() -> ReplyKeyboardMarkup:
    """Farzand asosiy menyusi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Test yechish"),
                KeyboardButton(text="📚 O'quv materiallar"),
            ],
            [
                KeyboardButton(text="📋 Vazifalarim"),
                KeyboardButton(text="⏱️ Pomodoro"),
            ],
            [
                KeyboardButton(text="🎭 Kayfiyatim"),
                KeyboardButton(text="👤 Mening profilim"),
            ],
            [
                KeyboardButton(text="📊 Mening statistikam"),
                KeyboardButton(text="🎭 Hayotiy Vaziyat"),
            ],
            [
                KeyboardButton(text="📖 Kundalik Yutuqlar"),
                KeyboardButton(text="❓ Yordam"),
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Menyudan tanlang..."
    )


def test_answer_kb(options: list, question_id: int) -> InlineKeyboardMarkup:
    """Test savoli uchun javob variantlari."""
    buttons = []
    for i, option in enumerate(options):
        buttons.append([
            InlineKeyboardButton(
                text=option,
                callback_data=f"test_{question_id}_{i}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def connect_kb() -> InlineKeyboardMarkup:
    """Ota-onaga ulanish tugmasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Ota-onaga ulanish", callback_data="connect_parent")]
    ])


def guide_pagination_kb(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """O'quv qo'llanmalari uchun sahifalash klaviaturasi."""
    buttons = []
    
    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Oldingisi", callback_data=f"guide_prev_{current_page}"))
    
    buttons.append(InlineKeyboardButton(text=f"{current_page + 1}/{total_pages}", callback_data="ignore"))
    
    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton(text="Keyingisi ➡️", callback_data=f"guide_next_{current_page}"))
        
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def child_profile_kb() -> InlineKeyboardMarkup:
    """Farzand profilini tahrirlash klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎂 Tug'ilgan kunni kiritish", callback_data="edit_birthday")],
        [InlineKeyboardButton(text="🌟 Qobiliyatlarim", callback_data="edit_abilities")],
        [InlineKeyboardButton(text="🎯 Maqsadlarim", callback_data="edit_goals")],
        [InlineKeyboardButton(text="✨ Istaklarim", callback_data="edit_wishes")],
        [InlineKeyboardButton(text="📅 Rejalarim", callback_data="edit_plans")]
    ])
