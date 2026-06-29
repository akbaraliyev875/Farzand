"""
Database CRUD operatsiyalari.
Barcha asinxron funksiyalar — SQLAlchemy async session orqali.
"""

import random
import string
from datetime import datetime, date, timedelta
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from bot.config import DB_URL
from database.models import (
    Base, User, FamilyLink, ActivityLog,
    KeywordAlert, TestResult, ContentCheck, DailyTip
)

# Async engine va session
engine = create_async_engine(DB_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Jadvalarni yaratish (agar mavjud bo'lmasa)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Yangi session olish."""
    return async_session()


# ─── USERS ────────────────────────────────────────────────────

async def get_user(user_id: int) -> Optional[User]:
    """Foydalanuvchini ID bo'yicha olish."""
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


async def create_user(
    user_id: int, role: str, full_name: str, username: str = None
) -> User:
    """Yangi foydalanuvchi yaratish."""
    async with async_session() as session:
        user = User(
            id=user_id,
            role=role,
            full_name=full_name,
            username=username,
            created_at=datetime.utcnow()
        )
        session.add(user)
        await session.commit()
        return user


async def update_user_role(user_id: int, role: str):
    """Foydalanuvchi rolini yangilash."""
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.role = role
            await session.commit()


# ─── FAMILY LINKS ────────────────────────────────────────────

def _generate_link_code(length: int = 6) -> str:
    """Tasodifiy ulanish kodi generatsiya qilish."""
    return "".join(random.choices(string.digits, k=length))


async def create_family_link(parent_id: int) -> str:
    """Ota-ona uchun ulanish kodi yaratish."""
    async with async_session() as session:
        # Avvalgi faol linkni o'chirish
        result = await session.execute(
            select(FamilyLink).where(
                and_(
                    FamilyLink.parent_id == parent_id,
                    FamilyLink.child_id.is_(None),
                    FamilyLink.is_active == True
                )
            )
        )
        old_links = result.scalars().all()
        for link in old_links:
            link.is_active = False

        # Yangi kod yaratish
        code = _generate_link_code()
        link = FamilyLink(
            parent_id=parent_id,
            link_code=code,
            is_active=True,
            created_at=datetime.utcnow()
        )
        session.add(link)
        await session.commit()
        return code


async def connect_child(child_id: int, code: str) -> Optional[FamilyLink]:
    """Farzandni ulanish kodi orqali ota-onaga ulash."""
    async with async_session() as session:
        result = await session.execute(
            select(FamilyLink).where(
                and_(
                    FamilyLink.link_code == code,
                    FamilyLink.child_id.is_(None),
                    FamilyLink.is_active == True
                )
            )
        )
        link = result.scalar_one_or_none()
        if not link:
            return None

        link.child_id = child_id
        link.linked_at = datetime.utcnow()
        await session.commit()
        return link


async def get_parent_for_child(child_id: int) -> Optional[int]:
    """Farzandning ota-onasini topish."""
    async with async_session() as session:
        result = await session.execute(
            select(FamilyLink.parent_id).where(
                and_(
                    FamilyLink.child_id == child_id,
                    FamilyLink.is_active == True
                )
            )
        )
        row = result.scalar_one_or_none()
        return row


async def get_children_for_parent(parent_id: int) -> list:
    """Ota-onaning barcha farzandlarini olish."""
    async with async_session() as session:
        result = await session.execute(
            select(FamilyLink).where(
                and_(
                    FamilyLink.parent_id == parent_id,
                    FamilyLink.child_id.is_not(None),
                    FamilyLink.is_active == True
                )
            )
        )
        return result.scalars().all()


async def get_all_active_families() -> list:
    """Barcha faol oilalarni olish."""
    async with async_session() as session:
        result = await session.execute(
            select(FamilyLink).where(
                and_(
                    FamilyLink.child_id.is_not(None),
                    FamilyLink.is_active == True
                )
            )
        )
        return result.scalars().all()


# ─── ACTIVITY LOGS ───────────────────────────────────────────

async def log_activity(
    child_id: int, session_start: datetime,
    session_end: datetime, duration_min: int
):
    """Faollik logini yozish."""
    async with async_session() as session:
        log = ActivityLog(
            child_id=child_id,
            session_start=session_start,
            session_end=session_end,
            duration_min=duration_min,
            date=session_start.date()
        )
        session.add(log)
        await session.commit()


async def get_daily_activity(child_id: int, target_date: date = None) -> int:
    """Kunlik umumiy ekran vaqtini olish (minutlarda)."""
    if target_date is None:
        target_date = date.today()
    async with async_session() as session:
        result = await session.execute(
            select(func.coalesce(func.sum(ActivityLog.duration_min), 0)).where(
                and_(
                    ActivityLog.child_id == child_id,
                    ActivityLog.date == target_date
                )
            )
        )
        return result.scalar()


# ─── KEYWORD ALERTS ──────────────────────────────────────────

async def save_alert(child_id: int, keyword: str, category: str, context: str = None):
    """Xavfli so'z signalini saqlash."""
    async with async_session() as session:
        alert = KeywordAlert(
            child_id=child_id,
            keyword=keyword,
            category=category,
            context=context,
            detected_at=datetime.utcnow()
        )
        session.add(alert)
        await session.commit()


async def get_daily_alerts(child_id: int, target_date: date = None) -> list:
    """Kunlik ogohlantirishlarni olish."""
    if target_date is None:
        target_date = date.today()
    async with async_session() as session:
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())
        result = await session.execute(
            select(KeywordAlert).where(
                and_(
                    KeywordAlert.child_id == child_id,
                    KeywordAlert.detected_at.between(start, end)
                )
            )
        )
        return result.scalars().all()


# ─── TEST RESULTS ────────────────────────────────────────────

async def save_test_result(
    child_id: int, test_type: str, score: int, risk_level: str
) -> TestResult:
    """Test natijasini saqlash."""
    async with async_session() as session:
        test = TestResult(
            child_id=child_id,
            test_type=test_type,
            score=score,
            risk_level=risk_level,
            taken_at=datetime.utcnow()
        )
        session.add(test)
        await session.commit()
        return test


async def get_latest_test(child_id: int) -> Optional[TestResult]:
    """Oxirgi test natijasini olish."""
    async with async_session() as session:
        result = await session.execute(
            select(TestResult)
            .where(TestResult.child_id == child_id)
            .order_by(TestResult.taken_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


# ─── CONTENT CHECKS ─────────────────────────────────────────

async def save_content_check(
    parent_id: int, file_id: str, result_str: str, confidence: float = None
):
    """Kontent tekshiruv natijasini saqlash."""
    async with async_session() as session:
        check = ContentCheck(
            parent_id=parent_id,
            file_id=file_id,
            result=result_str,
            confidence=confidence,
            checked_at=datetime.utcnow()
        )
        session.add(check)
        await session.commit()


async def get_today_check_count(parent_id: int) -> int:
    """Bugungi kontent tekshiruvlar sonini olish."""
    today = date.today()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    async with async_session() as session:
        result = await session.execute(
            select(func.count(ContentCheck.id)).where(
                and_(
                    ContentCheck.parent_id == parent_id,
                    ContentCheck.checked_at.between(start, end)
                )
            )
        )
        return result.scalar()


# ─── DAILY TIPS ──────────────────────────────────────────────

async def get_random_tip() -> Optional[DailyTip]:
    """Tasodifiy faol maslahat olish."""
    async with async_session() as session:
        result = await session.execute(
            select(DailyTip).where(DailyTip.is_active == True)
        )
        tips = result.scalars().all()
        if tips:
            return random.choice(tips)
        return None


async def get_all_parents() -> list:
    """Barcha ota-onalarni olish."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.role == "parent")
        )
        return result.scalars().all()


async def seed_tips():
    """Boshlang'ich maslahatlarni qo'shish (agar bo'sh bo'lsa)."""
    async with async_session() as session:
        result = await session.execute(select(func.count(DailyTip.id)))
        count = result.scalar()
        if count > 0:
            return

        tips = [
            DailyTip(tip_uz="🔐 Farzandingizga parolni hech kimga bermaslikni o'rgating — hatto do'stlariga ham.", category="xavfsizlik"),
            DailyTip(tip_uz="🔗 Noma'lum linkni ochmaslik haqida bugun gaplashing. Fishing hujumlari ko'paymoqda.", category="xavfsizlik"),
            DailyTip(tip_uz="📵 Kechqurun soat 21:00 dan keyin telefon ishlatmaslik qoidasini birgalikda kiriting.", category="tartib"),
            DailyTip(tip_uz="👁️ Farzandingiz qaysi YouTube kanallarni ko'rishini birgalikda ko'ring.", category="nazorat"),
            DailyTip(tip_uz="💬 Telegram guruhlarida kim bilan muloqot qilayotganini so'rang — do'stona suhbat shaklida.", category="muloqot"),
            DailyTip(tip_uz="🎮 O'yin o'ynash vaqtini cheklang: hafta kunlari 1 soat, dam olish kunlari 2 soat.", category="tartib"),
            DailyTip(tip_uz="📱 Yangi ilova o'rnatishdan oldin birga ko'rib chiqish qoidasini kiriting.", category="nazorat"),
            DailyTip(tip_uz="🤝 Internetda notanish odamlar bilan gaplashmaslik haqida tushuntiring.", category="xavfsizlik"),
            DailyTip(tip_uz="📸 Shaxsiy rasmlarni internetga qo'ymaslik kerakligi haqida gaplashing.", category="maxfiylik"),
            DailyTip(tip_uz="⏰ Uxlashdan 1 soat oldin telefon ishlatmaslik — yaxshi uyqu uchun muhim.", category="sog'liq"),
            DailyTip(tip_uz="🏃 Har kuni kamida 1 soat jismoniy faoliyat — ekran vaqtiga alternativa.", category="sog'liq"),
            DailyTip(tip_uz="📚 Telefon o'rniga kitob o'qish odatini birgalikda shakllantiring.", category="ta'lim"),
            DailyTip(tip_uz="🛡️ Farzandingizga onlayn bulling haqida va nima qilish kerakligini tushuntiring.", category="xavfsizlik"),
            DailyTip(tip_uz="💡 Texnologiya yaxshi va yomon tomonlari borligini farzandingizga ochiq tushuntiring.", category="ta'lim"),
            DailyTip(tip_uz="🔔 Bildirishnomalarni kamaytirish — diqqatni jamlashga yordam beradi.", category="tartib"),
        ]
        session.add_all(tips)
        await session.commit()
