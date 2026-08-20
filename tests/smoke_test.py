"""Small smoke test for the Flask app.

Usage: run this while the Flask app is running on http://127.0.0.1:5000
It will:
 - POST /add_project to create a test project
 - GET /projects and assert the page contains the project's name, status, and "Added on:" label
 - Delete the test project from the DB to clean up

This script uses only the standard library so no extra deps are required.
"""
import urllib.request
import urllib.parse
import sqlite3
import time
import sys

BASE = 'http://127.0.0.1:5000'
DB = 'projects.db'
TEST_NAME = 'Smoke Test Project'


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


def main():
    print('Posting test project...')
    code, _ = post_add_project(TEST_NAME, 'Smoke test description')
    if code not in (200, 302):
        print('Add project failed, code:', code)
        sys.exit(1)

    # give the app a moment to write to DB
    time.sleep(0.5)

    row = find_project_in_db(TEST_NAME)
    if not row:
        print('Test project not found in DB')
        sys.exit(1)
    project_id, name, status, timestamp = row
    print('Found project in DB:', row)

    code, html = get_projects()
    assert code == 200
    assert TEST_NAME in html, 'Project name not in /projects output'
    expected_status = f'Status: {status}'
    assert expected_status in html, f"Expected status text '{expected_status}' not found in /projects output"
    assert 'Added on:' in html, "Expected 'Added on:' not found in /projects output"

    print('Smoke test passed; cleaning up...')
    code = delete_project_by_id(project_id)
    if code not in (200, 302):
        print('Failed to delete test project, code:', code)
        sys.exit(1)

    print('Cleanup done. All checks passed.')


if __name__ == '__main__':
    main()
