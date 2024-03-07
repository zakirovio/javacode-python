# Пользовательская аутентификация DRF
Текущий релиз приложения включает:
- sqlite3;
- новая модель пользователей;
- основные API вьюхи для регистрации и аутентификации
- аутентификация JWT: SimpleJWT;
- refresh_token`ы хранятся и передаются через  httpOnly куки;
- библиотека SimpleJWT предлагает хранение выданных и заблокированных refresh_token`ов в двух разных таблицах;
- еще не истекшие access_token`ы добавляются в redis-cache после logout;

## Сборка

- ```git clone ```
- ```cd my-auth-drf-jwt-redis```
- ```python3.12 -m venv venv```
- ```source ./venv/bin/activate```
- ```pip install -r requirements.txt```
- ```cd src```
- ```docker compose -f docker-compose-cache.yaml up -d```
- ```cp env.template ./.env```
- ```python manage.py makemigrations```
- ```python manage.py migrate```
- ```python manage.py runserver```

## Тесты
- ```python manage.py test tests```

### Ссылка на следующий релиз
```https://github.com/zakirovio/{repo}/releases/tag/{None}```