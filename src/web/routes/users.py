import os
import requests
import uuid
from typing import Optional
from fastapi import Request, Depends, Response
from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin

from src.utils import settings


from src.web.models.users import UserCreate, UserRead, UserUpdate
from src.web.database.user_manager import auth_backend, current_active_user, fastapi_users


auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(UserRead, UserCreate)
reset_password_router = fastapi_users.get_reset_password_router()
verify_router = fastapi_users.get_verify_router(UserRead)
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
