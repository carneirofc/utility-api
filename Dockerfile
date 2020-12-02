FROM centos/python-38-centos7:20200624-7b63bb4

MAINTAINER Claudio Carneiro <claudio.carneiro@lnls.br>

USER root

RUN yum update -y && yum install -y httpd httpd-devel

RUN mkdir -p /opt/cons-utility-api
WORKDIR /opt/cons-utility-api

ADD ./requirements.txt /opt/cons-utility-api/requirements.txt
RUN pip install -r requirements.txt

ADD ./cons-common /opt/cons-utility-api/cons-common
RUN cd /opt/cons-utility-api/cons-common/ && pip install . && cd test/ && ./test_spreadsheet.py

ADD ./application       ./application
ADD ./config.py         ./config.py
ADD ./setup.py          ./setup.py
ADD ./wsgi.py           ./wsgi.py
ADD ./entrypoint.sh     ./entrypoint.sh

RUN mkdir -p /opt/socket && useradd -U www-data && chown -R www-data:www-data /opt/socket

ENV SPREADSHEET_SOCKET_PATH "/opt/socket/application.socket"
ENV SPREADSHEET_XLSX_PATH "/opt/spreadsheet/Redes e Beaglebones.xlsx"

CMD ["/opt/cons-utility-api/entrypoint.sh"]
