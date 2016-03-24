import os, sys
from flask import Flask, render_template, request, Response, session, redirect, flash
from functools import wraps
from TwitterSearch import *
import ipdb, datetime, random, json

app = Flask(__name__)
app.secret_key = 'some_secret'
RESULTS_FILE = "results.json"

@app.route("/")
def home():
    return render_template("without_cr/home.html", user=session.get("user"))

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

@app.route("/pick_tweet_hashtags", methods=["GET", "POST"])
def pick_tweet_hashtags():
    if request.method == "POST":
        flash("Thanks!", "success")
        return redirect("/")
    else:
        try:
            tso = TwitterSearchOrder() # create a TwitterSearchOrder object
            tso.set_keywords(['earthquake']) # let's define all words we would like to have a look for
            tso.set_include_entities(False) # and don't give us all those entity information
            ts = TwitterSearch(
                consumer_key = 'O92NoyCEQsUq7swRKg',
                consumer_secret = 'dD7NP6ZTOv9KX28Iw6O9gtgu5MpbzTG5qyfdd7S99Y',
                access_token = '46171206-lfcESnE0WfZ8iCb4QEfreOco3PuLodM0p2lp3gC9s',
                access_token_secret = 'CURU7xIS2InzDHF5LtPpZ8gLXjWg0M3okMbmCHrIWdI'
            )

            for tweet in ts.search_tweets_iterable(tso):
                print( '@%s tweeted: %s' % (tweet['user']['screen_name'], tweet['text']))
                tweet_id = tweet["id"]
                break
        except TwitterSearchException as e: # take care of all those ugly errors if there are some
            print e
        return render_template("without_cr/pick_tweet_hashtags.html",
            response={"controller_action":"pick_tweet_hashtags", "tweet_id":tweet_id})

@app.route("/answer_question", methods=["GET", "POST"])
def answer_question():
    if request.method == "POST":
        form = request.form
        answer = form["answer"]
        img_filename = form['image-filename']
        if answer != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["answer-questions"].setdefault(img_filename, []).append(answer)
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            flash("Thanks for your input!", "success")
        else:
            flash("Something went wrong. Try again.", "fail")
        return redirect("/")
    else:
        return render_template("without_cr/answer_question.html",
            response={"controller_action":"answer_question", "img": random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})

@app.route("/answer_multiple_questions", methods=["GET", "POST"])
def answer_multiple_questions():
    if request.method == "POST":
        form = request.form
        answer = form["answer"]
        img_filename = form['image-filename']
        if answer != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["answer-questions"].setdefault(img_filename, []).append(answer)
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
        else:
            flash("Something went wrong. Try again.", "fail")

        import ipdb; ipdb.set_trace()

        #Maintain Pipeline state.
        if session.get("answer_multiple_questions") == None:
            session["answer_multiple_questions"] = 5
            return redirect("/answer_multiple_questions")

        elif session["answer_multiple_questions"] == 0:
            session["answer_multiple_questions"] = None
            flash("All done, thank you!", "success")
            return redirect("/")
        else:
            session["answer_multiple_questions"] = session["answer_multiple_questions"] - 1
            flash("Thanks for your input!", "success")
            return redirect("/answer_multiple_questions")
    else:
        return render_template("without_cr/answer_question.html",
            response={"controller_action": "answer_multiple_questions", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})


@app.route("/rank_image", methods=["GET", "POST"])
def rank_image():
    import ipdb; ipdb.set_trace()
    if request.method == "POST":
        form = request.form
        rating = int(form["rating"])
        img_filename = form['image-filename']
        if rating != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["image-rankings"].setdefault(img_filename, [0,0,0,0,0])[rating] += 1
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            flash("Thanks for your input!", "success")
        else:
            flash("Something went wrong. Try again.", "fail")
        return redirect("/")
    else:
        return render_template("without_cr/ranking_image_task.html",
            response={"controller_action": "rank_image", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})

