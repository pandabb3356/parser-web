import sys

from rq import Worker

from web import create_app
from web.redis import create_queue_redis_client_instance


if __name__ == '__main__':
    app = create_app()

    redis = create_queue_redis_client_instance(app)

    queues = sys.argv[1:] or ['default']
    worker = Worker(queues, connection=redis)
    worker.work()
