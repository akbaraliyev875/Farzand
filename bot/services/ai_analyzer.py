"""
AI kontent tahlili — Google Gemini orqali skrinshot tahlili.
Agar Gemini API key bo'lmasa, oddiy "unknown" qaytaradi.
"""

import logging
from io import BytesIO

from aiogram import Bot
from aiogram.types import PhotoSize
from google import genai
from google.genai import types

from bot.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


async def analyze_screenshot(bot: Bot, photo: PhotoSize) -> str:
    """
    Skrinshotni AI orqali tahlil qilish.
    Qaytaradi: 'safe', 'violence', 'adult', 'gambling', 'unknown'
    """
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY sozlanmagan. Tahlil o'tkazib yuborildi.")
        return "unknown"

    try:
        # Rasmni yuklab olish
        file = await bot.get_file(photo.file_id)
        file_bytes = BytesIO()
        await bot.download_file(file.file_path, file_bytes)
        image_data = file_bytes.getvalue()

        # Gemini API ga so'rov
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = (
            "Bu rasmni tahlil qil va quyidagi kategoriyalardan "
            "faqat BIRINI qaytara:\n"
            "SAFE | VIOLENCE | ADULT | GAMBLING | UNKNOWN\n"
            "Faqat kategoriya nomini yoz, boshqa narsa emas."
        )

        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=image_data,
                    mime_type='image/jpeg',
                ),
                prompt,
            ]
        )

        result = response.text.strip().lower()

        # Natijani normalizatsiya
        valid = {"safe", "violence", "adult", "gambling", "unknown"}
        if result not in valid:
            return "unknown"
        return result

    except Exception as e:
        logger.error(f"AI tahlil xatosi: {e}")
        return "unknown"
