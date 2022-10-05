from conf.base import BaseConfig


class DevelopmentConfig(BaseConfig):
    DEBUG = True

    WEB_HOST_NAME = "http://localhost:5300/"

    MICROSOFT_TENANT_ID = ""
    MICROSOFT_CLIENT_ID = ""
    MICROSOFT_CLIENT_SECRET = ""
    MICROSOFT_SETTINGS = {
        "tenant_id": f"{MICROSOFT_TENANT_ID}",
        "client_id": f"{MICROSOFT_CLIENT_ID}",
        "client_secret": f"{MICROSOFT_CLIENT_SECRET}",
        "authority": f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}",
        "scopes": [
            "User.ReadBasic.All",
            "email",
        ],
        "redirect_uri": f"{WEB_HOST_NAME}api/microsoft/callback",
    }

    # front-end
    FRONTEND_SETTINGS = {
        "host_name": "http://localhost:8080/",
        "endpoint": {"login": "/login", "org_detail": "/org/{org_id}"},
    }

    # line
    LINE_CHANNEL_TOKEN = ""
    LINE_CHANNEL_SECRET = ""
    LINE = {
        "channel_token": f"{LINE_CHANNEL_TOKEN}",
        "channel_secret": f"{LINE_CHANNEL_SECRET}",
        "bot": {
            "text_mapper": {
                "org": "機構",
                "list": "列表",
                "login": "登入",
                "version": "版本",
                "toggle": "toggle",
            }
        },
        "account_link_uri": "https://access.line.me/dialog/bot/accountLink",
    }
