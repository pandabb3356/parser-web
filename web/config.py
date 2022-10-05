ENCRYPT_SCHEME = "sha256_crypt"
ENCRYPT_ROUNDS = 1000


def get_web_host(app_config: dict) -> str:
    return app_config.get("WEB_HOST_NAME") or ""
