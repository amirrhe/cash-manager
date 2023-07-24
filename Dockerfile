# Use the official Python image as the base image
FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app


COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
RUN pip3 install django gunicorn

COPY . /app/

CMD python3 manage.py makemigrations --no-input && \
    python3 manage.py migrate --no-input && \
    python3 manage.py collectstatic --no-input && \
    python3 manage.py createsuperuser --user admin --email admin@localhost --no-input; \
    gunicorn -b 0.0.0.0:8000 cashmanager.wsgi

