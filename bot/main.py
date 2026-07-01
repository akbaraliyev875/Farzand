"""
Farzand Nazorati Bot — Asosiy ishga tushirish fayli.
Barcha router, middleware va servislari shu yerda ulanadi.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from bot.config import BOT_TOKEN

# Handlers
from bot.handlers.parent.start import router as parent_start_router
from bot.handlers.parent.link_child import router as parent_link_router
from bot.handlers.parent.reports import router as parent_report_router
from bot.handlers.parent.content_check import router as parent_check_router
from bot.handlers.parent.ai_assistant import router as parent_ai_router
from bot.handlers.child.start import router as child_start_router
from bot.handlers.child.connect import router as child_connect_router
from bot.handlers.child.tests import router as child_tests_router
from bot.handlers.child.profile import router as child_profile_router
from bot.handlers.child.pomodoro import router as child_pomodoro_router
from bot.handlers.child.tasks_mood import router as child_tasks_mood_router
from bot.handlers.child.simulator import router as child_simulator_router
from bot.handlers.parent.tasks_mood import router as parent_tasks_mood_router

# Middlewares
from bot.middlewares.activity_tracker import ActivityTrackerMiddleware
from bot.middlewares.keyword_filter import KeywordFilterMiddleware

# Services
from bot.services.scheduler import setup_scheduler, set_bot

# Database
from database.crud import init_db, seed_tips

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Bot ishga tushganda."""
    logger.info("🚀 Farzand Nazorati Bot ishga tushmoqda...")

    # Database yaratish
    await init_db()
    logger.info("✅ Database tayyor")

    # Maslahatlarni qo'shish
    await seed_tips()
    logger.info("✅ Maslahatlar yuklandi")

    # Schedulerni sozlash
    set_bot(bot)
    setup_scheduler()
    logger.info("✅ Scheduler ishga tushdi")

    # Bot menyusini sozlash
    try:
        from aiogram.types import BotCommand
        commands = [
            BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="help", description="Yordam va qo'llanma"),
            BotCommand(command="report", description="Hisobot (Ota-ona)"),
            BotCommand(command="check", description="Tekshirish (Ota-ona)"),
            BotCommand(command="connect", description="Bog'lanish (Farzand)"),
            BotCommand(command="test", description="Test yechish (Farzand)"),
        ]
        await bot.set_my_commands(commands)
        logger.info("✅ Bot menyusi o'rnatildi")
    except Exception as e:
        logger.warning(f"⚠️ Bot menyusini o'rnatib bo'lmadi: {e}")


    # Bot ma'lumotlari
    try:
        me = await bot.get_me()
        logger.info(f"✅ Bot: @{me.username} ({me.full_name})")
    except Exception as e:
        logger.warning(f"⚠️ Bot ma'lumotlarini yuklab bo'lmadi (tarmoq xatosi): {e}")
    logger.info("🛡️ Farzand Nazorati Bot tayyor!")


async def on_shutdown(bot: Bot):
    """Bot to'xtaganda."""
    from bot.services.scheduler import scheduler
    scheduler.shutdown(wait=False)
    logger.info("🔴 Bot to'xtatildi")


async def main():
    """Asosiy funksiya."""
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token":
        logger.error(
            "❌ BOT_TOKEN sozlanmagan!\n"
            "1. .env.example faylini .env ga nusxalang\n"
            "2. @BotFather dan token oling\n"
            "3. .env faylida BOT_TOKEN ni to'ldiring"
        )
        sys.exit(1)

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewares — barcha xabarlar uchun
    dp.message.middleware(ActivityTrackerMiddleware())
    dp.message.middleware(KeywordFilterMiddleware())

    # Routerlarni ulash (tartib muhim!)
    dp.include_routers(
        parent_start_router,    # /start, /help (rol tanlash bilan)
        parent_link_router,     # /link
        parent_report_router,   # /report
        parent_check_router,    # /check, rasmlar
        parent_ai_router,       # AI yordamchi
        child_connect_router,   # /connect (FSM bilan)
        child_tests_router,     # /test (FSM bilan)
        child_profile_router,   # Profile va xohishlar
        child_pomodoro_router,  # Pomodoro
        child_simulator_router, # Simulyator
        child_tasks_mood_router,# Farzand vazifa va kayfiyat
        parent_tasks_mood_router,# Ota-ona vazifa va kayfiyat
        child_start_router,     # Qolgan barcha child handlerlar (Fallback)ri
    )

    # Lifecycle
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Botni ishga tushirish
    logger.info("🔄 Polling boshlanmoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
