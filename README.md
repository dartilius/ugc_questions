# Проект опросники

## Технологический стек
- Python3.11
- Django5.2
- PostgreSQL.16

## Запуск в DEV режиме
- `python -m venv venv`
- `source venv/Scripts/activate` - Для Windows или `source venv/bin/activate` Для Linux
- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py createsuperuser` - Для доступа к админке
- `python manage.py runserver` - Запускает сервер на localhost с портом 8000

## Запуск через Docker compose
- `./start.sh` - скрипт запускает контейнеры postgers, nginx и django, проводит миграции и создает администратора (его нужно ввести в консоль)

## Модели данных
- Survey - Основная модель опроса, содержит ссылку на автора, заголовок опроса, дату его создания и последнего обновления
- SurveyQuestions - Модель вопросов относящихся к опросу, содержит в себе текст вопроса, приоритетность его отображения в опросе и ссылку на сам опрос
- QuestionAnswerOption - Модель вариантов ответов на вопросы, содержит в себе текст ответа, приоритетность и ссылку на вопрос
- SurveyCompleting - Основная модель прохождения опроса пользователями, ссылается на пользователя и опрос, так же содержит дату старта и финиша прохождения опроса
- QuestionAnswer - Модель выбранных ответов пользователей на вопросы

## Доступные страницы
- "/" Страница со списком опросов
- "create/" Создание нового опроса
- "start_completing/<str:uid>" Начало прохождения опроса
- "survey/<str:uid>/complete" Завершение опроса
- "survey/<str:uid>/question/<int:q_id>/answer" Добавление ответа на вопрос
- "survey/<str:uid>/edit" Изменение опроса
- "/admin" - Страница администрирования

## Авторизация
- /admin/login
