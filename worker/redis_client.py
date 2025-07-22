from dotenv import load_dotenv
load_dotenv()

import redis
import os
import time
import sys
from logger_setup import logger

app_env = os.environ.get("APP_ENV", "dev")

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_USERNAME = os.environ.get('REDIS_USERNAME') if app_env == "prod" else None
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD') if app_env == "prod" else None

max_attempts = 10
delay_seconds = 3

# --- Redis setup ---
r = None
for attempt in range(1, max_attempts + 1):
    try:
        logger.info(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT} (attempt {attempt + 1}/10)...")
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=2,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        logger.info("Connected to Redis.")
        r.ping()  # Test connection
        break
    except redis.ConnectionError as e:
        r = None
        if attempt < max_attempts:
            logger.warning(f"Redis connection attempt {attempt} failed. Retrying...")
            logger.info(f"Retrying in {delay_seconds} seconds...")
            time.sleep(delay_seconds)
        else:
            logger.error(f"Failed to connect to Redis after multiple attempts: {e}")
            sys.exit(1)