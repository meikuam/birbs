import os
import sys
sys.path.append('.')

import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.templating import Jinja2Templates

from src.web.routes.leds import leds_router
from src.web.routes.feeder import feeder_router
from src.web.routes.drinker import drinker_router
from src.web.routes.reset import reset_router
from src.web.routes.video import video_router


main_app = FastAPI()

main_app.include_router(leds_router, prefix="/api/leds", tags=["leds"])
main_app.include_router(feeder_router, prefix="/api/feeder", tags=["feeder"])
main_app.include_router(drinker_router, prefix="/api/drinker", tags=["drinker"])
main_app.include_router(reset_router, prefix="/api/reset", tags=["reset"])

main_app.include_router(video_router, prefix="/api/video", tags=["video"])


@main_app.get("/")
def index( request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@main_app.get("/leds")
async def index(request: Request):
    return templates.TemplateResponse("leds.html", {"request": request})

@main_app.get("/drinker")
async def index(request: Request):
    return templates.TemplateResponse("drinker.html", {"request": request})

@main_app.get("/feeder")
async def index(request: Request):
    return templates.TemplateResponse("feeder.html", {"request": request})


@main_app.get("/video")
async def index(request: Request):
    return templates.TemplateResponse("video.html", {"request": request})

@main_app.get("/simple")
async def index(request: Request):
    return templates.TemplateResponse("simple.html", {"request": request})


templates = Jinja2Templates(directory="www/templates")






if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info")
