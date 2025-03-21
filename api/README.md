# Tornado API с авторизацией Keycloak

Этот проект предоставляет API на Tornado для генерации произвольных отчетов.  Доступ к endpoint `/reports` ограничен пользователями с ролью `prothetic_user` и требует аутентификации через Keycloak.

## Требования

*   Docker
*   Docker Compose (опционально, для локальной разработки с Keycloak)
*   Аккаунт Keycloak с настроенным realm, клиентом и пользователями с ролью `prothetic_user`.

## Настройка Keycloak (пример)

1.  **Создайте realm:** Назовите его, например, `your_realm`.
2.  **Создайте клиента:**
    *   Client ID: `your_client_id`
    *   Client Protocol: `openid-connect`
    *   Access Type: `confidential` (или `public` в зависимости от вашей архитектуры)
    *   Standard Flow Enabled: `ON`
    *   Valid Redirect URIs: `*` (или более строгие значения для production)
    *   Web Origins: `*` (или более строгие значения для production)
3.  **Создайте роль:**
    *   Role Name: `prothetic_user`
4.  **Создайте пользователя:**
    *   Добавьте пользователя в realm.
    *   Назначьте пользователю роль `prothetic_user` (client role, назначьте роль клиенту `your_client_id`).

## Развертывание

**Локально с Docker Compose (включая Keycloak):**

1.  Убедитесь, что у вас установлен Docker и Docker Compose.
2.  Клонируйте репозиторий: `git clone <your_repository_url>`
3.  Перейдите в каталог проекта: `cd <your_project_directory>`
4.  Запустите Keycloak и приложение: `docker-compose up --build`
5.  Перейдите по адресу `http://localhost:8080` чтобы настроить Keycloak.
6.  Перейдите по адресу `http://localhost:8888` чтобы использовать Tornado API.
7.  В запросах к `/reports` добавьте заголовок `Authorization: Bearer <your_access_token>`, где `<your_access_token>` - это токен, полученный из Keycloak после аутентификации пользователя с ролью `prothetic_user`.

**Без Docker Compose (только приложение):**

1.  Убедитесь, что у вас установлен Python 3.9 и pip.
2.  Клонируйте репозиторий: `git clone <your_repository_url>`
3.  Перейдите в каталог проекта: `cd <your_project_directory>`
4.  Создайте виртуальное окружение: `python3 -m venv venv`
5.  Активируйте виртуальное окружение: `source venv/bin/activate` (Linux/macOS) или `venv\Scripts\activate` (Windows)
6.  Установите зависимости: `pip install -r requirements.txt`
7.  Установите переменные окружения:
    *   `KEYCLOAK_REALM`:  Имя realm Keycloak.
    *   `KEYCLOAK_CLIENT_ID`: Client ID вашего клиента Keycloak.
    *   `KEYCLOAK_PUBLIC_KEY_URL`:  URL для получения публичного ключа Keycloak. Пример: `http://localhost:8080/realms/your_realm/protocol/openid-connect/certs`
8.  Запустите приложение: `python app.py`
9.  В запросах к `/reports` добавьте заголовок `Authorization: Bearer <your_access_token>`, где `<your_access_token>` - это токен, полученный из Keycloak после аутентификации пользователя с ролью `prothetic_user`.  Keycloak должен быть доступен по URL, указанному в `KEYCLOAK_PUBLIC_KEY_URL`.

## Использование

Для доступа к endpoint `/reports` необходимо выполнить следующие шаги:

1.  **Получите access token из Keycloak:**  Выполните аутентификацию пользователя с ролью `prothetic_user` в Keycloak.  Keycloak предоставит вам access token.
2.  **Добавьте заголовок Authorization:** В запросе к `/reports` добавьте заголовок `Authorization: Bearer <your_access_token>`, заменив `<your_access_token>` на полученный токен.

**Пример запроса (curl):**
bash
curl -H "Authorization: Bearer <your_access_token>" http://localhost:8888/reports