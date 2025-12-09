from dotenv import load_dotenv
load_dotenv()

from celery import Celery
import os

REDIS_HOST: str = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT: int = int(os.environ.get('REDIS_PORT', 6379))


def build_redis_url(db: int) -> str:
    return f"redis://{REDIS_HOST}:{REDIS_PORT}/{db}"

broker_url: str = build_redis_url(0)
backend_url: str = build_redis_url(1)

app = Celery('worker', broker=broker_url, backend=backend_url)



# RabbitMQ config
# QUEUE = "visum.transcription.queue"
# EXCHANGE = "visum.exchange"
# ROUTING_KEY = "visum.transcription"

# RabbitMQ
# username = os.environ.get('RABBITMQ_USERNAME') if app_env == "prod" else "user"
# password = os.environ.get('RABBITMQ_PASSWORD') if app_env == "prod" else "password"
# host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
# port = int(os.environ.get('RABBITMQ_PORT', 5672))
# vhost = os.environ.get('RABBITMQ_VHOST') if app_env == "prod" else "%2F"

# max_attempts = 10
# delay_seconds = 3
# for attempt in range(1, max_attempts + 1):
#     try:
#         logger.info(f"Connecting to RabbitMQ at {host}:{port} (attempt {attempt + 1}/10)...")
#         with socket.create_connection((host, port), timeout=delay_seconds):
#                 print(f"[INFO] RabbitMQ is up at {host}:{port}")
#                 break
#     except Exception as e:
#         if attempt < max_attempts:
#             logger.warning(f"RabbitMQ connection attempt {attempt} failed. Retrying...")
#             logger.info(f"Retrying in {delay_seconds} seconds...")
#             time.sleep(delay_seconds)
#         else:
#             logger.error(f"Failed to connect to RabbitMQ after multiple attempts: {e}")
#             sys.exit(1)



# app.conf.task_acks_late = True
# app.conf.worker_prefetch_multiplier = 1

# # Define Exchange & Queue
# exchange = Exchange(EXCHANGE, type='direct')
# queue = Queue(QUEUE, exchange=exchange, routing_key=ROUTING_KEY)
#
# app.conf.task_queues = [queue]
# app.conf.task_routes = {
#     'tasks.transcribe_and_summarize': {
#         'queue': QUEUE,
#         'routing_key': ROUTING_KEY,
#     },
# }
