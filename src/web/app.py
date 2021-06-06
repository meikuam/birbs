import os
import sys
sys.path.append('.')
from src.ir_led.ir_led import IRLedController

import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, UJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



ir_led_controller = IRLedController()
app = FastAPI()

app.mount("/static", StaticFiles(directory="www/static"), name="static")
templates = Jinja2Templates(directory="www/templates")



@app.get("/")
def index( request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/get_state")
def get_state(request: Request):
    global ir_led_controller
    return {"state": ir_led_controller.state, "value": ir_led_controller.value}


@app.post("/api/set_state")
def set_state(request: Request):
    global ir_led_controller
    req_json = request.json()
    if 'state' in req_json:
        ir_led_controller.set_led_state(req_json['state'])
    if 'value' in req_json:
        ir_led_controller.set_led_value(req_json['value'])
    return 200


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info")
