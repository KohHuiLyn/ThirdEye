import os

from urllib.parse import urlparse
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']
#url = urlparse(os.environ.get("REDIS_URL"))
#conn = redis.Redis(host=url.hostname, port=url.port, username=url.username, password=url.password, ssl=True, ssl_cert_reqs=None)

# Local
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
