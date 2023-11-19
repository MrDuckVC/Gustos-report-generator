ARG VERSION=slim

FROM python:3.11-slim as build

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        pkg-config \
        libmariadb-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --upgrade pip

RUN pip3 install --no-cache-dir --no-warn-script-location \
        uwsgi \
        Django>=4.2.5 \
        djangorestframework>=3.14.0 \
        django-mysql>=4.10.0 \
        mysqlclient>=2.2.0 \
        Pillow>=9.5.0 \
        openpyxl>=3.1.2 \
        requests>=2.31.0 \
        celery>=5.3.1 \
        redis>=4.6.0 \
        safety \
        bandit \
        tzdata \
        graypy


FROM python:3.11-slim as slim

ENV SOCK_PATH=/var/run/python/uwsgi.sock \
    WSGI_FILE_PATH=/var/www/backend/main/wsgi.py \
    WSGI_PROCESSES=4

VOLUME [ "/var/run/python" ]

WORKDIR /var/www/backend

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libmariadb3 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin/uwsgi /usr/local/bin/
COPY --from=build /usr/local/bin/celery /usr/local/bin/
COPY --from=build /usr/local/bin/bandit* /usr/local/bin/
COPY --from=build /usr/local/bin/safety /usr/local/bin/

CMD ["sh", "-c", "uwsgi --master --die-on-term --protocol uwsgi --wsgi-file $WSGI_FILE_PATH --socket $SOCK_PATH --chmod-socket=666 --processes=$WSGI_PROCESSES"]


FROM slim as slim-dev

EXPOSE 5000
EXPOSE 5678

RUN pip3 install --no-cache-dir --no-warn-script-location \
        debugpy

CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:5678", "manage.py", "runserver", "0.0.0.0:5000"]

FROM $VERSION

RUN apt-get update \
    && apt-get -y --no-install-recommends install wget \
    && wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_$(dpkg --print-architecture).deb \
    && apt install -y ./wkhtmltox_0.12.6.1-3.bookworm_$(dpkg --print-architecture).deb \
    && apt-get purge wget -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f ./wkhtmltox_0.12.6.1-3.bookworm_$(dpkg --print-architecture).deb


RUN pip3 install --no-cache-dir --no-warn-script-location \
        pandas==1.5.3 \
        numpy==1.24.2 \
        matplotlib==3.7.1 \
        pypdf==3.7.0 \
        sqlalchemy==2.0.6 \
        jinja2 \
        libsass \
        django-compressor \
        django-sass-processor \
        pdfkit \
        beautifulsoup4 \
        seaborn \
        django-bootstrap5
