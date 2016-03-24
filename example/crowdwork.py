import os, sys, ipdb
sys.path.append("../dist/crowdrouter-1.5.5")
from crowdrouter import AbstractCrowdRouter, AbstractWorkFlow, AbstractTask
from crowdrouter.decorators import *
from crowdrouter.task.abstract_crowd_choice import AbstractCrowdChoice
from TwitterSearch import *
import random, ipdb, json
RESULTS_FILE = "results.json"

class RankingImageTask(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        return {
            "status": "OK",
            "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)]),
            "template": "ranking_image_task.html"
        }

    @task
    def post(self, crowd_request, data, form, **kwargs):
        rating = int(form["rating"])
        img_filename = form['image-filename']
        if rating != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["image-rankings"].setdefault(img_filename, [0,0,0,0,0])[rating] += 1
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            return {"status":"OK", "path":"/"}
        else:
            return {"status":"fail"}

class PickTweetHashtagsTask(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
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
                print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )
                tweet_id = tweet["id"]
                break
        except TwitterSearchException as e: # take care of all those ugly errors if there are some
            print e
        return {"status": "OK", "tweet_id": tweet_id, "template": "pick_tweet_hashtags.html"}

    @task
    def post(self, crowd_request, data, form, **kwargs):
        return {"status": "OK", "path": "/"}

class AnswerQuestionsTask(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        return {
            "status": "OK",
            "img": random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)]),
            "template": "answer_questions.html"
        }

    @task
    def post(self, crowd_request, data, form, **kwargs):
        answer = form["answer"]
        img_filename = form['image-filename']
        if answer != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["answer-questions"].setdefault(img_filename, []).append(answer)
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            return {"status":"OK", "path":"/"}
        else:
            return {"status":"fail"}

class BasicWorkFlow(AbstractWorkFlow):
    tasks = [RankingImageTask, AnswerQuestionsTask, PickTweetHashtagsTask]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return task.execute(crowd_request)

class RankingMultipleImagesWorkFlow(AbstractWorkFlow):
    tasks = [RankingImageTask]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return self.repeat(crowd_request, 3)

class AnswerMultipleQuestionsWorkFlow(RankingMultipleImagesWorkFlow):
    tasks = [AnswerQuestionsTask]

    def __init__(self, cr):
        self.crowdrouter = cr

class MixedWorkFlow(AbstractWorkFlow):
    tasks = [PickTweetHashtagsTask, RankingImageTask, AnswerQuestionsTask, PickTweetHashtagsTask, RankingImageTask, AnswerQuestionsTask]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return self.pipeline(crowd_request)

class ChoiceRankOrQuestion(AbstractCrowdChoice):
    t1 = RankingImageTask
    t2 = AnswerQuestionsTask

    def choice(self, crowd_request):
        if crowd_request.get_data().get("param"):
            return self.t1
        else:
            return self.t2

class ChoiceWorkFlow(AbstractWorkFlow):
    tasks = [RankingImageTask, ChoiceRankOrQuestion, AnswerQuestionsTask]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return self.pipeline(crowd_request)

    def pre_pipeline(self, task, pipe_data):
        pipe_data["param"] = True

@workflow_auth_required
class AuthWorkFlow(BasicWorkFlow):
    def is_authenticated(self, crowd_request):
        session = crowd_request.get_session()
        return session.get("user") == "admin"

class MyCrowdRouter(AbstractCrowdRouter):
    workflows = [BasicWorkFlow, RankingMultipleImagesWorkFlow, ChoiceWorkFlow, AnswerMultipleQuestionsWorkFlow, MixedWorkFlow, AuthWorkFlow]
    def __init__(self):
        self.enable_crowd_statistics("test_crowd_statistics.db")

    @crowdrouter
    def route(self, workflow, crowd_request):
        return workflow.run(crowd_request)
