import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


DB_FILE = "tasks.db"


def get_db_connection():
    """Helper function to open a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Stage 0 logic:
    1. Creates tasks table if missing.
    2. Inserts 3 initial example tasks ONLY if table is empty.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """
    )

    # Check if table is empty
    cursor.execute("SELECT COUNT(*) as count FROM tasks")
    row = cursor.fetchone()
    if row["count"] == 0:
        initial_tasks = [
            ("Buy groceries", 0),
            ("Finish FastAPI assignment", 0),
            ("Learn SQL basics", 1),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", initial_tasks
        )

    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


# --- ASSIGNMENT-COMPLIANT ERROR HANDLERS ---
# Map 404 & Validation Errors to match assignment expectations
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Assignment specifies status 400 for bad/missing inputs
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid request payload"},
    )


# --- PYDANTIC SCHEMAS ---


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1)
    done: bool | None = None


# --- STAGE 1: READ ENDPOINTS ---


@app.get("/tasks")
def get_all_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    return [
        {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        for row in rows
    ]


@app.get("/tasks/{task_id}")
def get_single_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404)

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


# --- STAGE 2: CREATE ENDPOINT ---


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, 0))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "title": task.title, "done": False}


# --- STAGE 3: UPDATE & DELETE ENDPOINTS ---


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    """Stage 3: Update a task in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Verify task existence
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    existing_task = cursor.fetchone()

    if existing_task is None:
        conn.close()
        raise HTTPException(status_code=404)

    # 2. Retain existing values if not provided in payload
    new_title = task.title if task.title is not None else existing_task["title"]
    new_done = int(task.done) if task.done is not None else existing_task["done"]

    # 3. Execute SQL UPDATE
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id),
    )
    conn.commit()
    conn.close()

    return {"id": task_id, "title": new_title, "done": bool(new_done)}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """Stage 3: Delete a task from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Execute SQL DELETE
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

    # 2. Check if a row was actually deleted
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404)

    conn.close()
    return {"message": "Task deleted successfully"}