import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def main():
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                style TEXT NOT NULL DEFAULT 'cinematic',
                audio_url TEXT,
                video_url TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                kling_task_id TEXT,
                prompt TEXT,
                duration FLOAT,
                bpm FLOAT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
    print("projects table created!")

asyncio.run(main())
