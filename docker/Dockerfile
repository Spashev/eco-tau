FROM python:latest

MAINTAINER Spashev Nurken

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONFAULTHANDLER 1
ENV PYTHONBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get install -y --no-install-recommends apt-utils \
  && apt-get install -y --no-install-recommends libc-dev \
  && apt-get install -y --no-install-recommends gcc \
  && apt-get install -y --no-install-recommends gettext \
  && apt-get install -y --no-install-recommends screen \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists\*

WORKDIR /code

COPY app /code
COPY app/product/management/images /code/media/

RUN pip install --upgrade pip &&  pip install -r requirements.txt && pip install \
    Redis \
    uvicorn \
    psycopg2 \
    flake8  \
    pytest-django

EXPOSE 8000
EXPOSE 9000

COPY docker/start.uvicorn.sh ./
RUN chmod +x ./start.uvicorn.sh
