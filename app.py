
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path
from datetime import date

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("tasks.db")


def connect_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def setup_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                category TEXT DEFAULT 'Study',
                due_date TEXT DEFAULT '',
                status TEXT DEFAULT 'To Do'
            )
        """)


@app.route("/")
def home():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "All")
    priority_filter = request.args.get("priority", "All")
    sort = request.args.get("sort", "newest")

    query = "SELECT * FROM tasks WHERE name LIKE ?"
    values = [f"%{search}%"]

    if status_filter in ["To Do", "In Progress", "Completed"]:
        query += " AND status = ?"
        values.append(status_filter)

    if priority_filter in ["High", "Medium", "Low"]:
        query += " AND priority = ?"
        values.append(priority_filter)

    ordering = {
        "newest": "id DESC",
        "oldest": "id ASC",
        "deadline": "due_date ASC",
        "priority": "CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END"
    }
    query += " ORDER BY " + ordering.get(sort, "id DESC")

    with connect_db() as db:
        tasks = db.execute(query, values).fetchall()
        all_tasks = db.execute("SELECT * FROM tasks").fetchall()

    total = len(all_tasks)
    completed = sum(t["status"] == "Completed" for t in all_tasks)
    pending = sum(t["status"] == "To Do" for t in all_tasks)
    in_progress = sum(t["status"] == "In Progress" for t in all_tasks)
    today = date.today().isoformat()
    overdue = sum(
        bool(t["due_date"]) and t["due_date"] < today
        and t["status"] != "Completed" for t in all_tasks
    )
    progress = round(completed * 100 / total) if total else 0

    return render_template(
        "index.html", tasks=tasks, total=total,
        completed=completed, pending=pending,
        in_progress=in_progress, overdue=overdue,
        progress=progress, today=today,
        search=search, status_filter=status_filter,
        priority_filter=priority_filter, sort_by=sort
    )


@app.route("/add", methods=["POST"])
def add_task():
    name = request.form.get("task", "").strip()
    priority = request.form.get("priority", "Medium")
    category = request.form.get("category", "Study")
    due_date = request.form.get("due_date", "")

    if priority not in ["High", "Medium", "Low"]:
        priority = "Medium"
    if category not in ["Study", "Personal", "Work", "Other"]:
        category = "Study"

    if name:
        with connect_db() as db:
            db.execute("""
                INSERT INTO tasks (name, priority, category, due_date)
                VALUES (?, ?, ?, ?)
            """, (name, priority, category, due_date))

    return redirect(url_for("home"))


@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    name = request.form.get("task", "").strip()
    priority = request.form.get("priority", "Medium")
    category = request.form.get("category", "Study")
    due_date = request.form.get("due_date", "")

    if name:
        with connect_db() as db:
            db.execute("""
                UPDATE tasks SET name=?, priority=?, category=?, due_date=?
                WHERE id=?
            """, (name, priority, category, due_date, task_id))

    return redirect(url_for("home"))


@app.route("/status/<int:task_id>", methods=["POST"])
def change_status(task_id):
    status = request.form.get("status", "To Do")
    if status not in ["To Do", "In Progress", "Completed"]:
        status = "To Do"

    with connect_db() as db:
        db.execute("UPDATE tasks SET status=? WHERE id=?",
                   (status, task_id))
    return redirect(url_for("home"))


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    with connect_db() as db:
        task = db.execute(
            "SELECT status FROM tasks WHERE id=?", (task_id,)
        ).fetchone()
        if task:
            new_status = "To Do" if task["status"] == "Completed" else "Completed"
            db.execute("UPDATE tasks SET status=? WHERE id=?",
                       (new_status, task_id))
    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    with connect_db() as db:
        db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    return redirect(url_for("home"))


setup_db()

if __name__ == "__main__":
    app.run(debug=True)
