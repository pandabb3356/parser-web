import base64
import hmac
import json
import time
from datetime import timedelta, datetime
from hashlib import sha1
from uuid import uuid4

from flask import current_app
from flask.sessions import SessionMixin, SessionInterface
from redis import Redis, ReadOnlyError
from werkzeug.datastructures import CallbackDict

from web.redis import create_session_redis_client_instance
from web.util import utctimestamp_by_second

SESSION_SID_VERSION = "V2"
SESSION_PREFIX = "parser-web-session:"


def hmac_sha1(secret_key, data):
    data = bytes(str(data), "utf8")
    hashed = hmac.new(bytes(secret_key, "utf8"), data, sha1)
    return base64.urlsafe_b64encode(hashed.digest()).decode().rstrip("\n=")


def generate_sid():
    return "{}-{}".format(SESSION_SID_VERSION, str(uuid4()))


def secure_uid(session):
    uid = session.get("user_id", "0")
    b64uid = base64.urlsafe_b64encode(bytes(str(uid), "utf8")).decode().strip("\n=")
    time_delta = (
        timedelta(days=1)
        if session.permanent
        else get_session_non_permanent_time(session)
    )
    timestamp = utctimestamp_by_second(datetime.utcnow() + time_delta)
    sig = hmac_sha1(
        current_app.config.get("SECRET_KEY", ""), "{}@{}".format(uid, timestamp)
    )
    return "{}.{}.{}".format(b64uid, timestamp, sig)


def get_session_non_permanent_time(session):
    session_non_permanent_time = current_app.config.get(
        "SESSION_NON_PERMANENT_TIME", 86400
    )
    session_anonymous_time = current_app.config.get("SESSION_ANONYMOUS_TIME", 60)
    time_in_seconds = (
        session_anonymous_time
        if "user_id" not in session
        else session_non_permanent_time
    )
    return timedelta(seconds=time_in_seconds)


def get_redis_expiration_time(app, session):
    if session.permanent:
        return app.permanent_session_lifetime
    return get_session_non_permanent_time(session)


class Session(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False, permanent=False):
        def on_update(self):
            self.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False
        self.permanent = permanent


class RedisSessionInterface(SessionInterface):
    serializer = json
    session_class = Session

    def __init__(self, redis=None, prefix=SESSION_PREFIX):
        if redis is None:
            redis = Redis()
        self.redis = redis
        self.prefix = prefix

    @staticmethod
    def _get_session_key_and_permanent_option(app, request):
        session_key = request.headers.get("X-SESSION-ID")

        if session_key:
            permanent = True
        else:
            session_key = request.cookies.get(app.session_cookie_name)
            permanent = False

        return session_key, permanent

    def _new_session(self, _sid, _permanent):
        return self.session_class(sid=_sid, new=True, permanent=_permanent)

    def _existing_session(self, _data, _sid, _permanent):
        return self.session_class(initial=_data, sid=_sid, permanent=_permanent)

    def open_session(self, app, request):
        session_key, permanent = self._get_session_key_and_permanent_option(
            app, request
        )

        if not session_key or (
            not session_key.startswith(SESSION_SID_VERSION)
            and not session_key.startswith("V1-")
        ):
            return self._new_session(generate_sid(), permanent)

        sid = session_key.split(".")[0]
        val = self.redis.get(self.prefix + sid)
        if val is not None:
            data = self.serializer.loads(val)
            return self._existing_session(data, sid, permanent)
        return self._new_session(sid, permanent)

    def save_session(self, app, session, response):
        session["last_visit"] = int(time.time())

        self._update_redis(app, session)

        session_key = "{}.{}".format(session.sid, secure_uid(session))
        self._update_cookie(app, response, session, session_key)
        self._update_header_for_mobile(response, session_key)

    def _clean_redis_and_cookie(self, app, response, session):
        self.write_wrapper(self.redis.delete, self.prefix + session.sid)
        response.delete_cookie(
            app.session_cookie_name, domain=self.get_cookie_domain(app)
        )

    def _update_redis(self, app, session):
        redis_exp = get_redis_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.write_wrapper(
            self.redis.setex,
            self.prefix + session.sid,
            int(redis_exp.total_seconds()),
            val,
        )

    def _update_cookie(self, app, response, session, session_key):
        cookie_exp = self.get_expiration_time(app, session)

        response.set_cookie(
            app.session_cookie_name,
            session_key,
            expires=cookie_exp,
            httponly=self.get_cookie_httponly(app),
            domain=self.get_cookie_domain(app),
        )

    @staticmethod
    def _update_header_for_mobile(response, session_key):
        response.headers["X-SESSION-ID"] = session_key

    def write_wrapper(self, write_method, *args):
        for i in range(3):
            try:
                write_method(*args)
                break
            except ReadOnlyError:
                self.redis.connection_pool.reset()
                time.sleep(1)

    def _collect_session_keys(self):
        pattern = f"{SESSION_PREFIX}*"
        return self.redis.keys(pattern)

    def is_session_exist(self, session_key):
        if not session_key or not session_key.startswith(SESSION_SID_VERSION):
            return False

        sid = session_key.split(".")[0]
        val = self.redis.get(self.prefix + sid)
        if val:
            data = self.serializer.loads(val)
            from web.models.user import User
            from flask_login import login_user

            user = User.query.get(int(data["user_id"]))
            login_user(user)

        return val is not None


def init_app(app):
    if app.config.get("SESSION_BACKEND") == "redis":
        redis = create_session_redis_client_instance(app, decode_responses=True)
        app.session_interface = RedisSessionInterface(redis)
    else:
        pass  # use default backend
