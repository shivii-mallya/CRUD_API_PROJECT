# Task API (Python + FastAPI + SQLite)

A lightweight RESTful CRUD API built with Python and FastAPI that manages tasks stored in a SQLite database (`tasks.db`).

---

## 💡 What's New in Week 2 (Database Integration)
In Week 1, tasks were stored in an in-memory list and disappeared whenever the server restarted. In Week 2, the in-memory array was replaced with a persistent **SQLite database**. 

The client-facing REST API interface remains completely unchanged, demonstrating that data persistence is an internal implementation detail separated from the API contract.

---

## 🚀 Features

- **Full CRUD Operations:** Create, Read, Update, and Delete tasks via SQL queries.
- **Persistent Storage:** Tasks are saved in `tasks.db` and survive server restarts.
- **Auto-Initialization:** Database and `tasks` table are created automatically on startup.
- **Default Seed Data:** Populates 3 initial example tasks on first run if the table is empty.
- **Input Validation & Error Handling:** 
  - Unknown IDs return `404 {"error": "Task not found"}`.
  - Invalid payloads return `400 Bad Request`.
- **Interactive API Docs:** Built-in Swagger UI available at `/docs`.

---

## 🗄️ Database Details

- **Database Engine:** SQLite (Serverless, zero-configuration)
- **Database File Location:** `./tasks.db` (root of the project)
- **Table Schema (`tasks`):**
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `title` (TEXT NOT NULL)
  - `done` (INTEGER DEFAULT 0)

### Why SQLite?
1. **Zero Configuration:** Runs embedded in Python without needing a separate database service (like PostgreSQL or MySQL) installed.
2. **File-Based Persistence:** Stores data locally in `tasks.db`, making data durable across application restarts.
3. **Lightweight & Portable:** Ideal for local development, testing, and small-scale applications.

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/shivii-mallya/CRUD_API_PROJECT.git](https://github.com/shivii-mallya/CRUD_API_PROJECT.git)
   cd CRUD-API-Project