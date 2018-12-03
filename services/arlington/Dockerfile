FROM python:3.6.7-slim-jessie

RUN apt-get update && apt-get install -y \
    sqlite \
    texlive-latex-base

RUN mkdir app
COPY requirements.txt app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements.txt
WORKDIR /app
COPY . ./
