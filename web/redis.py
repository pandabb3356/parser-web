from collections import namedtuple
from typing import Union

from redis import Redis


def read_session_redis_config(config: dict) -> dict:
    return {
        "REDIS_HOST": config["REDIS_HOST"],
        "REDIS_PORT": config["REDIS_PORT"],
        "REDIS_DB": config["SESSION_REDIS_DB"],
        "REDIS_PASSWORD": config["REDIS_PASSWORD"],
    }


def read_queue_redis_config(config: dict) -> dict:
    return {
        "REDIS_HOST": config["REDIS_HOST"],
        "REDIS_PORT": config["REDIS_PORT"],
        "REDIS_DB": config["QUEUE_REDIS_DB"],
        "REDIS_PASSWORD": config["REDIS_PASSWORD"],
    }


def create_redis_client_instance(
    config: dict,
    decode_responses: bool = False,
    socket_timeout: Union[float, int] = None,
) -> Redis:
    redis = Redis(
        host=config["REDIS_HOST"],
        port=config["REDIS_PORT"],
        db=config["REDIS_DB"],
        password=config["REDIS_PASSWORD"],
        decode_responses=decode_responses,
        socket_timeout=socket_timeout,
        health_check_interval=config.get("REDIS_HEALTH_CHECK_INTERVAL", 30),
    )

    version = namedtuple("version", ["major", "minor", "patch"])

    redis.version = version(*map(int, redis.info("Server")["redis_version"].split(".")))

    return redis


def create_queue_redis_client_instance(app, decode_responses=False) -> Redis:
    redis_config = read_queue_redis_config(app.config)
    return create_redis_client_instance(
        config=redis_config, decode_responses=decode_responses
    )


def create_session_redis_client_instance(app, decode_responses=False) -> Redis:
    redis_config = read_session_redis_config(app.config)
    return create_redis_client_instance(
        config=redis_config, decode_responses=decode_responses
    )
