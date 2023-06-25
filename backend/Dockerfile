FROM python:3.9-slim

LABEL author='Saborrr' version=1.0 broken_keyboards=25

WORKDIR /app

COPY requirements.txt /app

COPY requirements.txt ./

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./ ./

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000" ]
