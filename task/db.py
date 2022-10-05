from invoke import task

from task.constants import FLASK_APP
from task.toolkit import get_web_config_path


@task
def new_migrate_file(ctx):
    ctx.run(f"FLASK_APP={FLASK_APP} APP_SETTINGS=\"{get_web_config_path()}\" flask db migrate")


@task
def upgrade(ctx):
    ctx.run(f"FLASK_APP={FLASK_APP} APP_SETTINGS=\"{get_web_config_path()}\" flask db upgrade")
