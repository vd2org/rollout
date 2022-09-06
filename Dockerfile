FROM python:3.10

RUN curl https://get.docker.com | sh

COPY app/requirements.txt /requirements.txt

RUN pip install -r /requirements.txt --no-cache-dir -q --compile

COPY app /opt/app
WORKDIR /opt/app

ENV PATH="${PATH}:/opt/app"

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1
ENV TZ=UTC

EXPOSE 8080

CMD ["uvicorn", "engine:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--log-config", "./logging.json"]
