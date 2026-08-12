from contextlib import asynccontextmanager
from fastapi import FastAPI
import sqlite3

DB_FILE = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print("Current working directory")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_tasks = [
            ("Buy groceries", False),
            ("Complete Week 2 Assignment", False),
            ("Learn SQLite with Python", True)
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", 
            sample_tasks
        )

    conn.commit()
    conn.close()

# Define startup & shutdown lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # RUNS ON STARTUP
    init_db()
    yield
    # RUNS ON SHUTDOWN (if needed)

# Pass lifespan to FastAPI app
app = FastAPI(lifespan=lifespan)