from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

Scss(app)

# set up SQLalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# generate a db for a specific user & not saving db every time
app.config['SQLALCHEMY_TRACK_NOTIFICATION'] = False
db = SQLAlchemy(app)

# modeling a data class for the db
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"tid: {self.id}"

# context manager to create / run a database when app is created
with app.app_context():
    db.create_all()

# creating a route using decorator
@app.route("/", methods=["GET", "POST"])
def index():
    # adding a task by checking the method (POST)
    if request.method == "POST":
        current_task = request.form["content"]
        new_task = MyTask(content=current_task)

        # try to establish a connection and send the new task to the db
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as err:
            print(f"ERROR: {err}")
            return f"ERROR: {err}"
    else:
        tasks = MyTask.query.order_by(MyTask.created).all()
        
        # render_template goes to the templates dir automatically
        return render_template("index.html", tasks=tasks)

@app.route("/delete/<int:id>")
def delete(id):
    delete_task = MyTask.query.get_or_404(id)

    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as err:
        print(f"ERROR: {err}")
        return f"ERROR: {err}"

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    task = MyTask.query.get_or_404(id)

    if request.method == "POST":
        task.content = request.form["content"]

        try:
            # no need to add task again
            db.session.commit()
            return redirect("/")
        except Exception as err:
            print(f"ERROR: {err}")
            return f"ERROR: {err}"
    else:
        return render_template("edit.html", task=task)

# start server
if __name__ == "__main__":
    # app.run(debug=True)    
    app.run(debug=False)
