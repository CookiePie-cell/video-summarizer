# 📹 Visum - AI Video Summarizer


**Visum** is a powerful, full-stack application that automatically transcribes and summarizes video and audio files. It uses an asynchronous microservices architecture to handle heavy AI processing without blocking the user interface.

<img width="1919" height="866" alt="image" src="https://github.com/user-attachments/assets/94bc1531-fa4c-45ca-8e6b-47d3f26c6e99" />

<img width="1895" height="865" alt="Screenshot 2025-12-17 130356" src="https://github.com/user-attachments/assets/cff9d69c-3cc9-4d9a-bf34-d19e3add002d" />

<img width="1911" height="862" alt="Screenshot 2025-12-17 130532" src="https://github.com/user-attachments/assets/177dd06e-c526-4e92-9c99-07c5a5df2dde" />


## 🏗 Architecture

The system is composed of four main services running in Docker containers:

1.  **Frontend (Next.js):** User interface for uploading files and viewing summaries.
2.  **Backend (Spring Boot):** REST API that manages job coordination and generates Presigned URLs.
3.  **Worker (Python Celery):** Asynchronous worker that performs the heavy lifting (transcription & summarization via Gemini/Whisper).
4.  **Storage & Broker:**
    * **MinIO:** Self-hosted S3-compatible object storage for video files.
    * **Redis:** Message broker for the job queue and temporary state storage.

## 🚀 Tech Stack

### Frontend
![Next JS](https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

### Backend
![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-%236DB33F.svg?style=for-the-badge&logo=spring-boot&logoColor=white)

### AI Engine
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Celery](https://img.shields.io/badge/celery-%2337814A.svg?style=for-the-badge&logo=celery&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![OpenAI Whisper](https://img.shields.io/badge/OpenAI%20Whisper-412991?style=for-the-badge&logo=openai&logoColor=white)

### Infrastructure
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-c72c48?style=for-the-badge&logo=minio&logoColor=white)
```mermaid
