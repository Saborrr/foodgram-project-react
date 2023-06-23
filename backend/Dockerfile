FROM python:3.9-slim

LABEL author='Saborrr' version=1.0 broken_keyboards=24

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install --upgrade pip --no-cache-dir

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
