FROM python:3.9-slim

LABEL author='Saborrr' version=1.0 broken_keyboards=23

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install --upgrade pip

RUN pip3 install -r /app/requirements.txt

COPY ./ /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
