from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="Task API", version="1.0")

# --- In-Memory Database ---
tasks_db = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Finish W2 A1 assignment", "done": True},
    {"id": 3, "title": "Read FastAPI docs", "done": False},
]
next_id = 4

@app.get("/")
def get_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    """Returns the full list of tasks."""
    return tasks_db


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Returns a single task by ID or 404 if not found."""
    for task in tasks_db:
        if task["id"] == task_id:
            return task
            
    # If the loop finishes without finding the task ID:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )