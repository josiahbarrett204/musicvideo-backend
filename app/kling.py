import time, hmac, hashlib, base64, json
import httpx
from app.config import settings

def _make_jwt() -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg":"HS256","typ":"JWT"}).encode()).rstrip(b"=").decode()
    now = int(time.time())
    payload = base64.urlsafe_b64encode(json.dumps({
        "iss": settings.kling_access_key,
        "exp": now + 1800,
        "nbf": now - 5
    }).encode()).rstrip(b"=").decode()
    sig = base64.urlsafe_b64encode(
        hmac.new(settings.kling_secret_key.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    ).rstrip(b"=").decode()
    return f"{header}.{payload}.{sig}"

KLING_BASE = "https://api.klingai.com"

async def generate_video(prompt: str, duration: float = 5, image_url: str = None) -> str:
    token = _make_jwt()
    dur_str = "10" if duration >= 8 else "5"
    body = {"model_name": "kling-v1", "prompt": prompt, "duration": dur_str, "aspect_ratio": "16:9", "mode": "std"}
    if image_url:
        body["image_url"] = image_url
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{KLING_BASE}/v1/videos/text2video",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=body
        )
        print(f"[Kling] submit status={r.status_code} body={r.text[:300]}", flush=True)
        r.raise_for_status()
        return r.json()["data"]["task_id"]

async def get_task_status(task_id: str) -> dict:
    token = _make_jwt()
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"{KLING_BASE}/v1/videos/text2video/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"[Kling] poll status={r.status_code} body={r.text[:300]}", flush=True)
        r.raise_for_status()
        data = r.json()["data"]
        status = data["task_status"]
        url = None
        if status == "succeed":
            url = data["task_result"]["videos"][0]["url"]
        return {"status": status, "video_url": url}
