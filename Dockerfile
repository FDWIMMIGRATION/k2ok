FROM python:3.10.3-slim-buster
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

