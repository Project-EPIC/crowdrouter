from flask import Flask, render_template, request, Response, session, redirect, flash
from functools import wraps
from peewee import *
from crowdwork import MyCrowdRouter, RankingMultipleImagesWorkFlow
from crowdrouter.errors import AuthenticationError
import ipdb, datetime

cr = MyCrowdRouter()
db = SqliteDatabase("database.db")
app = Flask(__name__)
app.secret_key = 'some_secret'

class BaseModel(Model):
    class Meta:
        database = db

class WorkFlow(BaseModel):
    name = CharField(null=False)
    description = CharField(null=False)
    workflow_name = CharField(null=False)
    date_created_at = DateTimeField(default=datetime.datetime.now())

    def __repr__(self):
        return "<WorkFlow[%s]: %s, %s>" % (self.id, self.name, self.workflow_name)

class Task(BaseModel):
    name = CharField(null=False)
    task_name = CharField(null=False)
    description = TextField(null=False)
    workflow_name = ForeignKeyField(WorkFlow)
    date_created_at = DateTimeField(default=datetime.datetime.now())

    def __repr__(self):
        return "<Task[%s]: %s, task:%s, workflow:%s>" % (self.id, self.name, self.task_name, self.workflow_name)

@app.route("/")
def home():
    # import ipdb; ipdb.set_trace()
    workflows = WorkFlow.select().order_by(WorkFlow.date_created_at.desc())
    return render_template("home.html", workflows=workflows, user=session.get("user"))

@app.route("/login", methods=["POST"])
def login():
    if request.form and request.form.get("username") and request.form.get("password"):
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "password":
            session["user"] = "admin"
            flash("Welcome 'admin'! Let's get to work!", "success")
            return redirect("/")
    flash("Invalid username/password combo. Please try again.", "fail")
    return redirect("/")

@app.route("/logout", methods=["POST"])
def logout():
    session["user"] = None
    flash("Bye!", "success")
    return redirect("/")

@app.route("/workflow/<int:workflow_id>/<task_name>", methods=["GET", "POST"])
def perform_task(workflow_id, task_name):
    workflow = WorkFlow.get(WorkFlow.id == workflow_id)
    # import ipdb; ipdb.set_trace()

    try:
        response = cr.route(workflow.workflow_name, task_name, request, session)
    except AuthenticationError:
        flash("Oops! You're not allowed to perform that task.", "fail")
        return redirect("/")

    if request.method == "GET":
        return render_template(response.response["template"], workflow=workflow, response=response.response)
    else:
        if response.path == "/":
            flash("Thanks for your input!", "success")
        return redirect(response.path)








def populate_tasks():
    db.drop_tables([Task, WorkFlow])
    db.create_tables([Task, WorkFlow])

    #Create WorkFlows
    basic_workflow = WorkFlow.create(name="Perform a Single Task", description="Rank an Image, Answer a Question, or Pick Out Tweet Hashtags.", workflow_name="BasicWorkFlow")
    rank_multiple_images_workflow = WorkFlow.create(name= "Rank Multiple Images", description="Rate Damage Severity of Multiple Images.", workflow_name="RankingMultipleImagesWorkFlow")
    answer_multiple_questions_workflow = WorkFlow.create(name= "Answer Multiple Questions", description="Answer Multiple Questions Based on Disaster Images", workflow_name="AnswerMultipleQuestionsWorkFlow")
    mixed_workflow = WorkFlow.create(name= "Mixed", description="Mixed WorkFlow", workflow_name="MixedWorkFlow")
    auth_workflow = WorkFlow.create(name= "Top Secret WorkFlow", description="WorkFlow for authenticated users only.", workflow_name="AuthWorkFlow")

    #Create Tasks
    Task.create(name="Rank an Image", description="Rate Damage Severity of an Image.", task_name="RankingImageTask", workflow_name=basic_workflow)
    Task.create(name="Answer a Question", description="Answer a Question.", task_name="AnswerQuestionsTask", workflow_name=basic_workflow)
    Task.create(name="Pick Tweet Hashtags", description="Select hashtags from a given tweet.", task_name="PickTweetHashtagsTask", workflow_name=basic_workflow)

    Task.create(name="Rank an Image", description="Rate Damage Severity of an Image.", task_name="RankingImageTask", workflow_name=rank_multiple_images_workflow)
    Task.create(name="Answer a Question", description="Answer a Question.", task_name="AnswerQuestionsTask", workflow_name=answer_multiple_questions_workflow)

    Task.create(name="Rank an Image", description="Rate Damage Severity of an Image.", task_name="RankingImageTask", workflow_name=mixed_workflow)
    Task.create(name="Answer a Question", description="Answer a Question.", task_name="AnswerQuestionsTask", workflow_name=mixed_workflow)
    Task.create(name="Pick Tweet Hashtags", description="Select hashtags from a given tweet.", task_name="PickTweetHashtagsTask", workflow_name=mixed_workflow)

    Task.create(name="Rank an Image", description="Rate Damage Severity of an Image.", task_name="RankingImageTask", workflow_name=auth_workflow)
    Task.create(name="Answer a Question", description="Answer a Question.", task_name="AnswerQuestionsTask", workflow_name=auth_workflow)


if __name__ == "__main__":
    db.connect()
    app.run()