@app.route("/rank_multiple_images", methods=["GET", "POST"])
def rank_multiple_images():
    import ipdb; ipdb.set_trace()
    if request.method == "POST":
        form = request.form
        rating = int(form["rating"])
        img_filename = form['image-filename']
        if rating != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["image-rankings"].setdefault(img_filename, [0,0,0,0,0])[rating] += 1
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
        else:
            flash("Something went wrong. Try again.", "fail")
            return redirect('/')

        import ipdb; ipdb.set_trace()

        #Maintain Pipeline state.
        if session.get("rank_multiple_images") == None:
            session["rank_multiple_images"] = 5
            return redirect("/rank_multiple_images")

        elif session["rank_multiple_images"] == 0:
            session["rank_multiple_images"] = None
            flash("All done, thank you!", "success")
            return redirect("/")
        else:
            session["rank_multiple_images"] = session["rank_multiple_images"] - 1
            flash("Thanks for your input!", "success")
            return redirect("/rank_multiple_images")
    else:
        return render_template("without_cr/ranking_image_task.html",
            response={"controller_action": "rank_multiple_images", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})


@app.route("/mixed_workflow_1", methods=["GET", "POST"])
def mixed_workflow_1():
    if request.method == "POST":
        form = request.form
        rating = int(form["rating"])
        img_filename = form['image-filename']
        if rating != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["image-rankings"].setdefault(img_filename, [0,0,0,0,0])[rating] += 1
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            return redirect("/mixed_workflow_2")
        else:
            flash("Something went wrong. Try again.", "fail")
            return redirect("/")
    else:
        return render_template("without_cr/ranking_image_task.html",
            response={"controller_action": "mixed_workflow_1", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})

@app.route("/mixed_workflow_2", methods=["GET", "POST"])
def mixed_workflow_2():
    if request.method == "POST":
        form = request.form
        answer = form["answer"]
        img_filename = form['image-filename']
        if answer != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["answer-questions"].setdefault(img_filename, []).append(answer)
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            return redirect("/mixed_workflow_3")
        else:
            flash("Something went wrong. Try again.", "fail")
            return redirect("/")
    else:
        return render_template("without_cr/answer_question.html",
            response={"controller_action": "mixed_workflow_2", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})

@app.route("/mixed_workflow_3", methods=["GET", "POST"])
def mixed_workflow_3():
    if request.method == "POST":
        return redirect("/mixed_workflow_4")
    else:
        try:
            # import ipdb; ipdb.set_trace()
            tso = TwitterSearchOrder() # create a TwitterSearchOrder object
            tso.set_keywords(['earthquake']) # let's define all words we would like to have a look for
            tso.set_include_entities(False) # and don't give us all those entity information
            ts = TwitterSearch(
                consumer_key = 'O92NoyCEQsUq7swRKg',
                consumer_secret = 'dD7NP6ZTOv9KX28Iw6O9gtgu5MpbzTG5qyfdd7S99Y',
                access_token = '46171206-lfcESnE0WfZ8iCb4QEfreOco3PuLodM0p2lp3gC9s',
                access_token_secret = 'CURU7xIS2InzDHF5LtPpZ8gLXjWg0M3okMbmCHrIWdI'
            )

            for tweet in ts.search_tweets_iterable(tso):
                print( '@%s tweeted: %s' % (tweet['user']['screen_name'], tweet['text']))
                tweet_id = tweet["id"]
                break
        except TwitterSearchException as e: # take care of all those ugly errors if there are some
            print e
        return render_template("without_cr/pick_tweet_hashtags.html",
            response={"controller_action":"mixed_workflow_3", "tweet_id":tweet_id})

@app.route("/mixed_workflow_4", methods=["GET", "POST"])
def mixed_workflow_4():
    if request.method == "POST":
        form = request.form
        answer = form["answer"]
        img_filename = form['image-filename']
        if answer != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["answer-questions"].setdefault(img_filename, []).append(answer)
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            return redirect("/mixed_workflow_5")
        else:
            flash("Something went wrong. Try again.", "fail")
            return redirect("/")
    else:
        return render_template("without_cr/answer_question.html",
            response={"controller_action": "mixed_workflow_4", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})

