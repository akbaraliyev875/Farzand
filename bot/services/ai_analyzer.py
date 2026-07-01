"""
AI kontent tahlili — Google Gemini orqali skrinshot tahlili.
Agar Gemini API key bo'lmasa, oddiy "unknown" qaytaradi.
"""

import logging
from io import BytesIO
import json

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


async def analyze_text_addiction(answers: list[str]) -> tuple[str, str]:
    """
    Bolaning yozma javoblarini Gemini orqali tahlil qilish.
    Qaytaradi: (risk_level, analysis_text)
    risk_level: 'low', 'medium', 'high'
    """
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY sozlanmagan. Tahlil o'tkazib yuborildi.")
        return "unknown", "AI xizmati hozircha ishlamayapti."

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        answers_text = "\n".join([f"{i+1}. {ans}" for i, ans in enumerate(answers)])

        prompt = (
            "Sen bolalar psixologisan. Quyida bolaning telefonga qaramligini tekshirish uchun "
            "berilgan mantiqiy savollarga uning javoblari keltirilgan:\n\n"
            f"{answers_text}\n\n"
            "Shu javoblarga qarab, bolaning internetga/telefonga qaramlik darajasini bahola. "
            "Javobing qat'iy ravishda quyidagi JSON formatida bo'lsin:\n"
            "{\n"
            '  "risk_level": "low" yoki "medium" yoki "high",\n'
            '  "analysis": "Bolaning holati haqida sening professional, tushunarli va qisqacha (3-4 gap) fikring hamda tavsiyang (O\'zbek tilida)."\n'
            "}\n"
            "Faqat JSON qaytar, boshqa izoh yozma."
        )

        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        text = response.text.strip()
        
        # Markdown kod bloklarini tozalash
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        risk = data.get("risk_level", "medium")
        analysis = data.get("analysis", "Tahlil qilib bo'lmadi.")

        if risk not in ("low", "medium", "high"):
            risk = "medium"

        return risk, analysis

    except Exception as e:
        logger.error(f"AI matn tahlil xatosi: {e}")
        return "unknown", "AI xizmatida xatolik yuz berdi."


async def generate_dynamic_guide() -> list[dict]:
    """
    Gemini yordamida bolalar uchun tasodifiy o'quv materialini shakllantirish.
    Qaytaradi: [{'title': '...', 'content': '...', 'image': '...'}, ...]
    image: 'time_management', 'cyber_security', 'online_learning', yoki 'cyber_bullying'
    """
    if not GEMINI_API_KEY:
        return []

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = (
            "Sen bolalar uchun qiziqarli internet xavfsizligi va vaqtni boshqarish bo'yicha "
            "mutaxassissan. Har doim o'quvchilarga turli xil mavzularda foydali "
            "qo'llanmalar berasiz (masalan: fishing, kiberbulling, internetda shaxsiy ma'lumotlar, "
            "vaqtni to'g'ri taqsimlash, o'yin qaramligidan qutulish va h.k.).\n\n"
            "Menga hozir bitta yangi qiziqarli mavzu bo'yicha 3 sahifalik qo'llanma tuzib ber. "
            "Javob qat'iy ravishda quyidagi JSON ro'yxat (array) formatida bo'lsin:\n"
            "[\n"
            "  {\n"
            '    "title": "1-sahifa sarlavhasi",\n'
            '    "content": "Sahifa matni (HTML formatlashdan foydalan, <b>qalin</b>, <i>kursiv</i>, emojilar qo\'sh). Matn bolaga tushunarli va qiziqarli bo\'lsin.",\n'
            '    "image": "mavzuga eng mos keladigan so\'zni tanla: [time_management, cyber_security, online_learning, cyber_bullying]"\n'
            "  },\n"
            "  ...\n"
            "]\n"
            "Faqat JSON qaytar."
        )

        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        text = response.text.strip()
        
        # Markdown kod bloklarini tozalash
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        return data

    except Exception as e:
        logger.error(f"AI qollanma generatsiya xatosi: {e}")
        return []


async def generate_moral_situation() -> str:
    """AI orqali hayotiy axloqiy vaziyat (simulyator) yaratish."""
    if not GEMINI_API_KEY:
        return "Tasavvur qiling, do'stingiz sizga siri borligini aytdi va uni hech kimga aytmasligingizni so'radi. Lekin bu sir uning xavfsizligiga xavf tug'dirishi mumkin. Nima qilgan bo'lardingiz?"
        
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            "Maktab yoshidagi bola uchun qiziqarli, o'ylantiradigan bitta qisqa hayotiy vaziyat (axloqiy dilemma) o'ylab top. "
            "Masalan: Do'stlik, rostgo'ylik, yordam berish kabi mavzularda. "
            "Matn o'zbek tilida, bolaga tushunarli va qisqa bo'lsin. Va oxirida 'Nima qilgan bo'lardingiz?' deb so'ra."
        )
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt]
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Simulyator generatsiyasida xato: {e}")
        return "Ko'chada ketayotib hamyon topib oldingiz, ichida puli bor. Atrofda hech kim yo'q. Nima qilasiz?"

