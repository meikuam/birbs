import os
import sys
sys.path.append('.')

import uvicorn
from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.web.database.user_manager import current_superuser, current_user
from src.web.database.users import User, create_db_and_tables
from src.web.routes.users import auth_router, register_router, reset_password_router, verify_router, users_router, create_first_admin

from src.web.routes.leds import leds_router
from src.web.routes.feeder import feeder_router
from src.web.routes.drinker import drinker_router
from src.web.routes.reset import reset_router
from src.web.routes.video import video_router


users_app = FastAPI()

users_app.include_router(
    auth_router,
    prefix="/auth/jwt",
    tags=["auth"]
)
users_app.include_router(
    register_router,
    prefix="/auth",
    tags=["auth"],
)
users_app.include_router(
    reset_password_router,
    prefix="/auth",
    tags=["auth"],
)
users_app.include_router(
    verify_router,
    prefix="/auth",
    tags=["auth"],
)
users_app.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
)
users_app.include_router(
    leds_router,
    prefix="/api/leds",
    tags=["leds"])
users_app.include_router(
    feeder_router,
    prefix="/api/feeder",
    tags=["feeder"])
users_app.include_router(
    drinker_router,
    prefix="/api/drinker",
    tags=["drinker"])
users_app.include_router(
    reset_router,
    prefix="/api/reset",
    tags=["reset"])

users_app.include_router(
    video_router,
    prefix="/api/video",
    tags=["video"])

@users_app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    await create_first_admin()

@users_app.get("/")
def index(request: Request, user: User = Depends(current_user)):
    if user is not None:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return RedirectResponse("/login")

@users_app.get("/login")
def login(request: Request, user: User = Depends(current_user)):
    if user is not None:
        return RedirectResponse("/")
    else:
        return templates.TemplateResponse("login.html", {"request": request})


@users_app.get("/leds")
async def index(request: Request):
    return templates.TemplateResponse("leds.html", {"request": request})

@users_app.get("/drinker")
async def index(request: Request):
    return templates.TemplateResponse("drinker.html", {"request": request})

@users_app.get("/feeder")
async def index(request: Request):
    return templates.TemplateResponse("feeder.html", {"request": request})


@users_app.get("/video")
async def index(request: Request):
    return templates.TemplateResponse("video.html", {"request": request})

@users_app.get("/simple")
async def index(request: Request):
    return templates.TemplateResponse("simple.html", {"request": request})


templates = Jinja2Templates(directory="www/templates")




if __name__ == "__main__":
    uvicorn.run("src.web.users_app:users_app", host="0.0.0.0", port=8080, log_level="info")
