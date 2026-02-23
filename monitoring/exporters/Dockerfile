FROM python:3.12-slim

WORKDIR /app

RUN pip install prometheus-client

COPY dagster_metrics_exporter.py .

CMD ["python", "dagster_metrics_exporter.py"]
