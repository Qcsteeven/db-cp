#!/bin/sh
set -e

echo "Ожидание запуска базы данных"
sleep 3

echo "Создание файлов миграций"
python manage.py makemigrations --noinput

echo "Применение миграций"
python manage.py migrate --noinput

echo "Настройка администратора"
python manage.py setup_admin

echo "Заполнение базы моковыми данными"
python manage.py init_data

echo "Запуск сервера"
exec python manage.py runserver 0.0.0.0:8000
