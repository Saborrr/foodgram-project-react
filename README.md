# Проект "Продуктовый помощник (Foodgram)"

## Описание проекта
Проект «Продуктовый помощник»: это приложение, в котором пользователи публикуют рецепты, могут подписываться на публикации других авторов и добавлять рецепты в избранное. Сервис «Список покупок» позволит пользователю создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Проект развернут по адресу: [84.201.164.176](http://84.201.164.176)

Логин: admin
email: admin@admin.ru
Пароль: admin

Документация к API [тут](http://84.201.164.176/api/docs/)

## Использованные технологии:

- Django 3.2.9
- Python 3.9.10
- Django Rest Framework 3.12.4
- PostgreSQL
- Nginx
- Gunicorn
- Authtoken
- Docker
- Docker-compose
- GitHub Actions
- Cервер Linux Ubuntu 20.04

## Запуск проекта

Установить docker, docker-compose на сервер ВМ Yandex.Cloud:
```
ssh <login>@<ip>
```
```
sudo apt update && sudo apt upgrade -y && sudo apt install curl -y
```
```
sudo curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo rm get-docker.sh
```
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```
sudo chmod +x /usr/local/bin/docker-compose
```

Создайте папку infra:

```
mkdir infra
```
- Перенести файлы docker-compose.yml и default.conf на сервер.

```
scp docker-compose.yml username@server_ip:/home/<username>/
```
```
scp default.conf <username>@<server_ip>:/home/<username>/
```
- Создайте файл .env в дериктории infra:

```
touch .env
```
- Заполните в настройках своего репозитория secrets:

```python
DB_ENGINE=<ваша база данных>
DB_NAME=<имя базы данных>
POSTGRES_USER=<имя пользователя>
POSTGRES_PASSWORD=<пароль>
DB_HOST=<хост>
DB_PORT=<порт>
```

Для доступа к контейнеру выполните следующие команды:

```
sudo docker compose exec backend python manage.py makemigrations
```
```
sudo docker compose exec backend python manage.py migrate --noinput
```
```
sudo docker compose exec backend python manage.py createsuperuser
```
```
sudo docker compose exec backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить базу данных ингредиентами и тэгами:

```
sudo docker-compose exec backend python manage.py load_tags
```
```
sudo docker-compose exec backend python manage.py load_ingredients
```

![Пример workflow](https://github.com/saborrr/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?event=push)
