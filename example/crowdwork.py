import os, sys, ipdb
sys.path.append("../dist/crowdrouter-1.5")
from crowdrouter import AbstractCrowdRouter, AbstractWorkFlow, AbstractTask
from crowdrouter.decorators import *
from TwitterSearch import *
import random, ipdb, json
RESULTS_FILE = "results.json"

class RankingImageTask(AbstractTask):
    @task("/workflow/<workflow_id>/RankingImageTask")
    def get(self, **kwargs):
        return {
            "status": "OK",
            "img":random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)]),
            "template": "ranking_image_task.html"
        }

    @task("/workflow/<workflow_id>/RankingImageTask")
    def post(self, **kwargs):
        rating = int(self.crowd_request.get_form()["rating"])
        img_filename = self.crowd_request.get_form()['image-filename']
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
    @task("/workflow/<workflow_id>/PickTweetHashtagsTask")
    def get(self, **kwargs):
        try:
            # import ipdb; ipdb.set_trace()
            tso = TwitterSearchOrder() # create a TwitterSearchOrder object
            tso.set_keywords(['earthquake']) # let's define all words we would like to have a look for
            tso.set_include_entities(False) # and don't give us all those entity information
            ts = TwitterSearch(
                consumer_key = '',
                consumer_secret = '',
                access_token = '',
                access_token_secret = ''
            )

            for tweet in ts.search_tweets_iterable(tso):
                print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )
                tweet_id = tweet["id"]
                break
        except TwitterSearchException as e: # take care of all those ugly errors if there are some
            print e
        return {"status": "OK", "tweet_id": tweet_id, "template": "pick_tweet_hashtags.html"}

    @task("/workflow/<workflow_id>/PickTweetHashtagsTask")
    def post(self, **kwargs):
        return {"status": "OK", "path": "/"}

class AnswerQuestionsTask(AbstractTask):
    @task("/workflow/<workflow_id>/AnswerQuestionsTask")
    def get(self, **kwargs):
        return {
            "status": "OK",
            "img": random.choice(["img" + str(x) + ".jpeg" for x in xrange(10)]),
            "template": "answer_questions.html"
        }

    @task("/workflow/<workflow_id>/AnswerQuestionsTask")
    def post(self, **kwargs):
        answer = self.crowd_request.get_form()["answer"]
        img_filename = self.crowd_request.get_form()['image-filename']
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
    def run(self, task):
        return task.execute()

class RankingMultipleImagesWorkFlow(AbstractWorkFlow):
    tasks = [RankingImageTask]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return self.repeat(task, 3)

class AnswerMultipleQuestionsWorkFlow(RankingMultipleImagesWorkFlow):
    tasks = [AnswerQuestionsTask]

    def __init__(self, cr):
        self.crowdrouter = cr

class MixedWorkFlow(AbstractWorkFlow):
    tasks = [PickTweetHashtagsTask, RankingImageTask, AnswerQuestionsTask, PickTweetHashtagsTask, RankingImageTask, AnswerQuestionsTask]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return self.pipeline(task)

@workflow_auth_required
class AuthWorkFlow(BasicWorkFlow):
    def is_authenticated(self, crowd_request):
        session = crowd_request.get_session()
        return session.get("user") == "admin"

class MyCrowdRouter(AbstractCrowdRouter):
    workflows = [BasicWorkFlow, RankingMultipleImagesWorkFlow, AnswerMultipleQuestionsWorkFlow, MixedWorkFlow, AuthWorkFlow]
    def __init__(self):
        self.enable_crowd_statistics("test_crowd_statistics.db")

    @crowdrouter
    def route(self, crowd_request, workflow):
        return workflow.run(crowd_request)
