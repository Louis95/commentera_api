# Base image with Python 3.11.4 and dependencies
FROM python:3.11.4-slim-buster AS base

RUN apt-get update \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home Commentera-API \
    && chown -R Commentera-API /home/Commentera-API
WORKDIR /home/Commentera-API

USER Commentera-API

ENV PATH="/home/Commentera-API/.local/bin:$PATH"

COPY --chown=Commentera-API requirements.txt .

WORKDIR /Commentera-API

COPY --chown=Commentera-API . .


EXPOSE 8000

RUN pip install --no-cache-dir -r requirements.txt



# Start the app
#CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
