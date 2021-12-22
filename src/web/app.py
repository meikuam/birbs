import os
import sys
sys.path.append('.')

import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.templating import Jinja2Templates

from src.web.routes.leds import leds_router
from src.web.routes.feeder import feeder_router
from src.web.routes.drinker import drinker_router
from src.web.routes.video import video_router
from src.web.routes.reset import reset_router


app = FastAPI()

app.include_router(leds_router, prefix="/api/leds", tags=["leds"])
app.include_router(feeder_router, prefix="/api/feeder", tags=["feeder"])
app.include_router(drinker_router, prefix="/api/drinker", tags=["drinker"])
app.include_router(video_router, prefix="/api/video", tags=["video"])
app.include_router(reset_router, prefix="/api/reset", tags=["reset"])

# app.mount("/static", StaticFiles(directory="www/static"), name="static")
templates = Jinja2Templates(directory="www/templates")


# @app.on_event("startup")
# async def startup_event():
#     controller_api = ControllerApi()



@app.get("/")
def index( request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/video")
async def index(request: Request):
    return templates.TemplateResponse("video.html", {"request": request})

@app.get("/leds")
async def index(request: Request):
    return templates.TemplateResponse("leds.html", {"request": request})

@app.get("/drinker")
async def index(request: Request):
    return templates.TemplateResponse("drinker.html", {"request": request})

@app.get("/feeder")
async def index(request: Request):
    return templates.TemplateResponse("feeder.html", {"request": request})




if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info")
