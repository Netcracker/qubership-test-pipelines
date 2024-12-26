FROM python:3.10.13-alpine3.19

ENV HOME_DIR=/scripts
ENV PYTHONPATH=/usr/local/lib/python3.10/site-packages/external_platform_library_builtIn

RUN echo alpine3.19/main > /etc/apk/repositories; \
    echo alpine3.19/community >> /etc/apk/repositories

RUN mkdir -p ${HOME_DIR}

COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt requirements.txt
COPY external-platform-built-in-library ${HOME_DIR}

RUN apk add --update --no-cache openssl-dev libffi-dev gcc musl-dev python3-dev make py3-pip
RUN set -x \
    && apk add --update --no-cache bash shadow python3 vim rsync ttyd build-base apk-tools py3-yaml

RUN set -x && apk upgrade --no-cache --available


RUN set -x \
    && pip3 install --upgrade pip setuptools==62.3.1 \
    && pip3 install -r requirements.txt \
    && pip3 install --upgrade paramiko \
    && pip3 install external-platform-library-builtIn==0.0.1 \
    && rm -rf /var/cache/apk/*

WORKDIR ${HOME_DIR}

