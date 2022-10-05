import os
import socket

from flask import render_template, redirect

from web.views.root import bp


@bp.route('/', methods=["GET"])
def get_root_index_view():
    return render_template('root/index.html')
