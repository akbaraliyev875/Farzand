"""
Hisobot generatsiya xizmati.
Farzandning kunlik hisobotini yaratadi.
"""

from datetime import date

from database import crud


async def generate_report_text(child_id: int, target_date: date = None) -> str:
    """Farzand uchun to'liq kunlik hisobot yaratish."""
    if target_date is None:
        target_date = date.today()

    # Farzand ma'lumotlari
    child = await crud.get_user(child_id)
    child_name = child.full_name if child else f"Farzand #{child_id}"

    # Ekran vaqti
    daily_min = await crud.get_daily_activity(child_id, target_date)
    hours = daily_min // 60
    mins = daily_min % 60

    # Ekran vaqti indikatori
    if daily_min <= 60:
        screen_emoji = "🟢"
        screen_status = "Normal"
    elif daily_min <= 180:
        screen_emoji = "🟡"
        screen_status = "O'rtacha"
    else:
        screen_emoji = "🔴"
        screen_status = "Yuqori"

    # Ogohlantirishlar
    alerts = await crud.get_daily_alerts(child_id, target_date)
    alert_text = ""
    if alerts:
        from bot.middlewares.keyword_filter import CATEGORY_NAMES
        alert_text = "\n\n⚠️ <b>Ogohlantirishlar:</b>\n"
        for alert in alerts:
            cat_name = CATEGORY_NAMES.get(alert.category, alert.category)
            alert_text += f"  • {cat_name}: <code>{alert.keyword}</code>\n"
    else:
        alert_text = "\n\n✅ Bugun ogohlantirish yo'q."

    # Oxirgi test natijasi
    last_test = await crud.get_latest_test(child_id)
    test_text = ""
    if last_test:
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        risk_names = {"low": "Past", "medium": "O'rtacha", "high": "Yuqori"}
        test_text = (
            f"\n\n📝 <b>Oxirgi test:</b>\n"
            f"  {risk_emoji.get(last_test.risk_level, '⚪')} "
            f"{risk_names.get(last_test.risk_level, 'Noma\'lum')} xavf "
            f"(ball: {last_test.score}/24)"
        )

    # Hisobotni yaratish
    report = (
        f"📊 <b>Kunlik hisobot</b>\n"
        f"📅 Sana: <b>{target_date.strftime('%d.%m.%Y')}</b>\n"
        f"👤 Farzand: <b>{child_name}</b>\n\n"
        f"{'─' * 25}\n\n"
        f"📱 <b>Ekran vaqti:</b>\n"
        f"  {screen_emoji} {hours} soat {mins} daqiqa ({screen_status})\n"
        f"{alert_text}"
        f"{test_text}\n\n"
        f"{'─' * 25}\n"
        f"🛡️ <i>Farzand Nazorati Bot</i>"
    )

    return report
