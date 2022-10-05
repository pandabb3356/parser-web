from enum import Enum, unique
from queue import Queue
from uuid import uuid4

from rq import Queue as RQ
from rq.job import JobStatus

from web.redis import create_queue_redis_client_instance


@unique
class QueuePriority(Enum):
    high = 1
    normal = 2


class QueueWrapper(object):
    def __init__(self, name):
        self.name = name
        self.queue = {}

    def init_app(self, app):
        if app.config["QUEUE_BACKEND"] == "redis":
            redis = create_queue_redis_client_instance(app)

            for priority in QueuePriority:
                self.queue[priority] = RQ(
                    name="{}-{}".format(self.name, priority.name),
                    default_timeout=app.config.get("RQ_DEFAULT_TIMEOUT"),
                    connection=redis,
                )
        else:
            for priority in QueuePriority:
                self.queue[priority] = InMemoryQueue()

    def enqueue(self, job_func, *args, **kwargs):
        priority = kwargs.pop("priority", QueuePriority.normal)
        return self.queue[priority].enqueue(job_func, *args, **kwargs)

    def get_jobs(self, priority=QueuePriority.normal):
        return self.queue[priority].get_jobs()

    def empty(self, priority=QueuePriority.normal):
        return self.queue[priority].empty()

    def get_job(self, job_id, priority=QueuePriority.normal):
        return self.queue[priority].fetch_job(job_id)

    def get_job_status(self, job_id, priority=QueuePriority.normal):
        job = self.get_job(job_id, priority)
        if job:
            return {"status": job.get_status(), "result": job.result}


class InMemoryJob(dict):
    def __init__(self, func, *args, **kwargs):
        self.id = str(uuid4())
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = None
        self.result = None
        super().__init__()

    def get_id(self):
        return self.id

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def perform(self):
        if callable(self.func):
            self.set_status(JobStatus.STARTED)
            self.result = self.func(*self.args, **self.kwargs)
            self.set_status(JobStatus.FINISHED)
            return self.result


class InMemoryQueue(object):
    def __init__(self):
        self.instance = Queue()

    def enqueue(self, *args, **kwargs):
        kwargs.pop("timeout", None)
        job = InMemoryJob(*args, **kwargs)
        job.update(
            {
                "job_func": args[0],
                "id": args[1] if len(args) >= 2 else None,
                "org_id": args[-1],
                "all_args": args,
            }
        )
        self.instance.put(job)
        job.status = JobStatus.QUEUED
        return job

    def get_jobs(self):
        return list(self.instance.queue)

    def empty(self):
        self.instance = Queue()

    def fetch_job(self, job_id):
        for job in self.instance.queue:
            if job.id == job_id:
                return job


instant_jobs_queue = QueueWrapper("instant-jobs")
