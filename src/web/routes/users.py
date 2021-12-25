import os
import requests
from src.utils import base_url
from fastapi_users.authentication import JWTAuthentication
from fastapi_users import FastAPIUsers
from fastapi import Request, Depends, Response

SECRET = os.getenv('API_SECRET', "SECRET")

from src.database.users import user_db

from src.web.models.users import (
    User,
    UserDB,
    UserCreate,
    UserUpdate
)


def on_after_register(user: UserDB, request: Request):
    print(f"User {user.id} has registered.")


def on_after_forgot_password(user: UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


jwt_authentication = JWTAuthentication(
    secret=SECRET,
    lifetime_seconds=3600,
    tokenUrl=requests.utils.urlparse(base_url()).path + "/auth/jwt/login"
)

fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

jwt_auth_router = fastapi_users.get_auth_router(jwt_authentication)

@jwt_auth_router.post("/refresh")
async def refresh_jwt(response: Response, user=Depends(fastapi_users.get_current_active_user)):
    return await jwt_authentication.get_login_response(user, response)

register_router = fastapi_users.get_register_router(on_after_register)

reset_password_router = fastapi_users.get_reset_password_router(
        SECRET, after_forgot_password=on_after_forgot_password
)

users_router = fastapi_users.get_users_router()
