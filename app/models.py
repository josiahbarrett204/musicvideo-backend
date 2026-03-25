from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    plan = Column(String, default="free")


from sqlalchemy import ForeignKey, Text, BigInteger

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    r2_key = Column(String, nullable=False)
    url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    status = Column(String, default="processing")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    style = Column(String, default="cinematic")
    status = Column(String, default="pending")
    bpm = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)
    prompt = Column(Text, nullable=True)
    audio_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    task_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
