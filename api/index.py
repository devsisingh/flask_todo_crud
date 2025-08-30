from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from sqlalchemy import or_

app = Flask(__name__, instance_path='/tmp/instance')

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Make sure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Initialize the database
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
        return render_template("index.html", allTodos = searchTodos)
    
    allTodos = Todo.query.all()
    return render_template("index.html", allTodos = allTodos)

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
        db.session.add(todo)
        db.session.commit()
        return redirect("/")

    updatetodo = Todo.query.filter_by(sno=sno).first()
    return render_template("update.html", updatetodo = updatetodo)

# Initialize the database tables (migrate)
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')