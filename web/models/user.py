from flask_security import UserMixin
from passlib.context import CryptContext

from web import db
from web.config import ENCRYPT_SCHEME, ENCRYPT_ROUNDS


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_no = db.Column(db.Unicode(255), nullable=False)
    password = db.Column(db.Unicode(255), nullable=True)
    name = db.Column(db.Unicode(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    email = db.Column(db.Unicode(255), nullable=False)

    roles = []  # TODO: Create roles

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def is_active(self):
        return self.active

    def verify_password(self, password):
        return CryptContext(ENCRYPT_SCHEME).verify(password, self.password)

    @classmethod
    def encrypt_password(cls, password):
        return CryptContext(ENCRYPT_SCHEME).encrypt(password, rounds=ENCRYPT_ROUNDS)

    def update_password(self, new_password):
        self.password = User.encrypt_password(new_password)
