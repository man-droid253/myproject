import urllib.request
import urllib.parse
import sqlite3
import time

BASE = 'http://127.0.0.1:5000'
DB = 'projects.db'
TEST_NAME = 'Pytest Smoke Project'


def post_add_project(name, description, category='Testing', status='in progress'):
    url = BASE + '/add_project'
    data = {
        'project-add': name,
        'project-description': description,
        'project-category': category,
        'status': status,
    }
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method='POST')
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.getcode(), resp.read()


def get_projects():
    url = BASE + '/projects'
    with urllib.request.urlopen(url, timeout=10) as resp:
        return resp.getcode(), resp.read().decode('utf-8')


def delete_project_by_id(project_id):
    url = f"{BASE}/delete_project/{project_id}"
    req = urllib.request.Request(url, data=b'', method='POST')
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.getcode()


def find_project_in_db(name):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    row = cur.execute("SELECT id, name, status, timestamp FROM projects WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row


def test_smoke_end_to_end():
    # Add
    code, _ = post_add_project(TEST_NAME, 'Pytest smoke test')
    assert code in (200, 302)
    time.sleep(0.5)

    # Verify DB
    row = find_project_in_db(TEST_NAME)
    assert row, 'project not found in DB after add'
    project_id, name, status, timestamp = row

    # Verify page contains name, status, and Added on label
    code, html = get_projects()
    assert code == 200
    assert TEST_NAME in html
    assert f'Status: {status}' in html
    assert 'Added on:' in html

    # Cleanup
    code = delete_project_by_id(project_id)
    assert code in (200, 302)
