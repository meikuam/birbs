import os

from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.password import get_password_hash
from src.database.base import (
    engine,
    database,
    Session
)
from src.web.models.users import (
    UserDB,
    UserCreate,
    UserTable,
    UserUpdate,
    Base
)

Base.metadata.create_all(engine)
users = UserTable.__table__
user_db = SQLAlchemyUserDatabase(UserDB, database, users)


async def create_first_admin() -> bool:
    try:
        session = Session()
        count = session.query(UserTable).filter_by(is_superuser=True).count()
        if count == 0:
            user = UserCreate(
                email=os.getenv('API_ADMIN_EMAIL', 'admin@admin.com'),
                password=os.getenv('API_ADMIN_PASSWORD', 'adminpassword')
            )

            hashed_password = get_password_hash(user.password)
            db_user = UserDB(
                **user.create_update_dict(), hashed_password=hashed_password
            )
            created_user = await user_db.create(db_user)
            if created_user:
                created_user.is_superuser = True
                updated_user = await user_db.update(created_user)
        session.commit()
        session.close()
        return True
    except Exception as e:
        return False
