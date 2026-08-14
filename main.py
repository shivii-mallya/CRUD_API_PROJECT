import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


DB_FILE = "tasks.db"


def get_db_connection():
    """Helper function to open a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# --- TABLE INITIALIZATION ---
def init_db():
    """Creates the tasks table if it does not already exist."""
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
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs when the app starts up
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


# --- PYDANTIC SCHEMAS (STAGE 2) ---
class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
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
        raise HTTPException(status_code=404, detail="Task not found")

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


# --- STAGE 2: WRITE ENDPOINTS (CREATE, UPDATE, DELETE) ---


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    """Create a new task."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, 0))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "title": task.title, "done": False}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    """Update an existing task's title, done status, or both."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if task exists first
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    existing_task = cursor.fetchone()

    if existing_task is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    # Use existing values if new ones aren't provided in the payload
    new_title = task.title if task.title is not None else existing_task["title"]
    new_done = int(task.done) if task.done is not None else existing_task["done"]

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id),
    )
    conn.commit()
    conn.close()

    return {"id": task_id, "title": new_title, "done": bool(new_done)}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """Delete a task by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    conn.close()
    return {"message": f"Task {task_id} successfully deleted"}