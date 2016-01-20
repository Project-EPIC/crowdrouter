from crowdrouter import AbstractCrowdRouter, AbstractWorkFlow, AbstractTask
from crowdrouter.decorators import *
import random, ipdb, json
RESULTS_FILE = "results.json"

class RankingImageTask(AbstractTask):
    def __init__(self, crowd_request, *args, **kwargs):
        super(RankingImageTask, self).__init__(crowd_request)
    @task
    def exec_request(self, *args, **kwargs):
        return {"status": "OK", "img":random.choice(["img1.jpeg", "img2.jpeg", "img3.jpeg", "img4.jpeg", "img5.jpeg"]), "template": "ranking_image_task.html"}
    @task
    def exec_response(self, *args, **kwargs):
        request = self._crowd_request.get_request()
        rating = int(request["data"]["rating"])
        img_filename = request['data']['image-filename']
        if rating != None:
            with open(RESULTS_FILE, "r+") as f:
                results = json.loads(f.read())
                results["image-rankings"].setdefault(img_filename, [0,0,0,0,0])[rating] += 1
                f.seek(0)
                f.write(json.dumps(results))
                f.truncate()
            return {"status":"OK"}
        else:
            return {"status":"fail"}

class AnswerQuestionsTask(AbstractTask):
    def __init__(self, crowd_request, *args, **kwargs):
        super(AnswerQuestionsTask, self).__init__(crowd_request)
    @task
    def exec_request(self, *args, **kwargs):
        return {"status": "OK", "template": "answer_questions_task.html"}
    @task
    def exec_response(self, *args, **kwargs):
        pass

class BasicWorkFlow(AbstractWorkFlow):
    def __init__(self):
        self._tasks = [RankingImageTask, AnswerQuestionsTask]
    @workflow
    def run(self, task, *args, **kwargs):
        return task.execute(args, kwargs)

class RankingMultipleImagesWorkFlow(AbstractWorkFlow):
    def __init__(self):
        self._tasks = [RankingImageTask, RankingImageTask, RankingImageTask]
    @workflow
    def run(self, task, *args, **kwargs):
        return task.execute(args, kwargs)

class MyCrowdRouter(AbstractCrowdRouter):
    def __init__(self):
        self._workflows = [BasicWorkFlow]
        self._task_counts = {}
    @crowdrouter
    def route(self, crowd_request, workflow, *args, **kwargs):
        crowd_response = workflow.run(crowd_request, args, kwargs)
        self.update_task_count(workflow, crowd_response.get_task().get_name())
        return crowd_response
