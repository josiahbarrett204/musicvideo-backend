import boto3
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import get_current_user, get_db
from app.models import User, Video
from app.config import settings

router = APIRouter()

def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )

@router.post("/videos/upload")
async def upload_video(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    r2_key = f"videos/{current_user.id}/{uuid.uuid4()}/{file.filename}"
    r2 = get_r2_client()
    r2.upload_fileobj(file.file, settings.r2_bucket_name, r2_key)
    url = f"{settings.r2_public_base_url}/{r2_key}"

    video = Video(
        user_id=current_user.id,
        title=title,
        description=description,
        r2_key=r2_key,
        url=url,
    )
    db.add(video)
    await db.commit()
    await db.refresh(video)

    return {"id": video.id, "title": video.title, "url": video.url, "status": video.status}

from sqlalchemy.future import select as sa_select

@router.get("/videos")
async def list_videos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        sa_select(Video).where(Video.user_id == current_user.id).order_by(Video.created_at.desc())
    )
    videos = result.scalars().all()
    return [
        {"id": v.id, "title": v.title, "url": v.url, "status": v.status, "created_at": str(v.created_at)}
        for v in videos
    ]

@router.get("/videos/{video_id}")
async def get_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        sa_select(Video).where(Video.id == video_id, Video.user_id == current_user.id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return {
        "id": video.id,
        "title": video.title,
        "description": video.description,
        "url": video.url,
        "thumbnail_url": video.thumbnail_url,
        "status": video.status,
        "created_at": str(video.created_at),
    }
