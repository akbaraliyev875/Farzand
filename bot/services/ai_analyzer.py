"""
AI kontent tahlili — OpenAI GPT-4o orqali skrinshot tahlili.
Agar OpenAI API key bo'lmasa, oddiy "unknown" qaytaradi.
"""

import base64
import logging
from io import BytesIO

from aiogram import Bot
from aiogram.types import PhotoSize

from bot.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)


async def analyze_screenshot(bot: Bot, photo: PhotoSize) -> str:
    """
    Skrinshotni AI orqali tahlil qilish.
    Qaytaradi: 'safe', 'violence', 'adult', 'gambling', 'unknown'
    """
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY sozlanmagan. Tahlil o'tkazib yuborildi.")
        return "unknown"

    try:
        # Rasmni yuklab olish
        file = await bot.get_file(photo.file_id)
        file_bytes = BytesIO()
        await bot.download_file(file.file_path, file_bytes)
        file_bytes.seek(0)

        # Base64 ga o'tkazish
        base64_image = base64.b64encode(file_bytes.read()).decode("utf-8")

        # OpenAI API ga so'rov
        import openai
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": (
                                "Bu rasmni tahlil qil va quyidagi kategoriyalardan "
                                "faqat BIRINI qaytara:\n"
                                "SAFE | VIOLENCE | ADULT | GAMBLING | UNKNOWN\n"
                                "Faqat kategoriya nomini yoz, boshqa narsa emas."
                            )
                        }
                    ]
                }
            ],
            max_tokens=10
        )

        result = response.choices[0].message.content.strip().lower()

        # Natijani normalizatsiya
        valid = {"safe", "violence", "adult", "gambling", "unknown"}
        if result not in valid:
            return "unknown"
        return result

    except Exception as e:
        logger.error(f"AI tahlil xatosi: {e}")
        return "unknown"
