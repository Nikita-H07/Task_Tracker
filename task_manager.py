import sqlite3
import os
import tkinter as tk
from tkinter import messagebox, ttk

DB_NAME = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            priority TEXT NOT NULL,
            deadline TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

def load_tasks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_task_db(name, priority, deadline):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (name, priority, deadline) VALUES (?, ?, ?)",
                   (name, priority, deadline))
    conn.commit()
    conn.close()

def mark_complete_db(task_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def delete_task_db(task_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def filter_tasks_db(filter_val):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if filter_val == "all":
        cursor.execute("SELECT * FROM tasks")
    elif filter_val in ["pending", "completed"]:
        cursor.execute("SELECT * FROM tasks WHERE status = ?", (filter_val,))
    else:
        cursor.execute("SELECT * FROM tasks WHERE priority = ?", (filter_val,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def refresh_table(filter_val="all"):
    for row in table.get_children():
        table.delete(row)
    rows = filter_tasks_db(filter_val)
    for row in rows:
        table.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))

def add_task():
    name = name_entry.get()
    priority = priority_var.get()
    deadline = deadline_entry.get()
    if not name or not deadline:
        messagebox.showwarning("Missing Info", "Please fill all fields!")
        return
    add_task_db(name, priority, deadline)
    refresh_table()
    name_entry.delete(0, tk.END)
    deadline_entry.delete(0, tk.END)
    messagebox.showinfo("Success", "Task added!")

def mark_complete():
    selected = table.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a task first!")
        return
    task_id = table.item(selected[0])["values"][0]
    mark_complete_db(task_id)
    refresh_table()
    messagebox.showinfo("Success", "Task marked complete!")

def delete_task():
    selected = table.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a task first!")
        return
    task_id = table.item(selected[0])["values"][0]
    delete_task_db(task_id)
    refresh_table()
    messagebox.showinfo("Deleted", "Task deleted!")

def filter_tasks():
    filter_val = filter_var.get()
    refresh_table(filter_val)

# Initialize DB
init_db()

# Main Window
root = tk.Tk()
root.title("Task Tracker")
root.geometry("900x600")
root.configure(bg="#1e1e2e")

# Title
tk.Label(root, text="Task Tracker", font=("Arial", 20, "bold"),
         bg="#1e1e2e", fg="#cdd6f4").pack(pady=10)

# Input Frame
input_frame = tk.Frame(root, bg="#1e1e2e")
input_frame.pack(pady=10)

tk.Label(input_frame, text="Task Name:", bg="#1e1e2e", fg="white").grid(row=0, column=0, padx=5)
name_entry = tk.Entry(input_frame, width=25)
name_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Priority:", bg="#1e1e2e", fg="white").grid(row=0, column=2, padx=5)
priority_var = tk.StringVar(value="medium")
priority_menu = ttk.Combobox(input_frame, textvariable=priority_var,
                              values=["high", "medium", "low"], width=10)
priority_menu.grid(row=0, column=3, padx=5)

tk.Label(input_frame, text="Deadline:", bg="#1e1e2e", fg="white").grid(row=0, column=4, padx=5)
deadline_entry = tk.Entry(input_frame, width=15)
deadline_entry.grid(row=0, column=5, padx=5)
tk.Label(input_frame, text="(DD-MM-YYYY)", bg="#1e1e2e",
         fg="gray", font=("Arial", 8)).grid(row=1, column=5)

# Add Button
tk.Button(root, text="+ Add Task", command=add_task,
          bg="#89b4fa", fg="#1e1e2e", font=("Arial", 11, "bold"),
          padx=10, pady=5).pack(pady=5)

# Filter Frame
filter_frame = tk.Frame(root, bg="#1e1e2e")
filter_frame.pack(pady=5)
tk.Label(filter_frame, text="Filter:", bg="#1e1e2e", fg="white").pack(side=tk.LEFT, padx=5)
filter_var = tk.StringVar(value="all")
ttk.Combobox(filter_frame, textvariable=filter_var,
             values=["all", "pending", "completed", "high", "medium", "low"],
             width=15).pack(side=tk.LEFT, padx=5)
tk.Button(filter_frame, text="Apply Filter", command=filter_tasks,
          bg="#a6e3a1", fg="#1e1e2e", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

# Table
table_frame = tk.Frame(root)
table_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

table = ttk.Treeview(table_frame,
                     columns=("ID", "Name", "Priority", "Deadline", "Status"),
                     show="headings", height=15)
for col, width in [("ID", 50), ("Name", 220), ("Priority", 100), ("Deadline", 150), ("Status", 100)]:
    table.heading(col, text=col)
    table.column(col, width=width)
table.pack(fill=tk.BOTH, expand=True)

# Action Buttons
btn_frame = tk.Frame(root, bg="#1e1e2e")
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="✅ Mark Complete", command=mark_complete,
          bg="#a6e3a1", fg="#1e1e2e", font=("Arial", 10, "bold"),
          padx=10).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="🗑 Delete Task", command=delete_task,
          bg="#f38ba8", fg="#1e1e2e", font=("Arial", 10, "bold"),
          padx=10).pack(side=tk.LEFT, padx=10)

refresh_table()
root.mainloop()
