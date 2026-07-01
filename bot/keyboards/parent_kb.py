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
                KeyboardButton(text="👤 Farzand profili"),
                KeyboardButton(text="📋 Vazifalar"),
            ],
            [
                KeyboardButton(text="🤖 AI yordamchi"),
                KeyboardButton(text="🎭 Farzand kayfiyati"),
            ],
            [
                KeyboardButton(text="⭐️ Xulq-atvor"),
                KeyboardButton(text="📖 Farzand yutuqlari"),
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


def children_profile_list_kb(children: list) -> InlineKeyboardMarkup:
    """Farzandlar ro'yxati (profil uchun)."""
    buttons = []
    for link in children:
        name = f"Farzand #{link.child_id}"
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {name}",
                callback_data=f"child_profile_{link.child_id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def ai_faq_kb() -> InlineKeyboardMarkup:
    """AI yordamchi - ko'p beriladigan savollar."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎣 Fishing (phishing) nima?", callback_data="faq_fishing")],
        [InlineKeyboardButton(text="👥 Onlayn bulling nima?", callback_data="faq_bulling")],
        [InlineKeyboardButton(text="📱 Ekran qaramligi nima?", callback_data="faq_addiction")],
        [InlineKeyboardButton(text="🔐 Bolaga xavfsiz parol qanday o'rgatiladi?", callback_data="faq_password")],
        [InlineKeyboardButton(text="🛡️ Bolani internetda qanday himoya qilaman?", callback_data="faq_protection")],
        [InlineKeyboardButton(text="🎮 O'yin qaramligi belgilari qanday?", callback_data="faq_gaming")],
        [InlineKeyboardButton(text="💬 Boshqa savol berish", callback_data="faq_custom")]
    ])
