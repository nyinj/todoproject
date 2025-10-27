# -------- STAGE 1: Builder --------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# -------- STAGE 2: Runtime --------
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /install /usr/local
COPY . /app/

EXPOSE 8000

# Django runs inside the container on port 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
