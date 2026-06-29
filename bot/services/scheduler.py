"""
APScheduler — kunlik hisobotlar va maslahatlar.
Har kuni soat 20:00 da hisobot, 09:00 da maslahat yuboradi.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database import crud
from bot.services.report_generator import generate_report_text

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")

# Bot reference — main.py da o'rnatiladi
_bot = None


def set_bot(bot):
    """Bot referensini saqlash."""
    global _bot
    _bot = bot


async def send_daily_reports():
    """Har kuni soat 20:00 da barcha ota-onalarga hisobot yuborish."""
    if not _bot:
        return

    try:
        families = await crud.get_all_active_families()
        sent = 0
        for family in families:
            try:
                report = await generate_report_text(family.child_id)
                await _bot.send_message(family.parent_id, report, parse_mode="HTML")
                sent += 1
            except Exception as e:
                logger.error(f"Hisobot yuborishda xato (parent: {family.parent_id}): {e}")

        logger.info(f"✅ Kunlik hisobotlar yuborildi: {sent} ta")
    except Exception as e:
        logger.error(f"Kunlik hisobotlar xatosi: {e}")


async def send_daily_tips():
    """Har kuni soat 09:00 da barcha ota-onalarga maslahat yuborish."""
    if not _bot:
        return

    try:
        tip = await crud.get_random_tip()
        if not tip:
            return

        parents = await crud.get_all_parents()
        sent = 0
        for parent in parents:
            try:
                await _bot.send_message(
                    parent.id,
                    f"💡 <b>Bugungi maslahat:</b>\n\n{tip.tip_uz}",
                    parse_mode="HTML"
                )
                sent += 1
            except Exception as e:
                logger.error(f"Maslahat yuborishda xato (parent: {parent.id}): {e}")

        logger.info(f"✅ Kunlik maslahatlar yuborildi: {sent} ta")
    except Exception as e:
        logger.error(f"Kunlik maslahatlar xatosi: {e}")


def setup_scheduler():
    """Schedulerni sozlash va ishga tushirish."""
    # Har kuni soat 20:00 da hisobot
    scheduler.add_job(
        send_daily_reports,
        trigger=CronTrigger(hour=20, minute=0),
        id="daily_reports",
        replace_existing=True
    )

    # Har kuni soat 09:00 da maslahat
    scheduler.add_job(
        send_daily_tips,
        trigger=CronTrigger(hour=9, minute=0),
        id="daily_tips",
        replace_existing=True
    )

    scheduler.start()
    logger.info("📅 Scheduler ishga tushdi (hisobot: 20:00, maslahat: 09:00)")
