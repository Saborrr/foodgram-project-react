FROM python:3.9.10-slim

LABEL author='Saborrr' version=1.0 broken_keyboards=2

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY ./ /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
