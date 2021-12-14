import os
import sys
sys.path.append('.')
from src.controller.controller_api import ControllerApi

import uvicorn
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, UJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

class Leds(BaseModel):
    state: Optional[bool]
    value: Optional[int]

controller_api: ControllerApi = ControllerApi()
app = FastAPI()

# app.mount("/static", StaticFiles(directory="www/static"), name="static")
templates = Jinja2Templates(directory="www/templates")


# @app.on_event("startup")
# async def startup_event():
#     controller_api = ControllerApi()

@app.get("/")
def index( request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/leds", response_model=Leds)
async def get_state():
    state, value = controller_api.leds_get()
    return {"state": state, "value": value}


@app.post("/api/leds")
async def set_state(leds: Leds):
    if leds.state is not None:
        controller_api.leds_status_set(leds.state)
    if leds.value is not None:
        controller_api.leds_value_set(leds.value)
    return 200


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info")
