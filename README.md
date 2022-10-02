# Yatube project

___
### Описание
Текстовая социальная сеть для ведения блога.
___
### Технологии

- [Python 3.7]
- [Django 2.2.19]
___
### Запуск проекта в dev-режиме
Клонировать репозиторий и перейти в директорию с ним:
```
git clone https://github.com/Annsjaw/yatube_project.git
```
```
cd yatube_project
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
Сервер будет доступен по адресу:
```
http://127.0.0.1:8000/
```
___
### Автор

- [Дмитрий Ротанин], студент Яндекс Практикума

[//]: # (Ниже находятся справочные ссылки)

   [Python 3.7]: <https://www.python.org/downloads/release/python-370/>
   [Django 2.2.19]: <https://www.djangoproject.com/download/>
   [Дмитрий Ротанин]: <https://github.com/Annsjaw>