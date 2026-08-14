import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
DB_FILE = "tasks.db"


def get_db_connection():
    """Helper function to open a database connection."""
    conn = sqlite3.connect(DB_FILE)
    # Allows accessing columns by name: row["title"] instead of row[1]
    conn.row_factory = sqlite3.Row
    return conn


# --- STAGE 1: READ ENDPOINTS ---


@app.get("/tasks")
def get_all_tasks():
    """Retrieve all tasks from the SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL: Select all rows from the tasks table
    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    # Convert database rows into a list of dictionaries
    tasks = []
    for row in rows:
        tasks.append(
            {
                "id": row["id"],
                "title": row["title"],
                "done": bool(row["done"]),  # SQLite stores booleans as 0 or 1
            }
        )

    return tasks


@app.get("/tasks/{task_id}")
def get_single_task(task_id: int):
    """Retrieve a single task by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL: Select task where id matches (using ? parameter binding for security)
    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    )
    row = cursor.fetchone()
    conn.close()

    # Handle 404 if no matching record is found
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }