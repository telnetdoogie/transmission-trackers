FROM python:3-alpine as builder

RUN apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3-alpine

COPY --from=builder /install /usr/local

WORKDIR /app

COPY add_trackers.py .
CMD ["python", "add_trackers.py"]