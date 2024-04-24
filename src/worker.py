import logging
import os

import redis
import rq

logging.basicConfig(level=logging.INFO)

with rq.Connection(redis.from_url(os.environ.get("RQ_REDIS_URL"))):
    worker = rq.Worker(["default"])
    worker.work()
