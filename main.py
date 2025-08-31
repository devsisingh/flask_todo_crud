from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Use PostgreSQL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()

    searchtext = request.args.get('search')
    if searchtext:
        searchTodos = Todo.query.filter(or_(
            Todo.title.ilike(f"%{searchtext}%"),
            Todo.desc.ilike(f"%{searchtext}%")
        )).all()
        return render_template("index.html", allTodos=searchTodos)

    allTodos = Todo.query.all()
    return render_template("index.html", allTodos=allTodos)

@app.route('/delete/<int:sno>')
def delete(sno):
    deltodo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(deltodo)
    db.session.commit()
    return redirect("/")

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        newtitle = request.form['title']
        newdesc = request.form['desc']
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title = newtitle
        todo.desc = newdesc
        db.session.commit()
        return redirect("/")

    updatetodo = Todo.query.filter_by(sno=sno).first()
    return render_template("update.html", updatetodo=updatetodo)

# Temporary route to initialize the PostgreSQL DB
@app.route('/setup')
def setup():
    db.create_all()
    return "Database tables created successfully! ✅"

if __name__ == '__main__':
    app.run(debug=True)