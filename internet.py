from flask import Flask, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# User roles: admin, manager, employee
USERS_FILE = 'users.json'
EMPLOYEES_FILE = 'employees.json'

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    if 'user' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_json(USERS_FILE)
        
        for user in users:
            if user['username'] == username and check_password_hash(user['password'], password):
                session['user'] = user['username']
                session['role'] = user['role']
                return redirect('/dashboard')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    employees = load_json(EMPLOYEES_FILE)
    return render_template('dashboard.html', employees=employees, role=session['role'])

@app.route('/add_employee', methods=['POST'])
def add_employee():
    if session.get('role') in ['admin', 'manager']:
        employees = load_json(EMPLOYEES_FILE)
        employees.append({
            'id': len(employees) + 1,
            'name': request.form['name'],
            'position': request.form['position'],
            'salary': request.form['salary']
        })
        save_json(EMPLOYEES_FILE, employees)
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)