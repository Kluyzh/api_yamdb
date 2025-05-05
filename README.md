# api_YaMDb

## Описание
Описание группового проекта для Яндекс Практикума — API для социальной сети **YaMDb**. 
Проект YaMDb собирает отзывы пользователей на различные произведения. 
Пользователи могут оставлять отзывы, ставить оценки и комментировать отзывы других пользователей.

---

## Установка

1. Клонируйте репозиторий:

```bash
git clonegit@github.com:Kluyzh/api_yamdb.git
cd api_yamdb
git branch feature  # Создали новую ветку с именем feature.
git branch  # Проверили, в какой ветке находимся.
feature  # Появилась новая ветка.
git fetch —all  # Проверить наличие всех веток
git branch -a
git checkout -b develop  # Создали ветку develop и сразу переключились на неё.
git checkout develop  # Переключились в develop.
git merge feature/email-validation  # переместить все коммиты из feature/email-validation в ветку develop — смержить ветки
   

```
Создайте и активируйте виртуальное окружение:

```python -m venv venv
source venv/Scripts/activate
```
Установите зависимости:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```[README.md](README.md)
Выполните миграции:
```
python manage.py makemigrations
python manage.py migrate
```
Установите дополнительные библиотеки (если не указаны в requirements.txt):
```
pip install django-filter
```
Запустите сервер разработки:
```
python manage.py runserver
```

---

## Пример запроса на регистрацию пользователя


POST /api/v1/auth/signup/
Заголовок: Authorization: Bearer <токен>

Тело запроса:
```
{
   "email": "user1@example.com",
  "username": "^w\\Z"
}

Ответ:

{
  "email": "rejoice1",
  "username": "rejoice1"
}
```



Python 3.9+

Группа Разработчиков:
Автор 1: Илья Клюжев (Тимлид)
Автор 2: Олеся Виноградова
Автор 3: Нияз Хабиулин
