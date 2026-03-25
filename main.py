from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as auth_router
from app.projects import router as projects_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://musicvideo-frontend.vercel.app", "https://musicvideo-backend-production.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from sqlalchemy import text

@app.on_event("startup")
async def reset_stuck_projects():
    async with AsyncSessionLocal() as db:
        await db.execute(
            text("UPDATE projects SET status='failed' WHERE status='generating'")
        )
        await db.commit()
        print("✅ Reset any stuck generating projects")

app.include_router(auth_router, prefix="/api/auth")
app.include_router(projects_router, prefix="/api/projects")
