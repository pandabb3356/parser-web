from typing import NamedTuple, Tuple

from web.models.user import User
from web.user.repository import get_user_by_user_no


class UserInfo(NamedTuple):
    user_no: str
    name: str
    email: str
    active: bool


def get_or_generate_user(user_info: UserInfo) -> Tuple[bool, User]:
    existed_user = get_user_by_user_no(user_info.user_no)
    return bool(existed_user), existed_user or generate_user(user_info)


def generate_user(user_info: UserInfo) -> User:
    return User(
        user_no=user_info.user_no,
        email=user_info.email,
        name=user_info.name,
        active=user_info.active,
    )
