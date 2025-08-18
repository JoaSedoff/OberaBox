FROM python:3.11-slim

WORKDIR /app

RUN apt-get -y update
RUN apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config -y
RUN pip install "Flask[async]" python-dotenv python-telegram-bot


ENV TZ="America/Argentina/Buenos_Aires"

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app


CMD ["gunicorn", "-w", "4", "-b", ":8007", "app:app"]