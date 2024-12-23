from flask import *
from pymongo import MongoClient
from werkzeug.security import *
from bson.objectid import *


app = Flask(__name__)
app.secret_key = "12345"

client=MongoClient('mongodb+srv://YashmitSunkara:11132008@cluster0.vjgqqbm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.task_manager
users_collection = db.users
tasks_collection = db.tasks


@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    tasks = list(tasks_collection.find({"user": session['user']}))
    print(tasks)
    return render_template('index.html', tasks=tasks, user=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({"username": username})
        print(username, user['password'])
        print(user)
        print(check_password_hash(user['password'], password))

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            session['passsword'] = password
            print('Login Succesful')
            print("Login Succesful")
            return redirect(url_for('index'))
        else:
            print('Invalid Username or Password')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)
        if users_collection.find_one({"username":username}):
            print("Username already exists. Try another one")  
        else:
            users_collection.insert_one({"username": username, "password": generate_password_hash(password)})
            print("Registration Successful") 

    return render_template('register.html')

@app.route('/add', methods=['POST'])
def add_task():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    if title:
        tasks_collection.insert_one({"title": title, "description": description, "user": session['user']})
    return redirect(url_for('index'))

@app.route('/edit/<task_id>', methods=['POST'])
def edit_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    tasks_collection.update_one(
        {"_id": ObjectId(task_id), "user": session['user']},
        {"$set": {"title": title, "description": description}}
    )
    return redirect(url_for('index'))

@app.route('/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    tasks_collection.delete_one({"_id": ObjectId(task_id), "user": session['user']})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
