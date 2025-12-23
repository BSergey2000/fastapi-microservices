"""
Скрипт для тестирования сервисов
"""

import requests
import time
import json


def test_todo_service():
    print("🧪 Тестируем ToDo сервис...")

    base_url = "http://localhost:8000"

    # 1. Создаем задачу
    print("1. Создаем задачу...")
    task_data = {
        "title": "Купить продукты",
        "description": "Молоко, хлеб, яйца",
        "completed": False
    }

    response = requests.post(f"{base_url}/items", json=task_data)
    print(f"   Ответ: {response.status_code}")
    task = response.json()
    print(f"   Создана задача: {task['title']} (ID: {task['id']})")

    # 2. Получаем все задачи
    print("\n2. Получаем все задачи...")
    response = requests.get(f"{base_url}/items")
    tasks = response.json()
    print(f"   Найдено задач: {len(tasks)}")

    # 3. Обновляем задачу
    print("\n3. Обновляем задачу...")
    update_data = {"completed": True}
    response = requests.put(f"{base_url}/items/{task['id']}", json=update_data)
    updated_task = response.json()
    print(f"   Задача обновлена: completed={updated_task['completed']}")

    print("✅ ToDo сервис работает корректно!\n")


def test_shorturl_service():
    print("🧪 Тестируем URL Shortener сервис...")

    base_url = "http://localhost:8001"

    # 1. Создаем короткую ссылку
    print("1. Создаем короткую ссылку...")
    url_data = {"url": "https://github.com"}

    response = requests.post(f"{base_url}/shorten", json=url_data)
    print(f"   Ответ: {response.status_code}")
    short_url = response.json()
    print(f"   Создана короткая ссылка: {short_url['short_url']}")

    # 2. Получаем статистику
    print("\n2. Получаем статистику...")
    response = requests.get(f"{base_url}/stats/{short_url['short_id']}")
    stats = response.json()
    print(f"   Статистика: {json.dumps(stats, indent=4, ensure_ascii=False)}")

    print("✅ URL Shortener сервис работает корректно!")


if __name__ == "__main__":
    print("🚀 Запускаем тестирование микросервисов...\n")

    # Ждем немного, чтобы сервисы успели запуститься
    time.sleep(3)

    try:
        test_todo_service()
        test_shorturl_service()
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения. Убедитесь, что сервисы запущены!")
        print("   Запустите: docker-compose up -d")
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")