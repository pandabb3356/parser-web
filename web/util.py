import io
import re
import unicodedata
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

import pandas as pd
from flask import current_app
from werkzeug.http import dump_options_header
from werkzeug.urls import url_quote

from web.constants import FILE_TIME_DISPLAY


def handle_header_filename(response, filename):
    file_names = OrderedDict()
    try:
        filename_latin = filename.encode("latin-1")
    except UnicodeEncodeError:
        file_names["filename"] = unicodedata.normalize("NFKD", filename).encode(
            "latin-1", "ignore"
        )
        file_names["filename*"] = "UTF-8''{}".format(url_quote(filename))
    else:
        file_names["filename"] = filename_latin

    response.headers.set(
        "Content-Disposition", dump_options_header("attachment", file_names)
    )


def make_df_excel_response(df_sets, file_name):
    from flask import Response

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")

    for (df, sheet_name) in df_sets:
        df.to_excel(writer, sheet_name=sheet_name)

    writer.save()
    output.seek(0)

    response = Response()
    response.status_code = 200
    response.data = output.getvalue()
    response.headers[
        "Content-type"
    ] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    handle_header_filename(response, "{}.xlsx".format(file_name))

    return response


def generate_current_time_for_file_name():
    now = datetime.utcnow() + timedelta(
        hours=current_app.config.get("UTC_TIME_OFFSET", 0)
    )
    return now.strftime(FILE_TIME_DISPLAY)


def utctimestamp_by_second(utc_date_time):
    return int((utc_date_time.replace(tzinfo=timezone.utc)).timestamp())


def remove_emoji(source_text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", source_text)
