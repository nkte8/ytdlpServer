import logging
import os

import redis
import rq

logging.basicConfig(level=logging.INFO)

worker = rq.Worker(
    ["default"],
    connection=redis.from_url(os.environ.get("RQ_REDIS_URL")),
)
worker.work()
