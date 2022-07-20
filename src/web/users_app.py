import os
import sys
sys.path.append('.')

import uvicorn
from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.templating import Jinja2Templates

from src.web.database.user_manager import current_active_user
from src.web.database.users import User, create_db_and_tables
from src.web.routes.users import auth_router, register_router, reset_password_router, verify_router, users_router

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


@users_app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.first_name}, {user.email}!"}


@users_app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()

@users_app.get("/")
def index( request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


templates = Jinja2Templates(directory="www/templates")




if __name__ == "__main__":
    uvicorn.run("users_app:users_app", host="0.0.0.0", port=5000, log_level="info")
