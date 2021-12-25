import os
import sys
sys.path.append('.')
import asyncio
import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.templating import Jinja2Templates

from src.web.routes.leds import leds_router
from src.web.routes.feeder import feeder_router
from src.web.routes.drinker import drinker_router
from src.web.routes.reset import reset_router
from src.web.routes.users import (
    jwt_auth_router,
    register_router,
    reset_password_router,
    users_router
)
from src.database.base import database
from src.database.users import create_first_admin, init_models

controller_app = FastAPI()


@controller_app.on_event("startup")
async def startup():
    await database.connect()
    await asyncio.run(init_models())
    success = await create_first_admin()


@controller_app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

controller_app.include_router(
    leds_router,
    prefix="/api/leds",
    tags=["leds"]
)
controller_app.include_router(
    feeder_router,
    prefix="/api/feeder",
    tags=["feeder"]
)
controller_app.include_router(
    drinker_router,
    prefix="/api/drinker",
    tags=["drinker"]
)
controller_app.include_router(
    reset_router,
    prefix="/api/reset",
    tags=["reset"]
)
# users routers
controller_app.include_router(
    jwt_auth_router,
    prefix="/auth/jwt",
    tags=["auth"]
)
controller_app.include_router(
    register_router,
    prefix="/auth",
    tags=["auth"]
)
# controller_app.include_router(
#     reset_password_router,
#     prefix="/auth",
#     tags=["auth"]
# )
controller_app.include_router(
    users_router,
    prefix="/users",
    tags=["users"]
)

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
