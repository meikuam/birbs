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


controller_app = FastAPI()

controller_app.include_router(leds_router, prefix="/api/leds", tags=["leds"])
controller_app.include_router(feeder_router, prefix="/api/feeder", tags=["feeder"])
controller_app.include_router(drinker_router, prefix="/api/drinker", tags=["drinker"])
controller_app.include_router(reset_router, prefix="/api/reset", tags=["reset"])


@controller_app.get("/")
def index( request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@controller_app.get("/leds")
async def index(request: Request):
    return templates.TemplateResponse("leds.html", {"request": request})

@controller_app.get("/drinker")
async def index(request: Request):
    return templates.TemplateResponse("drinker.html", {"request": request})

@controller_app.get("/feeder")
async def index(request: Request):
    return templates.TemplateResponse("feeder.html", {"request": request})



templates = Jinja2Templates(directory="www/templates")






if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info")
