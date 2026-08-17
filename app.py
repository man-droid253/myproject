from flask import Flask, render_template, request, redirect,flash
import sqlite3
    
app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure secret key

conn = sqlite3.connect('projects.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS projects
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              description TEXT NOT NULL)''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute("SELECT * FROM projects")
    projects_list = c.fetchall()
    conn.close()
    return render_template('projects.html', projects_list=projects_list)

@app.route('/add_project', methods=['POST'])
def add_project():
    if request.method == 'POST':
        project_name = request.form.get('project-add')
        project_description = request.form.get('project-description')
        flash(f'Project "{project_name}" added successfully!', 'success')  
        
        if project_name and project_description:
            conn = sqlite3.connect('projects.db')
            c = conn.cursor()
            c.execute("INSERT INTO projects (name, description) VALUES (?, ?)",
                      (project_name, project_description))
            conn.commit()
            conn.close()
    
    return redirect('/projects') 

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    flash(f'Project with ID {project_id} deleted successfully!', 'success')  
    
    return redirect('/projects')  

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()

    if request.method == 'POST':
        project_name = request.form.get('project-add')
        project_description = request.form.get('project-description')
        flash(f'Project "{project_name}" updated successfully!', 'success')
        if project_name and project_description:
            c.execute(
                "UPDATE projects SET name = ?, description = ? WHERE id = ?",
                (project_name, project_description, project_id)
            )
            conn.commit()

        conn.close()
        return redirect('/projects')

    c.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = c.fetchone()
    conn.close()

    if project is None:
        return redirect('/projects')

    return render_template('edit_project.html', project=project)


if __name__ == '__main__':
    app.run(debug=True)
