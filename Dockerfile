FROM python:3.9.19-alpine as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY add_trackers.py /app

WORKDIR /app
CMD ["python", "add_trackers.py"]