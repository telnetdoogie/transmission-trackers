FROM dhi.io/python:3-alpine3.23-dev AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM dhi.io/python:3-alpine3.23

COPY --from=builder /install /usr/local

WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY *.py ./

# Run as nobody user
USER nobody
CMD ["python", "-u", "./app.py"]
