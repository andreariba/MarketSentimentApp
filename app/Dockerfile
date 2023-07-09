FROM python:3.11.3-slim

RUN apt-get update && \
    apt-get install -y cron libpq-dev gcc

RUN pip install --upgrade pip && \
    pip install \
        python-dotenv \
        pandas \
        psycopg2 \
        dash \
        dash-bootstrap-components \
        transformers \
        xformers \
        torch torchvision torchaudio

WORKDIR /home

COPY . .

CMD ["python", "app.py", "--port", "8060"]

EXPOSE 8060