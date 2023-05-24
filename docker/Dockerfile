FROM python:latest

MAINTAINER Spashev Nurken

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONFAULTHANDLER 1
ENV PYTHONBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Add alpine mirrors
RUN apt-get update \
  && apt-get install -y --no-install-recommends apt-utils \
  && apt-get install -y --no-install-recommends libc-dev \
  && apt-get install -y --no-install-recommends gcc \
  && apt-get install -y --no-install-recommends gettext \
  && apt-get install -y --no-install-recommends screen \
  && apt-get clean

WORKDIR /code

COPY app /code
COPY app/product/management/images /code/media/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install Redis
RUN pip install uvicorn
RUN pip install psycopg2
RUN pip install flake8
RUN pip install pytest-django

EXPOSE 8000

COPY docker/start.uvicorn.sh ./
RUN chmod +x ./start.uvicorn.sh
