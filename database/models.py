"""
SQLAlchemy modellari — Farzand Nazorati bot uchun.
SQLite bilan ishlaydi (aiosqlite).
"""

from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, Integer, String, Text, Float,
    Boolean, DateTime, Date, ForeignKey, create_engine
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """Foydalanuvchilar — ota-ona yoki farzand."""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Telegram user_id
    role = Column(String(10), nullable=False)   # 'parent' yoki 'child'
    full_name = Column(String(100))
    username = Column(String(50))
    language = Column(String(5), default="uz")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_premium = Column(Boolean, default=False)

    # Relationships
    children_links = relationship(
        "FamilyLink", foreign_keys="FamilyLink.parent_id", back_populates="parent"
    )
    parent_links = relationship(
        "FamilyLink", foreign_keys="FamilyLink.child_id", back_populates="child"
    )


class FamilyLink(Base):
    """Ota-ona ↔ Farzand bog'liqlik."""
    __tablename__ = "family_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    child_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    link_code = Column(String(10), unique=True, nullable=False)
    linked_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("User", foreign_keys=[parent_id], back_populates="children_links")
    child = relationship("User", foreign_keys=[child_id], back_populates="parent_links")


class ActivityLog(Base):
    """Ekran vaqti loglari."""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    session_start = Column(DateTime, nullable=False)
    session_end = Column(DateTime, nullable=False)
    duration_min = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)


class KeywordAlert(Base):
    """Xavfli so'zlar signallari."""
    __tablename__ = "keyword_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    keyword = Column(String(50), nullable=False)
    category = Column(String(30), nullable=False)
    context = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    is_notified = Column(Boolean, default=False)


class TestResult(Base):
    """Qaramlik test natijalari."""
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    test_type = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False)
    risk_level = Column(String(10), nullable=False)  # 'low', 'medium', 'high'
    taken_at = Column(DateTime, default=datetime.utcnow)


class ContentCheck(Base):
    """Kontent tekshirish tarixi."""
    __tablename__ = "content_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    file_id = Column(String(200), nullable=False)
    result = Column(String(20), nullable=False)  # 'safe','violence','adult','gambling','unknown'
    confidence = Column(Float, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)


class DailyTip(Base):
    """Kunlik maslahatlar."""
    __tablename__ = "daily_tips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tip_uz = Column(Text, nullable=False)
    tip_ru = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
