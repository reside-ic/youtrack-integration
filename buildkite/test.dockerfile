FROM python

COPY ./requirements-docker.txt /workspace/requirements-docker.txt
COPY ./requirements-dev.txt /workspace/requirements-dev.txt

WORKDIR /workspace

RUN pip3 install -r requirements-docker.txt
RUN pip3 install -r requirements-dev.txt

COPY . /workspace
RUN python3 -m pytest
