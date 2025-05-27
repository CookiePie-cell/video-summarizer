import json
import logging
import pika
import os
import whisper
import time
import sys
from multiprocessing import Process, current_process
import google.generativeai as genai

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

genai.configure(api_key="API_KEY")

prompt = """"
You are an AI agent tasked with analyzing the following transcript, which has been generated from a video, film, podcast, or other audio source. Your goal is to provide a comprehensive summary and insightful analysis and then write them as JSON string.

Given the transcript, perform the following tasks where each topic is the json key and the value is the answer to the topic:

1. Summary
Write a clear, concise summary of the video content in 1–2 paragraphs.

2. Topic Detection
List the main topics or themes discussed. This would be a json list of string. The string has this format:
"<topic>: <brief description of the topic>"

Provide keywords or tags relevant to the video.

3. Quote Extraction
Identify 3–5 impactful, memorable, or insightful quotes with timestamps (if available). This would be a json list of string.

4. Character or Speaker Insights
Identify speakers or characters (based on names or context). This would be a json list of string.

Describe their roles, opinions, or behaviors briefly.

5. Sentiment Analysis
Indicate the overall sentiment (positive, negative, neutral). This would be a json object with the following format:
{
    "sentiment": "positive/negative/neutral",
    "description": "Brief description of the sentiment"
} 

Note any emotional changes or spikes across the video.

7. Questions and Answers
Extract any key questions posed and the answers provided. This would be a json list of objects with the following format:
[
    {
        "question": "What is the question?",
        "answer": "What is the answer?"
    }
]

If there is no questions or answers provided, just write "There is no questions and answers in this transcription"

8. Named Entity Recognition
List important people, places, organizations, and concepts mentioned. This would be a json object with value as list of string with the following format:
{
    "People": ["Name of the entity"],
    "Places": ["Name of the place"],
    "Organizations": ["Name of the organization"],
    "Concepts": ["Name of the concept]"
}

9. Content Classification
Classify the video type: e.g., tutorial, interview, drama, vlog, documentary. Use the following json format:
{
    "type": "Motivational Speech / Personal Narrative",
    "characteristics": e.g., ["Inspirational, Personal Growth, Storytelling"]
}

Optional: Is it educational, mature, comedic, etc.?

Here is the transcript: 
"""

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
    model = genai.GenerativeModel("gemini-2.0-flash")

    if transcription:
        logger.info(f"[{process_name}] Transcription completed")
        logger.info(f"[{process_name}] Summarizing transcription")
        response = model.generate_content(prompt + transcription)
        logger.info(f"===== [{process_name}] Summary:\n{response.text} =====")
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
