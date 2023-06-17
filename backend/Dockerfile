FROM python:3.9-slim

LABEL author='Saborrr' version=1.0 broken_keyboards=14

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
