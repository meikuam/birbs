import contextlib
import uuid
from typing import Optional, Union, Dict, Any

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, InvalidPasswordException, UUIDIDMixin
from fastapi_users.authentication import JWTStrategy, CookieTransport, AuthenticationBackend

from src.web.database.users import User, get_user_db
from src.web.models.users import UserCreate
from src.utils import settings


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.fastapi["secret"]
    verification_token_secret = settings.fastapi["secret"]

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters")
        if len(password) > 25:
            raise InvalidPasswordException(
                reason="Password should be less then 25 characters")
        if len(user.email) > 320:
            raise InvalidPasswordException(
                reason="email length should be less then 320 characters https://www.rfc-editor.org/rfc/rfc3696")
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail")

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_update(
        self,
        user: User,
        update_dict: Dict[str, Any],
        request: Optional[Request] = None
    ):
        print(f"User {user.id} has been updated with {update_dict}.")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        # we can send email after success verify
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_verify(
        self, user: User, request: Optional[Request] = None
    ):
        print(f"User {user.id} has been verified")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        # we should send email to user with token
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has reset their password.")

    async def on_before_delete(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} is going to be deleted")

    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} is successfully deleted")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.fastapi["secret"],
        lifetime_seconds=settings.fastapi["token_lifetime"],
        token_audience=["fastapi-users:auth"])


cookie_transport = CookieTransport(
    cookie_name="fastapiuserauth",
    cookie_max_age=settings.fastapi["token_lifetime"],
    cookie_secure=False
)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(optional=True)
current_active_user = fastapi_users.current_user(active=True)
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
