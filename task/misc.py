import os
import signal
import subprocess

from invoke import task

from task.constants import FLASK_APP
from task.toolkit import get_web_config_path


@task
def server(ctx):
    ctx.run(f"FLASK_APP={FLASK_APP} APP_SETTINGS=\"{get_web_config_path()}\" flask run --port=5300")


@task
def worker(ctx):
    process = subprocess.Popen(f'APP_SETTINGS={get_web_config_path()} python ./run_worker.py instant-jobs-normal',
                               shell=True, preexec_fn=os.setsid)
    try:
        while True:
            input()
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        os.killpg(process.pid, signal.SIGTERM)


@task
def shell(ctx):
    ctx.run(f"FLASK_APP={FLASK_APP} APP_SETTINGS=\"{get_web_config_path()}\" flask shell")
