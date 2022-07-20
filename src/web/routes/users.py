# import os
# import requests
# import uuid
# from typing import Optional
# from fastapi import Request, Depends, Response
# from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin
from fastapi_users.exceptions import UserAlreadyExists
from src.utils import settings

from sqlalchemy import select, func
from src.web.models.users import UserCreate, UserRead, UserUpdate
from src.web.database.user_manager import auth_backend, fastapi_users, get_user_manager_context
from src.web.database.users import User, get_async_session_context, get_user_db_context

auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(UserRead, UserCreate)
reset_password_router = fastapi_users.get_reset_password_router()
verify_router = fastapi_users.get_verify_router(UserRead)
users_router = fastapi_users.get_users_router(UserRead, UserUpdate)


async def create_user(email: str, password: str, is_superuser: bool = False):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(
                        UserCreate(
                            email=email,
                            password=password,
                            is_superuser=is_superuser
                        )
                    )
                    # await session.commit()
                    print(f"User created {user}")
    except UserAlreadyExists:
        print(f"User {email} already exists")


async def create_first_admin() -> bool:
    try:
        async with get_async_session_context() as session:

            count = (
                await session.execute(
                    select(func.count()).select_from(select(User).filter_by(is_superuser=True))
                )
            ).scalar_one()
            print("count", count)
        if count == 0:
            print("create user")
            await create_user(
                email=settings.fastapi["admin_email"],
                password=settings.fastapi["admin_password"],
                is_superuser=True)
        return True
    except Exception as e:
        print("exception", e)
        return False