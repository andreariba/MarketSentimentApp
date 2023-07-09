FROM python:3.11.3-slim

RUN apt-get update && \
    apt-get install -y cron libpq-dev gcc syslog-ng

RUN pip install --upgrade pip && \
    pip install \
    pandas \
    python-dotenv \
    psycopg2 \
    dash \
    dash-bootstrap-components \
    transformers \
    xformers \
    torch torchvision torchaudio


COPY . .

RUN echo "30 23 * * * root python /update.py >> /var/log/cron.log 2>&1" >> /etc/crontab

RUN touch /var/log/cron.log

CMD ["/bin/bash", "/run.sh"]