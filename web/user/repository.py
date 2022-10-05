from typing import Optional

from web.models.user import User


def get_user_by_id(user_id: int) -> Optional[User]:
    return User.query.get(user_id)


def get_user_by_user_no(user_no: str) -> Optional[User]:
    return User.query.filter(User.user_no == user_no).first()


def get_user_by_email(email: str) -> Optional[User]:
    return User.query.filter(User.email == email).first()
