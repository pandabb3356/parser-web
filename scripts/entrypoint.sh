#!/usr/bin/env bash

export APP_SETTINGS
export PYTHONPATH=$PYTHONPATH:/parser-web
export FLASK_APP

case "$1" in
  parser_web)
    exec flask run --port=5300 --host=0.0.0.0
    ;;
  parser_worker)
    # To give the parser_web time to run initdb.
    sleep 10
    exec python /parser-web/run_worker.py  instant-jobs-normal
    ;;
  db_upgrade)
    exec flask db upgrade
    ;;
  *)
    # The command is something like bash, not an airflow subcommand. Just run it in the right environment.
    exec "$@"
    ;;
esac
