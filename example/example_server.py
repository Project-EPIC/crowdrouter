from flask import Flask, render_template, request, session, redirect, flash
from peewee import *
from crowdwork import MyCrowdRouter
import ipdb, datetime

cr = MyCrowdRouter()
db = SqliteDatabase("database.db")
app = Flask(__name__)
app.secret_key = 'some_secret'

class Task(Model):
    name = CharField(null=False)
    task = CharField(null=False)
    description = TextField(null=False)
    date_created_at = DateTimeField(default=datetime.datetime.now())
    class Meta:
        database = db

@app.route("/")
def home():
    tasks = Task.select().order_by(Task.date_created_at.desc())
    return render_template("home.html", tasks=tasks)

@app.route("/task/<int:task_id>")
def go_to_task(task_id):
    task = Task.get(Task.id == task_id)
    response = cr.route("BasicWorkFlow", task.task, {"method":request.method}).get_response()
    return render_template(response["template"], task=task, response=response)

@app.route("/task/<int:task_id>/submit", methods=["POST"])
def submit_task(task_id):
    task = Task.get(Task.id == task_id)
    response = cr.route("BasicWorkFlow", task.task, {"method":request.method, 'data':request.form}).get_response()
    flash("Thanks for your input!", "success")
    return redirect("/")

def populate_tasks():
    db.drop_table(Task)
    db.create_table(Task)
    Task.create(name="Ranking Images", description="Rate Images out of 5 stars", task="RankingImageTask")
    Task.create(name="Answer Some Questions", description="Multiple Choice for several questions.", task="AnswerQuestionsTask")

if __name__ == "__main__":
    db.connect()
    app.run()
