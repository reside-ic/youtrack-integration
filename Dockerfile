FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENV STATIC_INDEX 1
COPY app /app
COPY config.json /app