@app.route("/mixed_workflow_5", methods=["GET", "POST"])
def mixed_workflow_5():
    if request.method == "POST":
        form = request.form
        rating = int(form["rating"])
        img_filename = form['image-filename']
        if rating != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["image-rankings"].setdefault(img_filename, [0,0,0,0,0])[rating] += 1
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            flash("Thank you for your input!", "success")
            return redirect("/")
        else:
            flash("Something went wrong. Try again.", "fail")
            return redirect("/")
    else:
        return render_template("without_cr/ranking_image_task.html",
            response={"controller_action": "mixed_workflow_5", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})

@app.route("/choice/1", methods=["GET", "POST"])
def choice_1():
    if request.method == "POST":
        form = request.form
        rating = int(form["rating"])
        img_filename = form['image-filename']
        if rating != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["image-rankings"].setdefault(img_filename, [0,0,0,0,0])[rating] += 1
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            session["results"] = rating
            return redirect("/choice/2")
        else:
            flash("Something went wrong. Try again.", "fail")
            return redirect("/")
    else:
        return render_template("without_cr/ranking_image_task.html",
            response={"controller_action": "choice/1", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})

@app.route("/choice/2", methods=["GET", "POST"])
def choice_2():
    if request.method == "POST":
        if session["results"] > 3:
            form = request.form
            rating = int(form["rating"])
            img_filename = form['image-filename']
            if rating != None:
                with open(RESULTS_FILE, "r+") as f:
                    results = json.loads(f.read())
                    results["image-rankings"].setdefault(img_filename, [0,0,0,0,0])[rating] += 1
                    f.seek(0)
                    f.write(json.dumps(results))
                    f.truncate()
                session["results"] = rating
                return redirect("/choice/3")
            else:
                flash("Something went wrong. Try again.", "fail")
                return redirect("/")
        else:
            form = request.form
            answer = form["answer"]
            img_filename = form['image-filename']
            if answer != None:
                with open(RESULTS_FILE, "r+") as f:
                    results = json.loads(f.read())
                    results["answer-questions"].setdefault(img_filename, []).append(answer)
                    f.seek(0)
                    f.write(json.dumps(results))
                    f.truncate()
                return redirect("/choice/3")
            else:
                flash("Something went wrong. Try again.", "fail")
                return redirect("/")
    else:
        if session["results"] > 3:
            return render_template("without_cr/ranking_image_task.html",
                response={"controller_action":"choice/2", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})
        else:
            return render_template("without_cr/answer_question.html",
                response={"controller_action":"choice/2", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})


@app.route("/choice/3", methods=["GET", "POST"])
def choice_3():
    if request.method == "POST":
        form = request.form
        answer = form["answer"]
        img_filename = form['image-filename']
        if answer != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["answer-questions"].setdefault(img_filename, []).append(answer)
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            flash("Thank you for your input!", "success")
            return redirect("/")
        else:
            flash("Something went wrong. Try again.", "fail")
            return redirect("/")
    else:
        return render_template("without_cr/answer_question.html",
            response={"controller_action":"choice/3", "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)])})

@app.route("/auth_answer_question", methods=["GET", "POST"])
def auth_answer_question():
    if session.get("user") and session["user"] == "admin":
        return redirect("/answer_question")
    else:
        flash("Oops! You are not authenticated to perform this task." "fail")
        return redirect("/")

@app.route("/auth_rank_image", methods=["GET", "POST"])
def auth_rank_image():
    import ipdb; ipdb.set_trace()
    if session.get("user") and session["user"] == "admin":
        return redirect("/rank_image")
    else:
        flash("Oops! You are not authenticated to perform this task." "fail")
        return redirect("/")

@app.route("/auth_pick_tweet_hashtags", methods=["GET", "POST"])
def auth_pick_tweet_hashtags():
    if session.get("user") and session["user"] == "admin":
        return redirect("/pick_tweet_hashtags")
    else:
        flash("Oops! You are not authenticated to perform this task." "fail")
        return redirect("/")

if __name__ == "__main__":
    app.run()
