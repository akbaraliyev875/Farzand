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


async def send_birthday_reminders():
    """Tug'ilgan kun eslatmalari (Har kuni 09:00)."""
    if not _bot: return
    try:
        from datetime import date
        today = date.today().strftime("%d.%m")
        families = await crud.get_all_active_families()
        for family in families:
            profile = await crud.get_child_profile(family.child_id)
            if profile and profile.birthday and profile.birthday.startswith(today):
                try:
                    await _bot.send_message(
                        family.parent_id,
                        f"🎉 <b>Diqqat!</b>\n\nBugun farzandingizning tug'ilgan kuni!\nUni qutlashni va mehr ko'rsatishni unutmang! 🎂",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    pass
    except Exception as e:
        logger.error(f"Tug'ilgan kun eslatmasi xatosi: {e}")


async def send_motivation_reminders():
    """Maqsad va qobiliyatlar bo'yicha motivatsiya eslatmalari (Haftada 1 marta yakshanba 10:00)."""
    if not _bot: return
    try:
        families = await crud.get_all_active_families()
        for family in families:
            profile = await crud.get_child_profile(family.child_id)
            if profile and (profile.goals or profile.abilities or profile.wishes):
                msg = "💡 <b>Ruhlantiruvchi eslatma</b>\n\nFarzandingizning profilidan:\n"
                if profile.goals: msg += f"🎯 <b>Maqsadi:</b> {profile.goals}\n"
                if profile.abilities: msg += f"🌟 <b>Qobiliyati:</b> {profile.abilities}\n"
                if profile.wishes: msg += f"✨ <b>Istagi:</b> {profile.wishes}\n"
                msg += "\n<i>Bugun uning maqsadlariga erishishida qo'llab-quvvatlang yoki shu haqida suhbatlashing!</i>"
                try:
                    await _bot.send_message(family.parent_id, msg, parse_mode="HTML")
                except Exception:
                    pass
    except Exception as e:
        logger.error(f"Motivatsiya eslatmasi xatosi: {e}")


async def send_gratitude_reminder():
    """Har kuni 20:00 da farzandga kundalik yutuqlarni yozishni eslatish."""
    if not _bot: return
    try:
        children = await crud.get_all_children()
        for child in children:
            try:
                await _bot.send_message(
                    child.id,
                    "📖 <b>Kundalik Yutuqlar vaqti!</b>\n\nBugun nimalardan xursand bo'ldingiz? "
                    "Menyudan «📖 Kundalik Yutuqlar» tugmasini bosib yozib qoldiring!",
                    parse_mode="HTML"
                )
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Gratitude eslatmasi xatosi: {e}")

async def check_dangerous_moods():
    """Har kuni xavfli kayfiyatlarni tekshirish va ota-onaga xabar berish."""
    if not _bot: return
    try:
        families = await crud.get_all_active_families()
        for family in families:
            moods = await crud.get_latest_moods(family.child_id, 3)
            if len(moods) == 3:
                # Agar oxirgi 3 ta kayfiyat "Ma'yus" yoki "G'azabda" bo'lsa
                bad_moods = ["😔 Ma'yus", "😠 G'azabda"]
                if all(m.mood in bad_moods for m in moods):
                    try:
                        await _bot.send_message(
                            family.parent_id,
                            f"⚠️ <b>Diqqat: Xavfli Signal!</b>\n\n"
                            f"Farzandingiz ketma-ket 3 marta salbiy kayfiyat belgiladi. "
                            f"Farzandingizda stress kuzatilmoqda, iltimos, u bilan suhbatlashing.",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
    except Exception as e:
        logger.error(f"Xavfli kayfiyat tekshiruvida xato: {e}")


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
    
    scheduler.add_job(
        send_birthday_reminders,
        trigger=CronTrigger(hour=9, minute=0),
        id="birthday_reminders",
        replace_existing=True
    )
    
    scheduler.add_job(
        send_motivation_reminders,
        trigger=CronTrigger(day_of_week='sun', hour=10, minute=0),
        id="motivation_reminders",
        replace_existing=True
    )
    
    scheduler.add_job(
        send_gratitude_reminder,
        trigger=CronTrigger(hour=20, minute=0),
        id="gratitude_reminders",
        replace_existing=True
    )
    
    scheduler.add_job(
        check_dangerous_moods,
        trigger=CronTrigger(hour=20, minute=30),
        id="dangerous_moods",
        replace_existing=True
    )

    scheduler.start()
    logger.info("📅 Scheduler ishga tushdi")
