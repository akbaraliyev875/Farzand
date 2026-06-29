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
                KeyboardButton(text="📊 Mening statistikam"),
                KeyboardButton(text="❓ Yordam"),
            ],
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
