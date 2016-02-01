import os, sys, ipdb
# sys.path.append("../dist/crowdrouter-1.3")
from crowdrouter import AbstractCrowdRouter, AbstractWorkFlow, AbstractTask
from crowdrouter.decorators import *
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
    def __init__(self, cr):
        self.tasks = [RankingImageTask, AnswerQuestionsTask]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return task.execute()

class RankingMultipleImagesWorkFlow(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [RankingImageTask]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return self.repeat(task, 3)

class AnswerMultipleQuestionsWorkFlow(RankingMultipleImagesWorkFlow):
    def __init__(self, cr):
        self.tasks = [AnswerQuestionsTask]
        self.crowdrouter = cr

class MixedWorkFlow(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [RankingImageTask, AnswerQuestionsTask, RankingImageTask, RankingImageTask, AnswerQuestionsTask]
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
    def __init__(self):
        self.workflows = [BasicWorkFlow, RankingMultipleImagesWorkFlow, AnswerMultipleQuestionsWorkFlow, MixedWorkFlow, AuthWorkFlow]
        self.task_counts = {}

    @crowdrouter
    def route(self, crowd_request, workflow):
        crowd_response = workflow.run(crowd_request)
        self.update_task_count(workflow, crowd_response)
        return crowd_response
