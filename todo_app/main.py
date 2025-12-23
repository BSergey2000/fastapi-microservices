"""
ToDo сервис на FastAPI
Реализация CRUD операций для списка задач
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
import database
from datetime import datetime

# Инициализируем FastAPI приложение
app = FastAPI(
    title="ToDo Service",
    description="Сервис для управления задачами",
    version="1.0.0"
)

# Модель для создания задачи
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

# Модель для обновления задачи
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# Модель для ответа (включает id и created_at)
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: str

@app.on_event("startup")
def startup_event():
    """Инициализируем БД при запуске приложения"""
    print("🚀 Запускаем ToDo сервис...")
    database.init_db()

@app.get("/")
def read_root():
    """Корневой эндпоинт"""
    return {
        "service": "ToDo Service",
        "status": "running",
        "docs": "/docs",
        "endpoints": [
            "POST /items",
            "GET /items",
            "GET /items/{id}",
            "PUT /items/{id}",
            "DELETE /items/{id}"
        ]
    }

@app.post("/items", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    """Создание новой задачи"""
    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)",
            (task.title, task.description, task.completed)
        )
        conn.commit()

        # Получаем созданную задачу
        task_id = cursor.lastrowid
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task_data = cursor.fetchone()

        if not task_data:
            raise HTTPException(status_code=500, detail="Ошибка при создании задачи")

        return dict(task_data)
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

@app.get("/items", response_model=List[TaskResponse])
def get_all_tasks():
    """Получение всех задач"""
    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        return [dict(task) for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

@app.get("/items/{item_id}", response_model=TaskResponse)
def get_task_by_id(item_id: int):
    """Получение задачи по ID"""
    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (item_id,))
        task = cursor.fetchone()

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Задача с ID {item_id} не найдена"
            )

        return dict(task)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

@app.put("/items/{item_id}", response_model=TaskResponse)
def update_task(item_id: int, task_update: TaskUpdate):
    """Обновление задачи по ID"""
    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        # Проверяем существование задачи
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (item_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Задача с ID {item_id} не найдена")

        # Собираем поля для обновления
        update_fields = []
        values = []

        if task_update.title is not None:
            update_fields.append("title = ?")
            values.append(task_update.title)

        if task_update.description is not None:
            update_fields.append("description = ?")
            values.append(task_update.description)

        if task_update.completed is not None:
            update_fields.append("completed = ?")
            values.append(task_update.completed)

        if not update_fields:
            raise HTTPException(status_code=400, detail="Нет данных для обновления")

        # Выполняем обновление
        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
        values.append(item_id)
        cursor.execute(query, values)
        conn.commit()

        # Получаем обновленную задачу
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (item_id,))
        updated_task = cursor.fetchone()

        return dict(updated_task)
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(item_id: int):
    """Удаление задачи по ID"""
    conn = database.get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM tasks WHERE id = ?", (item_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Задача с ID {item_id} не найдена")

        return None
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)