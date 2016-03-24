from flask import Flask, render_template, request, Response, session, redirect, flash
from functools import wraps
from peewee import *
from crowdwork import *
from crowdrouter.errors import AuthenticationError
import ipdb, datetime

cr = MyCrowdRouter()
app = Flask(__name__)
app.secret_key = 'some_secret'

@app.route("/")
def home():
    return render_template("home.html", workflows=cr.workflows, user=session.get("user"))

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

@app.route("/ChoiceWorkFlow/<task_name>", methods=["GET", "POST"])
def pipeline(task_name):
    response = cr.pipeline(ChoiceWorkFlow, request, session)

    if response.method == "POST":
        flash("Thank you for your input!", "success")
        return redirect(response.path)
    return render_template(response.response["template"], workflow=ChoiceWorkFlow.__name__, response=response.response)

@app.route("/<workflow_name>/<task_name>", methods=["GET", "POST"])
def perform_task(workflow_name, task_name):
    try:
        response = cr.route(workflow_name, task_name, request, session)
    except AuthenticationError:
        flash("Oops! You're not allowed to perform that task.", "fail")
        return redirect("/")

    if response.method == "GET":
        return render_template(response.response["template"], workflow=workflow_name, response=response.response)
    else:
        flash("Thank you for your input!", "success")
        return redirect(response.path)

@app.route("/stats", methods=["GET"])
def stats():
    report = cr.report_crowd_statistics()
    return render_template("stats.html", report=report)

if __name__ == "__main__":
    app.run()
