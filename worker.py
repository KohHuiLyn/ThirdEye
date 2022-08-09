import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL','redis://:pc58093e5f59de50a88b132884068ae62f73cbbd09fcfc47cd964f61ef8766663@ec2-34-192-110-76.compute-1.amazonaws.com:18130')
# Local
# redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()