FROM python:3.13.1-alpine3.21 as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13.1-alpine3.21

COPY --from=builder /install /usr/local

WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY *.py .

# Run as nobody user
USER nobody
CMD ["python", "-u", "./add_trackers.py"]
