FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --require-hashes -r requirements.txt && useradd --uid 10001 --create-home app && mkdir -p /var/lib/ef-sinn-inquiry && chown app:app /var/lib/ef-sinn-inquiry
COPY inquiry_service ./inquiry_service
COPY wsgi.py ./
USER 10001:10001
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "1", "--timeout", "60", "--graceful-timeout", "30", "--error-logfile", "-", "wsgi:app"]
