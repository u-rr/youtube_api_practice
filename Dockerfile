FROM python:3
# FROM gcr.io/google_appengine/python
WORKDIR /code/
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /code/

