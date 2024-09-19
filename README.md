# javacode-python
В тестовом описано приложение, которое работает с кошельком; в моем представлении это предполагает наличие аутентификации
* у меня был свой готовый пет проект с jwt аутентификацией, поэтому этот сделан на основе него
* никаких дополнительных манипуляций делать не нужно, я объединил два проекта в один и убрал конфликты

## Собираем
* ```git clone git@github.com:zakirovio/javacode-python.git```
* ```cd javacode-python```
* Win32: ```python -m venv .venv``` или Unix: ```python3 -m venv .venv```
* Аналогично: ```.venv\Scripts\activate``` или ```source ./.venv/bin/activate```
* ```pip install -r requirements.txt```
* ```cd src```
* ```далее нужно создать .env файл, скопировав переменные окружения из .env.template```
* . . .