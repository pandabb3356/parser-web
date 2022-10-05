from werkzeug.utils import redirect


def login():
    return redirect("/api/microsoft/auth")
