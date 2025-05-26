import json
import logging
import pika
import os
import whisper
import time
import sys
from multiprocessing import Process, current_process

# Simple logger setup
logger = logging.getLogger("transcriber")
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# RabbitMQ config
QUEUE = "visum.transcription.queue"
EXCHANGE = "visum.exchange"
ROUTING_KEY = "visum.transcription"

username = os.environ.get('RABBITMQ_USERNAME', 'user')
password = os.environ.get('RABBITMQ_PASSWORD', 'password')
host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')

def run_whisper(file_path):
    try:
        logger.info(f"Running Whisper on file: {file_path}")
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        logger.error(f"Whisper error: {e}")
        return None

def process_task(file_path):
    process_name = current_process().name
    logger.info(f"[{process_name}] Transcribing: {file_path}")
    transcription = run_whisper(file_path)
    if transcription:
        logger.info(f"[{process_name}] Transcription completed: {transcription}")
    else:
        logger.warning(f"[{process_name}] Transcription failed for {file_path}")

def on_message(channel, method_frame, header_frame, body):
    try:
        body_json = json.loads(body)
        file_path = body_json.get('filePath')
        if not file_path:
            logger.warning("No filePath found in message. Skipping.")
            channel.basic_ack(method_frame.delivery_tag)
            return

        # Spawn a new process for the task
        p = Process(target=process_task, args=(file_path,))
        p.start()

        # Immediately ACK the message to avoid duplicate processing
        # (You could also delay ack until after transcription, if you want stronger reliability)
        logger.info("Acknowledging message...")
        channel.basic_ack(method_frame.delivery_tag)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        channel.basic_nack(method_frame.delivery_tag, requeue=False)

# --- RabbitMQ setup ---
credentials = pika.PlainCredentials(username, password)
max_attempts = 10
delay_seconds = 3
time.sleep(delay_seconds)

connection = None
for attempt in range(1, max_attempts + 1):
    try:
        logger.info(f"Connecting to RabbitMQ (attempt {attempt}/{max_attempts})...")
        connection_params = pika.ConnectionParameters(
            host=host,
            port=5672,
            virtual_host="/",
            credentials=credentials,
            heartbeat=5
        )
        connection = pika.BlockingConnection(connection_params)
        logger.info("Connected to RabbitMQ.")
        break
    except Exception as e:
        logger.warning(f"Connection attempt {attempt} failed: {e}")
        if attempt < max_attempts:
            logger.info(f"Retrying in {delay_seconds} seconds...")
            time.sleep(delay_seconds)
        else:
            logger.error("All connection attempts failed.")
            sys.exit(1)

channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True, auto_delete=False)
channel.queue_declare(queue=QUEUE, durable=True, auto_delete=False)
channel.queue_bind(queue=QUEUE, exchange=EXCHANGE, routing_key=ROUTING_KEY)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE, on_message_callback=on_message)

try:
    logger.info(f"Waiting for messages on queue: {QUEUE}")
    channel.start_consuming()
except KeyboardInterrupt:
    logger.info("Shutdown requested. Stopping consumer...")
    channel.stop_consuming()

connection.close()
logger.info("Connection closed. Worker exiting.")
