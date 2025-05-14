from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200

import uuid

#Задние 1: Тестирование регистрации пользователя:
def test_create_user():
    # Генерация уникального username и email для каждого теста
    unique_id = uuid.uuid4().hex
    username = f"testuser_{unique_id}"
    email = f"{username}@example.com"

    # Проверка успешной регистрации нового пользователя
    response = client.post(
        "/register/",
        json={
            "username": username,
            "email": email,
            "full_name": "Test User Unique",
            "password": "password123"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email

    # Проверка повторной регистрации с тем же username или email
    response = client.post(
        "/register/",
        json={
            "username": username,
            "email": email,
            "full_name": "Test User Unique",
            "password": "password123"
        },
    )
    assert response.status_code == 400

# Задание 2: Тестирование аутентификации
def test_login_for_access_token():
    # Регистрация нового пользователя
    client.post(
        "/register/",
        json={"username": "testuser3", "email": "testuser3@example.com", "full_name": "Test User 3", "password": "password123"},
    )

    # Проверка успешной аутентификации пользователя и получения токена
    response = client.post(
        "/token",
        data={"username": "testuser3", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Проверка неправильного username или password
    response = client.post(
        "/token",
        data={"username": "testuser3", "password": "wrongpassword"},
    )
    assert response.status_code == 401

    # Проверка истекшего или неправильного токена
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert response.status_code == 401

# Задание 3: Тестирование получения пользователей
def test_get_current_user():
    # Регистрация нового пользователя
    client.post(
        "/register/",
        json={"username": "testuser5", "email": "testuser5@example.com", "full_name": "Test User 5", "password": "password123"},
    )

    # Получаем токен
    response = client.post(
        "/token",
        data={"username": "testuser5", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    # Проверка получения информации о текущем пользователе с правильным токеном
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser5"

# Задание 4: Тестирование обновления пользователя
def test_update_user():
    # Генерация уникального username и email для каждого теста
    unique_id = uuid.uuid4().hex
    username = f"testuser_{unique_id}"
    email = f"{username}@example.com"

    # Регистрация нового пользователя с уникальными данными
    response = client.post(
        "/register/",
        json={
            "username": username,
            "email": email,
            "full_name": "Test User Unique",
            "password": "password123"
        },
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Получаем токен
    response = client.post(
        "/token",
        data={"username": username, "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    # Проверка обновления данных пользователя
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated Test User Unique"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Test User Unique"

    # Проверка обновления с некорректными данными
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "invalidemail"},
    )
    assert response.status_code == 400  # Изменено на 400, если API возвращает 400 для некорректных данных

    # Проверка обновления без правильного токена
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": "Bearer invalidtoken"},
        json={"full_name": "Updated Test User Unique"},
    )
    assert response.status_code == 401


# Задание 5: Тестирование удаления пользователя
def test_delete_user():
    # Регистрация нового пользователя
    response = client.post(
        "/register/",
        json={"username": "testuser7", "email": "testuser7@example.com", "full_name": "Test User 7", "password": "password123"},
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Получаем токен
    response = client.post(
        "/token",
        data={"username": "testuser7", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    # Проверка успешного удаления пользователя
    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Проверка повторной попытки удалить того же пользователя
    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

# # Задание 6: Тестирование работы CORS
# def test_cors():
#     # Проверка работы CORS с запросами из разрешенного источника
#     response = client.get("/", headers={"Origin": "http://allowed-origin.com"})
#     assert response.status_code == 200
#     assert "access-control-allow-origin" in response.headers
#     assert response.headers["access-control-allow-origin"] == "http://allowed-origin.com"