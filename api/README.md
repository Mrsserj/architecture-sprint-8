# Tornado API с авторизацией Keycloak

Этот проект предоставляет API на Tornado для генерации произвольных отчетов.  Доступ к endpoint `/reports` ограничен пользователями с ролью `prothetic_user` и требует аутентификации через Keycloak.

## Требования

*   Docker
*   Docker Compose (опционально, для локальной разработки с Keycloak)
*   Аккаунт Keycloak с настроенным realm, клиентом и пользователями с ролью `prothetic_user`.

## Развертывание

**Локально с Docker Compose (включая Keycloak):**

1.  Убедитесь, что у вас установлен Docker и Docker Compose.
2.  Клонируйте репозиторий: `git clone <your_repository_url>`
3.  Перейдите в каталог проекта: `cd <your_project_directory>`
4.  Запустите Keycloak и приложение: `docker-compose up --build`
5.  Перейдите по адресу `http://localhost:8080` чтобы настроить Keycloak.
6.  Перейдите по адресу `http://localhost:8000` чтобы использовать Tornado API.
7.  В запросах к `/reports` добавьте заголовок `Authorization: Bearer <your_access_token>`, где `<your_access_token>` - это токен, полученный из Keycloak после аутентификации пользователя с ролью `prothetic_user`.

## Использование

Для доступа к endpoint `/reports` необходимо выполнить следующие шаги:

1.  **Получите access token из Keycloak:**  Выполните аутентификацию пользователя с ролью `prothetic_user` в Keycloak.  Keycloak предоставит вам access token.
2.  **Добавьте заголовок Authorization:** В запросе к `/reports` добавьте заголовок `Authorization: Bearer <your_access_token>`, заменив `<your_access_token>` на полученный токен.

**Пример запроса (curl):**
bash
curl -H "Authorization: Bearer <your_access_token>" http://localhost:8000/reports