from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from surv_server.tortoise.db import init_db
from surv_server.tortoise.models import PhotoRecord

app = FastAPI(title="SurvServer Client API", version="1.0.0")


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def read_root():
    return RedirectResponse("/docs")


@app.get("/photos/{token}/file")
async def get_photo_by_token(token: str):
    p: PhotoRecord = (
        await PhotoRecord.filter(token=token).prefetch_related("ftp_user").first()
    )
    if not p:
        return JSONResponse({"detail": "Photo not found"}, status_code=404)
    path = p.get_real_path()
    return FileResponse(path)
