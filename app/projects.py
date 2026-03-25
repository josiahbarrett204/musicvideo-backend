import os, uuid, tempfile
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.deps import get_db
from app.auth import get_current_user
from app.models import User
from app.r2 import upload_file
from app.kling import generate_video, get_task_status
from app.audio_analysis import analyze_audio, build_prompt
from PIL import Image
import io

router = APIRouter()


def convert_to_jpeg(file_bytes: bytes, filename: str) -> tuple:
    try:
        img = Image.open(io.BytesIO(file_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=90)
        new_name = filename.rsplit(".", 1)[0] + ".jpg"
        return out.getvalue(), new_name
    except Exception:
        return file_bytes, filename


async def process_project(project_id: int, audio_path: str, title: str, style: str, db: AsyncSession, custom_prompt: str = "", portrait_urls: list = []):
    try:
        analysis = analyze_audio(audio_path)
        prompt = custom_prompt if custom_prompt else build_prompt(title, style, analysis)
        image_url = portrait_urls[0] if portrait_urls else None
        task_id = await generate_video(prompt, analysis.get("duration", 5), image_url=image_url)
        await db.execute(
            text("UPDATE projects SET status='generating', kling_task_id=:tid WHERE id=:id"),
            {"tid": task_id, "id": project_id}
        )
        await db.commit()

        import asyncio
        for _ in range(120):
            await asyncio.sleep(10)
            result = await get_task_status(task_id)
            if result["status"] == "succeed":
                await db.execute(
                    text("UPDATE projects SET status='done', video_url=:url WHERE id=:id"),
                    {"url": result["video_url"], "id": project_id}
                )
                await db.commit()
                break
            elif result["status"] == "failed":
                await db.execute(
                    text("UPDATE projects SET status='failed' WHERE id=:id"),
                    {"id": project_id}
                )
                await db.commit()
                break
    except Exception as e:
        print(f"[process_project ERROR] {type(e).__name__}: {e}")
        import traceback; traceback.print_exc()
        try:
            await db.execute(
                text("UPDATE projects SET status='failed' WHERE id=:id"),
                {"id": project_id}
            )
            await db.commit()
        except Exception:
            pass
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


@router.post("")
async def create_project(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    style: str = Form(...),
    custom_prompt: str = Form(""),
    audio: UploadFile = File(...),
    portrait: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    audio_data = await audio.read()
    audio_key = f"audio/{current_user.id}/{uuid.uuid4()}{os.path.splitext(audio.filename)[1]}"
    audio_url = await upload_file(audio_data, audio_key, audio.content_type or "audio/mpeg")

    portrait_url = ""
    if portrait and portrait.filename:
        portrait_raw = await portrait.read()
        portrait_data, portrait_filename = convert_to_jpeg(portrait_raw, portrait.filename)
        portrait_key = f"portraits/{current_user.id}/{uuid.uuid4()}.jpg"
        portrait_url = await upload_file(portrait_data, portrait_key, "image/jpeg")

    result = await db.execute(
        text("""INSERT INTO projects (user_id, title, style, audio_url, portrait_urls, status)
                VALUES (:uid, :title, :style, :audio_url, :portrait_urls, 'queued')
                RETURNING id, title, style, audio_url, portrait_urls, status, created_at"""),
        {"uid": current_user.id, "title": title, "style": style,
         "audio_url": audio_url, "portrait_urls": portrait_url}
    )
    await db.commit()
    row = result.fetchone()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1])
    tmp.write(audio_data)
    tmp.close()

    portrait_list = [portrait_url] if portrait_url else []
    background_tasks.add_task(
        process_project, row.id, tmp.name, title, style, db, custom_prompt, portrait_list
    )

    return {"id": row.id, "title": row.title, "style": row.style,
            "audio_url": row.audio_url, "portrait_urls": row.portrait_urls,
            "status": row.status, "created_at": str(row.created_at)}


@router.get("")
async def get_projects(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        text("SELECT id, title, style, audio_url, portrait_urls, status, video_url, created_at FROM projects WHERE user_id=:uid ORDER BY created_at DESC"),
        {"uid": current_user.id}
    )
    rows = result.fetchall()
    return [{"id": r.id, "title": r.title, "style": r.style, "audio_url": r.audio_url,
             "portrait_urls": r.portrait_urls, "status": r.status, "video_url": r.video_url,
             "created_at": str(r.created_at)} for r in rows]


@router.get("/{project_id}")
async def get_project(project_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        text("SELECT id, title, style, audio_url, portrait_urls, status, video_url, created_at FROM projects WHERE id=:id AND user_id=:uid"),
        {"id": project_id, "uid": current_user.id}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"id": row.id, "title": row.title, "style": row.style, "audio_url": row.audio_url,
            "portrait_urls": row.portrait_urls, "status": row.status, "video_url": row.video_url,
            "created_at": str(row.created_at)}


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await db.execute(
        text("DELETE FROM projects WHERE id=:id AND user_id=:uid"),
        {"id": project_id, "uid": current_user.id}
    )
    await db.commit()
    return {"message": "Deleted"}

@router.post("/{project_id}/retry")
async def retry_project(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        text("SELECT id, title, style, audio_url, portrait_urls FROM projects WHERE id=:id AND user_id=:uid AND status=:status"),
        {"id": project_id, "uid": current_user.id, "status": "failed"}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Project not found or not in failed state")

    await db.execute(
        text("UPDATE projects SET status=:status, video_url=NULL WHERE id=:id"),
        {"status": "queued", "id": project_id}
    )
    await db.commit()

    import tempfile, httpx, os
    async with httpx.AsyncClient() as client:
        r = await client.get(row.audio_url)
        ext = os.path.splitext(row.audio_url)[1] or ".mp3"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        tmp.write(r.content)
        tmp.close()

    portrait_list = [u for u in (row.portrait_urls or "").split(",") if u]
    background_tasks.add_task(
        process_project, row.id, tmp.name, row.title, row.style, db, "", portrait_list
    )
    return {"message": "Re-queued"}
