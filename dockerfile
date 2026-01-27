
FROM python:3.12-slim

RUN pip install docker

WORKDIR /app

COPY watcher.py /app/watcher.py

CMD ["python", "/app/watcher.py"]
