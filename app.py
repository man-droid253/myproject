import os
import sqlite3
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'banana'  # Replace with a secure secret key

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'projects.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS projects (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               description TEXT NOT NULL,
               category TEXT NOT NULL DEFAULT 'Learning',
               status TEXT NOT NULL DEFAULT 'not started',
               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )


def reset_db():
    with get_db_connection() as conn:
        conn.execute('DROP TABLE IF EXISTS projects')
        conn.execute(
            '''
            CREATE TABLE projects (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               description TEXT NOT NULL,
               category TEXT NOT NULL DEFAULT 'Learning',
               status TEXT NOT NULL DEFAULT 'not started',
               timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )


init_db()


def format_timestamp(ts_str):
    if not ts_str:
        return ''
    try:
        # SQLite CURRENT_TIMESTAMP gives 'YYYY-MM-DD HH:MM:SS'
        dt = datetime.strptime(ts_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
        return dt.strftime('%b %d, %Y %I:%M %p')
    except Exception:
        return ts_str


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/projects')
def projects():
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY timestamp DESC").fetchall()
    projects_list = []
    for r in rows:
        d = dict(r)
        d['formatted_ts'] = format_timestamp(d.get('timestamp'))
        projects_list.append(d)

    return render_template('projects.html', projects_list=projects_list)


@app.route('/reset_db', methods=['POST'])
def reset_db_route():
    reset_db()
    flash('Database reset successfully.', 'success')
    return redirect('/projects')


@app.route('/add_project', methods=['POST'])
def add_project():
    project_name = (request.form.get('project-add') or '').strip()
    project_description = (request.form.get('project-description') or '').strip()
    project_category = request.form.get('project-category') or 'Learning'
    project_status = request.form.get('status') or 'not started'

    if not project_name or not project_description:
        flash('Project name and description are required.', 'error')
        return redirect('/projects')

    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO projects (name, description, category, status) VALUES (?, ?, ?, ?)",
            (project_name, project_description, project_category, project_status),
        )

    flash(f'Project "{project_name}" added to "{project_category}" successfully!', 'success')
    return redirect('/projects')


@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))

    flash(f'Project with ID {project_id} deleted successfully!', 'success')
    return redirect('/projects')


@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if request.method == 'POST':
        project_name = (request.form.get('project-add') or '').strip()
        project_description = (request.form.get('project-description') or '').strip()
        project_category = request.form.get('project-category') or 'Learning'
        project_status = request.form.get('status') or 'not started'

        if not project_name or not project_description:
            flash('Project name and description are required.', 'error')
            return redirect('/projects')

        with get_db_connection() as conn:
            conn.execute(
               "UPDATE projects SET name = ?, description = ?, category = ?, status = ? WHERE id = ?",
               (project_name, project_description, project_category, project_status, project_id),
            )

        flash(f'Project "{project_name}" updated successfully!', 'success')
        return redirect('/projects')

    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()

    if row is None:
        return redirect('/projects')

    project = dict(row)
    project['formatted_ts'] = format_timestamp(project.get('timestamp'))

    return render_template('edit_project.html', project=project)


if __name__ == '__main__':
    app.run(debug=True)
