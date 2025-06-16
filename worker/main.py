from dotenv import load_dotenv
load_dotenv()

import json
import logging
import pika
import os
import whisper
import time
import sys
from multiprocessing import Process, current_process
import google.generativeai as genai
import redis

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

username = os.environ.get('RABBITMQ_USERNAME')
password = os.environ.get('RABBITMQ_PASSWORD')
host = os.environ.get('RABBITMQ_HOST')

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = int(os.environ.get('REDIS_PORT'))
REDIS_USERNAME = os.environ.get('username')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

prompt = """"
You are an AI agent tasked with analyzing the following transcript, which has been generated from a video, film, podcast, or other audio source. Your goal is to provide a comprehensive summary and insightful analysis and then write them as JSON string.

Given the transcript, perform the following tasks where each topic is the json key and the value is the answer to the topic:

1. summary
Write a clear, concise summary of the video content in 1–4 paragraphs.

2. bulletPoints
Write a list of key points or highlights from the text. This should be a json list of string.

3. topicIdentification
List the main topics or themes discussed. This would be a json list of string. The string has this format:
"<topic>: <brief description of the topic>"

Provide keywords or tags relevant to the video.

4. quoteExtraction
Identify 3–5 impactful, memorable, or insightful quotes. This would be a json list of string.

5. characterIdentification
Identify speakers or characters (based on names or context). This would be a json list of string.

Describe their roles, opinions, or behaviors briefly.

6. sentimentAnalysis
Indicate the overall sentiment (positive, negative, neutral). This would be a json object with the following format:
{
    "sentiment": "positive/negative/neutral",
    "description": "Brief description of the sentiment"
} 

Note any emotional changes or spikes across the video.

7. qna
Extract any key questions posed and the answers provided. This would be a json list of objects with the following format:
[
    {
        "question": "What is the question?",
        "answer": "What is the answer?"
    }
]

If there is no questions or answers provided, use an empty list.

8. namedEntities
List important people, places, organizations, and concepts mentioned. This would be a json object with value as list of string with the following format:
{
    "people": ["Name of the entity"],
    "places": ["Name of the place"],
    "organizations": ["Name of the organization"],
}

9. contentClassification
Classify the audio genre: e.g., tutorial, interview, drama, vlog, documentary. Use the following json format:
{
    "type": e.g., "Motivational Speech",
    "characteristics": e.g., ["Inspirational, Personal Growth, Storytelling"]
}

PS: Do not include any additional text or explanations in your response. Just provide pure JSON String with the keys and values as specified above.
Here is the transcript: 
"""

def run_whisper(file_path):
    try:
        logger.info(f"Running Whisper on file: {file_path}")
        model = whisper.load_model("tiny")
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        logger.error(f"Whisper error: {e}")
        return None

def process_task(body_json):
    process_name = current_process().name
    file_path = body_json.get('filePath')
    job_id = f"job:{body_json.get('jobId')}"
    r.hset(job_id, mapping={
        'status': 'PROCESSING',
    })
    logger.info(f"[{process_name}] Transcribing: {file_path}")
    transcription = run_whisper(file_path)
    model = genai.GenerativeModel("gemini-2.0-flash")

    if transcription:
        logger.info(f"[{process_name}] Transcription completed")
        logger.info(f"[{process_name}] Summarizing transcription")
        response = model.generate_content(prompt + transcription)
        response_text = response.text
        if response_text[0:8].strip() == "```json":
            response_text = response_text[8:-3]
        r.hset(job_id, mapping={
            'status': 'COMPLETED',
            "summaryResult": response_text,
        })
        logger.info(f"[{process_name}] Summary: {response_text}")
        # logger.info(f"===== [{process_name}] Summary:\n{response.text} =====")
    else:
        r.hset(job_id, mapping={
            'status': 'FAILED',
            'errorMessage': 'Transcription failed'
        })
        logger.warning(f"[{process_name}] Transcription failed for {file_path}")

def on_message(channel, method_frame, header_frame, body):
    try:
        body_json = json.loads(body)
        file_path = body_json.get('filePath')
        if not file_path:
            logger.warning("No filePath found in message. Skipping.")
            channel.basic_ack(method_frame.delivery_tag)
            return

        p = Process(target=process_task, args=(body_json,))
        p.start()

        # Immediately ACK the message to avoid duplicate processing
        logger.info("Acknowledging message...")
        channel.basic_ack(method_frame.delivery_tag)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        channel.basic_nack(method_frame.delivery_tag, requeue=False)


max_attempts = 10
delay_seconds = 3

# --- Redis setup ---
r = None
for attempt in range(1, max_attempts + 1):
    try:
        logger.info(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT} (attempt {attempt + 1}/10)...")
        # r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
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

# --- RabbitMQ setup ---
credentials = pika.PlainCredentials(username, password)

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
            logger.info(f"RabbitMQ connection attempt {attempt} failed. Retrying...")
            logger.info(f"Retrying in {delay_seconds} seconds...")
            time.sleep(delay_seconds)
        else:
            logger.error(f"Failed to connect to RabbitMQ after multiple attempts: {e}")
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
