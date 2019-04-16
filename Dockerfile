FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./requirements-docker.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV STATIC_INDEX 1
COPY ./src /app
