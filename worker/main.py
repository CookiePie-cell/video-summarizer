from fastapi import FastAPI
from pydantic import BaseModel
from celery_worker import process_task

app = FastAPI()

class TranscribeAndSummeryRequest(BaseModel):
    object_key: str
    job_id: str
    status: str

@app.post("/transcribe-and-summarize")
async def transcribe_and_summary(request: TranscribeAndSummeryRequest):
    job_id = f"job:{request.job_id}"
    process_task.delay(request.object_key, job_id)

    return {"status": request.status, "job_id": request.job_id}
