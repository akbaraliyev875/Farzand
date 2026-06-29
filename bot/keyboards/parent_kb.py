"""
Ota-ona uchun klaviaturalar (keyboards).
"""

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


def role_selection_kb() -> InlineKeyboardMarkup:
    """Rolni tanlash (ota-ona / farzand)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👨‍👩‍👧 Ota-ona sifatida", callback_data="role_parent"),
        ],
        [
            InlineKeyboardButton(text="🧒 Farzand sifatida", callback_data="role_child"),
        ]
    ])


def parent_main_kb() -> ReplyKeyboardMarkup:
    """Ota-ona asosiy menyusi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Hisobot"),
                KeyboardButton(text="🔗 Farzand ulash"),
            ],
            [
                KeyboardButton(text="🔍 Kontent tekshirish"),
                KeyboardButton(text="💡 Bugungi maslahat"),
            ],
            [
                KeyboardButton(text="⚙️ Sozlamalar"),
                KeyboardButton(text="❓ Yordam"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Menyudan tanlang..."
    )


def confirm_kb() -> InlineKeyboardMarkup:
    """Tasdiqlash tugmalari."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="confirm_no"),
        ]
    ])


def back_to_menu_kb() -> InlineKeyboardMarkup:
    """Asosiy menyuga qaytish."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_menu")]
    ])


def children_list_kb(children: list) -> InlineKeyboardMarkup:
    """Farzandlar ro'yxati (hisobot uchun)."""
    buttons = []
    for link in children:
        name = f"Farzand #{link.child_id}"
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {name}",
                callback_data=f"child_report_{link.child_id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
