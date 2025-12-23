"""
Сервис сокращения URL на FastAPI
Создает короткие ссылки и перенаправляет по ним
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import database
import validators  # Для валидации URL

app = FastAPI(
    title="URL Shortener Service",
    description="Сервис для создания коротких ссылок",
    version="1.0.0"
)

# Модель для создания короткой ссылки
class URLCreate(BaseModel):
    url: str

# Модель для ответа
class URLResponse(BaseModel):
    short_id: str
    short_url: str
    original_url: str
    created_at: str

@app.on_event("startup")
def startup_event():
    """Инициализируем БД при запуске"""
    print("🚀 Запускаем URL Shortener сервис...")
    database.init_db()

@app.get("/")
def read_root():
    """Корневой эндпоинт"""
    return {
        "service": "URL Shortener Service",
        "status": "running",
        "docs": "/docs",
        "endpoints": [
            "POST /shorten",
            "GET /{short_id} - редирект",
            "GET /stats/{short_id} - статистика"
        ]
    }

@app.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
def create_short_url(url_data: URLCreate):
    """Создание короткой ссылки"""
    original_url = url_data.url

    # Валидация URL
    if not validators.url(original_url):
        raise HTTPException(
            status_code=400,
            detail="Некорректный URL. Пример: https://example.com"
        )

    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        # Проверяем, нет ли уже такой ссылки
        cursor.execute("SELECT * FROM urls WHERE original_url = ?", (original_url,))
        existing = cursor.fetchone()

        if existing:
            # Если ссылка уже есть, возвращаем существующую
            short_id = existing["short_id"]
        else:
            # Генерируем новый short_id
            short_id = database.generate_short_id()

            # Проверяем уникальность (маловероятно, но на всякий случай)
            cursor.execute("SELECT COUNT(*) FROM urls WHERE short_id = ?", (short_id,))
            while cursor.fetchone()[0] > 0:
                short_id = database.generate_short_id()
                cursor.execute("SELECT COUNT(*) FROM urls WHERE short_id = ?", (short_id,))

            # Сохраняем в БД
            cursor.execute(
                "INSERT INTO urls (short_id, original_url) VALUES (?, ?)",
                (short_id, original_url)
            )

        conn.commit()

        # Формируем ответ
        return {
            "short_id": short_id,
            "short_url": f"http://localhost:8001/{short_id}",  # В реальности тут должен быть домен сервиса
            "original_url": original_url,
            "created_at": cursor.execute(
                "SELECT created_at FROM urls WHERE short_id = ?", (short_id,)
            ).fetchone()["created_at"]
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    """Перенаправление по короткой ссылке"""
    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        # Находим оригинальный URL
        cursor.execute("SELECT original_url FROM urls WHERE short_id = ?", (short_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Короткая ссылка не найдена")

        # Увеличиваем счетчик кликов
        cursor.execute(
            "UPDATE urls SET click_count = click_count + 1 WHERE short_id = ?",
            (short_id,)
        )
        conn.commit()

        # Перенаправляем
        return RedirectResponse(url=result["original_url"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

@app.get("/stats/{short_id}")
def get_url_stats(short_id: str):
    """Получение статистики по короткой ссылке"""
    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT short_id, original_url, created_at, click_count FROM urls WHERE short_id = ?",
            (short_id,)
        )
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Короткая ссылка не найдена")

        return dict(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)