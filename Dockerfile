FROM python:3.9.7-slim-buster

USER root

RUN apt update -y && \
    apt install -y \
        apache2 \
        apache2-dev \
        gcc \
        libsasl2-dev \
        libssl-dev \
        python-dev

RUN mkdir -p /opt/cons-utility-api
WORKDIR /opt/cons-utility-api

ADD ./requirements.txt /opt/cons-utility-api/requirements.txt
RUN pip install -r requirements.txt

ADD ./application       ./application
ADD ./config.py         ./config.py
ADD ./setup.py          ./setup.py
ADD ./wsgi.py           ./wsgi.py
ADD ./entrypoint.sh     ./entrypoint.sh

RUN mkdir -p /opt/socket && chown -R www-data:www-data /opt/socket

ENV SPREADSHEET_SOCKET_PATH "/opt/socket/application.socket"
ENV SPREADSHEET_XLSX_PATH "/opt/spreadsheet/Redes e Beaglebones.xlsx"

CMD ["/opt/cons-utility-api/entrypoint.sh"]
