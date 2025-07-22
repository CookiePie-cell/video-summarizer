import tempfile

from dotenv import load_dotenv
load_dotenv()

import os
import whisper
import json
import google.generativeai as genai
from logger_setup import logger
from redis_client import r
from celery_setup import app
from s3_client import s3

app_env = os.environ.get("APP_ENV", "dev")

s3_bucket = os.environ.get("MINIO_BUCKET")

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
        raise

def update_status(job_id, status, result=None, error_message=None):
    r.hset(job_id, mapping={
        'status': status,
        'summaryResult': json.dumps(result) if result else "",
        'errorMessage': str(error_message) if error_message else ""
    })

# object_key = file_name :)))))))))))))
def download_file(object_key):
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_file_path = tmp.name
            logger.info(f"Downloading {object_key}: {tmp_file_path}")

            s3.download_fileobj(s3_bucket, object_key, tmp)
        return tmp_file_path
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise



def summarize(job_id, transcription):
    model = genai.GenerativeModel("gemini-2.0-flash")

    if not transcription:
        error_msg = "Transcription failed or returned empty"
        logger.warning(f"[{job_id}] {error_msg}")
        update_status(job_id, status="FAILED", error_message=error_msg)
        raise ValueError(error_msg)

    try:
        logger.info(f"[{job_id}] Transcription completed")
        logger.info(f"[{job_id}] Summarizing transcription")
        response = model.generate_content(prompt + transcription)
        response_text = response.text

        if response_text.strip().startswith("```json"):
            response_text = response_text[8:-3]

        logger.info(f"[{job_id}] Summary: {response_text}")
        return response_text

    except Exception as e:
        logger.error(f"[{job_id}] Error during summarization: {e}")
        raise

@app.task
def process_task(object_key, job_id):
    logger.info(f"Object key: {object_key}")
    update_status(job_id, status="PROCESSING")
    logger.info(f"[{job_id}] Transcribing: {object_key}")

    try:
        file_path = download_file(object_key)
        transcription = run_whisper(file_path)
        summary = summarize(job_id, transcription)
        update_status(job_id, status="COMPLETED", result=summary)
    except Exception as e:
        logger.error(f"[{job_id}] Error processing task: {e}")
        update_status(job_id, status="FAILED", error_message=str(e))

