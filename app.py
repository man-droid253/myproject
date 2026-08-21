import os
import sqlite3
from datetime import datetime
import re
from markupsafe import Markup

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

def highlight(text, query):
    if not text or not query:
        return Markup.escape(text or '')
    try:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        # Replace matches with <mark>...</mark>
        highlighted = pattern.sub(lambda m: '<mark>{}</mark>'.format(Markup.escape(m.group(0))), text)
        return Markup(highlighted)
    except Exception:
        return Markup.escape(text)


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
def dashboard():
    # Use the shared DB helper and consistent status values
    with get_db_connection() as conn:
        total_projects = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        planned_projects = conn.execute("SELECT COUNT(*) FROM projects WHERE status = 'not started'").fetchone()[0]
        in_progress_projects = conn.execute("SELECT COUNT(*) FROM projects WHERE status = 'in progress'").fetchone()[0]
        completed_projects = conn.execute("SELECT COUNT(*) FROM projects WHERE status = 'completed'").fetchone()[0]

        rows = conn.execute(
            "SELECT id, name, description, category, status, timestamp FROM projects ORDER BY timestamp DESC LIMIT 5"
        ).fetchall()

    recent_projects = []
    for r in rows:
        d = dict(r)
        d['formatted_ts'] = format_timestamp(d.get('timestamp'))
        recent_projects.append(d)

    return render_template(
        'index.html',
        total_projects=total_projects,
        planned_projects=planned_projects,
        in_progress_projects=in_progress_projects,
        completed_projects=completed_projects,
        recent_projects=recent_projects,
    )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/projects')
def projects():
    q = (request.args.get('q') or '').strip()
    params = []
    where = ''
    if q:
        like = f"%{q}%"
        where = "WHERE lower(name) LIKE ? OR lower(description) LIKE ? OR lower(category) LIKE ? OR lower(status) LIKE ?"
        params = [like.lower(), like.lower(), like.lower(), like.lower()]

    sql = f"SELECT * FROM projects {where} ORDER BY timestamp DESC"
    with get_db_connection() as conn:
        rows = conn.execute(sql, params).fetchall()

    projects_list = []
    for r in rows:
        d = dict(r)
        d['formatted_ts'] = format_timestamp(d.get('timestamp'))
        # prepare highlighted versions for server-side search results
        if q:
            d['highlighted_name'] = highlight(d.get('name', ''), q)
            d['highlighted_description'] = highlight(d.get('description', ''), q)
            d['highlighted_category'] = highlight(d.get('category', ''), q)
            d['highlighted_status'] = highlight(d.get('status', ''), q)
        else:
            d['highlighted_name'] = Markup.escape(d.get('name', ''))
            d['highlighted_description'] = Markup.escape(d.get('description', ''))
            d['highlighted_category'] = Markup.escape(d.get('category', ''))
            d['highlighted_status'] = Markup.escape(d.get('status', ''))
        projects_list.append(d)

    return render_template('projects.html', projects_list=projects_list, q=q)


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
