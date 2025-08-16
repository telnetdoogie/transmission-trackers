FROM python:3.13.7-alpine3.21 AS builder

# mitigate vulnerabilities
RUN apk update && apk upgrade --no-cache

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13.7-alpine3.21

# mitigate vulnerabilities
RUN apk update && apk upgrade --no-cache

COPY --from=builder /install /usr/local

WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY *.py ./

# Run as nobody user
USER nobody
CMD ["python", "-u", "./app.py"]
