from flask import Blueprint

bp = Blueprint("api", __name__)

from . import (
    org,
    parser,
    services,
    login,
    microsoft,
    linebot,
)
