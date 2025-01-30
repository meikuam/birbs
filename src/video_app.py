import os
import sys
sys.path.append('.')

import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from src.web.routes.video import video_router


video_app = FastAPI()

video_app.include_router(video_router, prefix="/api/video", tags=["video"])

templates = Jinja2Templates(directory="www/templates")


@video_app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("video_unsafe.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("video_app:video_app", host="0.0.0.0", port=9000, log_level="info")
