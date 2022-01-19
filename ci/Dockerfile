FROM debian:11

RUN apt-get update -y \
    && apt-get install -y \
        postgresql-client \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app/

COPY requirements.txt ./
RUN pip3 install -r /opt/app/requirements.txt
