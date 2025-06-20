#FROM python:3.11-slim
#
#RUN apt-get update && apt-get install -y ffmpeg && apt-get clean
#
#WORKDIR /app
#
#COPY requirements.txt .
#
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . .
#
## Run the app
#CMD ["python", "main.py"]

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Pre-install torch and numpy (to avoid redownloading during whisper install)
RUN pip install --no-cache-dir \
    numpy==1.26.3 \
    torch==2.2.2+cpu torchvision==0.17.2+cpu torchaudio==2.2.2 \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .

# Install controlled deps normally
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir openai-whisper

# clean up
RUN rm -rf ~/.cache/pip

COPY . .

CMD ["python", "main.py"]