async def evaluate_moral_answer(situation: str, answer: str) -> str:
    """AI orqali bolaning hayotiy vaziyatga bergan javobini tahlil qilish."""
    if not GEMINI_API_KEY:
        return "Javobingiz uchun rahmat! Har doim to'g'ri yo'lni tanlashga harakat qiling va kattalardan maslahat so'rashdan tortinmang."
        
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            f"Vaziyat: {situation}\n"
            f"Bolaning javobi: {answer}\n\n"
            "Sen mehribon va dono ustozsan. Bolaning bu qarorini tahlil qil. Uni maqtash bilan birga, agar xato qilsa "
            "muloyimlik bilan to'g'ri yo'lni tushuntirib ber. Ijobiy motivatsiya ber. Javob o'zbek tilida va samimiy bo'lsin."
        )
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt]
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Simulyator javob tahlilida xato: {e}")
        return "Javobingizni qabul qildim. Har doim halol va ochiqko'ngil bo'lish eng to'g'ri yo'ldir."

import asyncio

async def answer_parent_question(question: str) -> str:
    """
    Ota-onaning savoliga AI javob berish.
    Bolalar internet xavfsizligi bo'yicha mutaxassis sifatida javob qaytaradi.
    """
    if not GEMINI_API_KEY:
        return "AI xizmati sozlanmagan."

    max_retries = 3
    delay = 1.5

    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)

            prompt = (
                "Role & Persona:\n"
                "You are an expert AI assistant specialized in bolalar internet xavfsizligi va raqamli tarbiya (children's internet safety and digital parenting). "
                "You are precise, professional, and prioritize efficiency. Barcha javoblarni faqat O'zbek tilida yoz.\n\n"
                "Core Guidelines:\n"
                "- Formatting: Faqat quyidagi Telegram HTML teglaridan foydalan: <b>qalin</b>, <i>kursiv</i>, <code>kod</code>. Boshqa HTML teglarni va Markdownni (**) ishlatma. Ro'yxat uchun oddiy '• ' yoki '1. ' ishlating.\n"
                "- Accuracy: Provide practical, proven, and easily understandable advice for parents.\n"
                "- Constraint Enforcement: Do not include unnecessary conversational filler. Javob 300 so'zdan oshmasin. Matnni chiroyli qilish uchun emojilardan foydalan.\n"
                "- Safety & Ethics: Always adhere to responsible AI usage. Bolalar manfaati va xavfsizligini birinchi o'ringa qo'ying.\n"
                "- Handling Errors: Agar so'rov noaniq bo'lsa, bitta aniqlashtiruvchi savol bering.\n\n"
                "Response Structure:\n"
                "- Start with the most important information or direct answer.\n"
                "- Provide step-by-step instructions or actionable advice.\n"
                "- Include secondary advice only if relevant.\n\n"
                "Interaction Style:\n"
                "Be professional, empathetic, and concise.\n\n"
                f"Ota-onaning savoli: {question}"
            )

            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )

            text = response.text.strip()
            text = _sanitize_telegram_html(text)
            return text

        except Exception as e:
            logger.warning(f"AI savol-javob urinishi {attempt + 1} muvaffaqiyatsiz bo'ldi: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error(f"AI savol-javob xatosi (yakuniy): {e}")
                return "Kechirasiz, sun'iy intellekt xizmati hozirda band yoki ishlamayapti. Iltimos, bir ozdan keyin qaytadan urinib ko'ring yoki boshqa savol berib ko'ring."



import re

def _sanitize_telegram_html(text: str) -> str:
    """Telegram qo'llab-quvvatlamaydigan HTML teglarni tozalash."""
    allowed_tags = {'b', 'i', 'u', 's', 'code', 'pre', 'a', 'em', 'strong'}
    
    def replace_tag(match):
        full = match.group(0)
        tag_name = match.group(1).lower().strip()
        if tag_name in allowed_tags:
            return full
        return ""
    
    text = re.sub(r'<(/?)(\w+)(?:\s[^>]*)?\s*/?>', lambda m: replace_tag_fn(m, allowed_tags), text)
    return text


def replace_tag_fn(match, allowed_tags):
    tag_name = match.group(2).lower()
    if tag_name in allowed_tags:
        return match.group(0)
    return ""
