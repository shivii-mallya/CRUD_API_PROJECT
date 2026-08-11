from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="Task API", version="1.0")


# --- Input Schemas ---
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the task")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# --- In-Memory Database ---
tasks_db = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Finish W2 A1 assignment", "done": True},
    {"id": 3, "title": "Read FastAPI docs", "done": False},
]
next_id = 4


# --- Stage 1 & 2 Endpoints ---
@app.get("/")
def get_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

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


# --- Stage 4 Endpoints ---
@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    # Search for task by ID
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    # Reject empty payload
    if payload.title is None and payload.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must supply 'title' or 'done' status to update"
        )

    # Validate and update title if provided
    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty"
            )
        task["title"] = payload.title.strip()

    # Update completion status if provided
    if payload.done is not None:
        task["done"] = payload.done

    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    global tasks_db
    task_idx = next((i for i, t in enumerate(tasks_db) if t["id"] == task_id), None)
    if task_idx is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    tasks_db.pop(task_idx)
    return None