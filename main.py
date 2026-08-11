from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Task API", version="1.0")


# --- Pydantic Schema for Input Validation ---
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the task")


# --- In-Memory Database ---
tasks_db = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Finish W2 A1 assignment", "done": True},
    {"id": 3, "title": "Read FastAPI docs", "done": False},
]
next_id = 4


# --- Stage 1 Endpoints ---
@app.get("/")
def get_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}


# --- Stage 2 Endpoints ---
@app.get("/tasks")
def get_tasks():
    return tasks_db

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


# --- Stage 3 Endpoint ---
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    global next_id
    
    # Reject empty or whitespace-only titles ("   ")
    if not payload.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty or whitespace"
        )

    new_task = {
        "id": next_id,
        "title": payload.title.strip(),
        "done": False
    }
    tasks_db.append(new_task)
    next_id += 1
    return new_task