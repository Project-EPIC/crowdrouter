from crowdrouter import AbstractCrowdRouter, AbstractWorkFlow, AbstractTask
from crowdrouter.task.abstract_crowd_choice import AbstractCrowdChoice
from crowdrouter.decorators import *

class MockRequest(object):
    method = None
    session = None
    path = None
    data = None
    form = None

    def __init__(self, method, path=None, crowd_response=None, data=None, form=None):
        self.method = method
        self.path = path
        self.data = data
        self.form = form
        if crowd_response:
            self.session = crowd_response.crowd_request.get_session()
        else:
            self.session = {}
        self.session["modified"] = False

class TestTask1(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        print_msg("TEST [GET]-1")
        return {"status": "OK", "msg": "TEST [GET]"}

    @task
    def post(self, crowd_request, data, form, **kwargs):
        print_msg("TEST [POST]-1")
        return {"status": "OK", "msg": "TEST [POST]"}

class TestTask2(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        print_msg("TEST [GET]-2")
        return {"status": "OK", "msg": "TEST [GET]-2"}

    @task
    def post(self, crowd_request, data, form, **kwargs):
        print_msg("TEST [POST]-2")
        return {"status": "OK", "msg": "TEST [POST]-2"}

class TestTask3(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        print_msg("TEST [GET]-3")
        return {"status": "OK", "msg": "TEST [GET]-3"}

    @task
    def post(self, crowd_request, data, form, **kwargs):
        print_msg("TEST [POST]-3")
        return {"status": "OK", "msg": "TEST [POST]-3"}

class SubTask1(TestTask1):
    pass

@task_auth_required
class TestTaskAuth(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        print_msg("TEST [GET]-TestTaskAuth")
        return {"status": "OK", "msg": "TEST [GET]-3"}

    @task
    def post(self, crowd_request, data, form, **kwargs):
        print_msg("TEST [POST]-TestTaskAuth")
        return {"status": "OK", "msg": "TEST [POST]-3"}

    def is_authenticated(self, crowd_request):
        return crowd_request.get_session().get("task_auth") == True

class BadTask(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        return {"status": "OK", "msg": "TEST [GET] - BAD"}
    @task
    def post(self, crowd_request, data, form, **kwargs):
        return {"status": "OK", "msg": "TEST [POST] - BAD"}

class TestTaskURI(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        if data.get("bad_param"):
            raise TaskError("Bad param")
        return {"status": "OK", "msg": "TEST [GET] - URI"}

    @task
    def post(self, crowd_request, data, form, **kwargs):
        return {"status": "OK", "msg": "TEST [POST] - URI", "test_id":1}

class TestTaskURI2(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        return {"status": "OK"}
    @task
    def post(self, crowd_request, data, form, **kwargs):
        return {"status": "OK"}

class TestTaskChoice1(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        return {"status": "OK"}
    @task
    def post(self, crowd_request, data, form, **kwargs):
        return {"status": "OK", "param":True}

class TestTaskChoice2(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        return {"status": "OK"}
    @task
    def post(self, crowd_request, data, form, **kwargs):
        return {"status": "OK", "number":1}

class TestTaskGuard1(AbstractTask):
    @task
    def get(self, crowd_request, data, **kwargs):
        param = kwargs['pipe_data']['param1']
        return {"status": "OK"}
    @task
    def post(self, crowd_request, data, form, **kwargs):
        param = kwargs['pipe_data']['param1']
        return {"status": "OK", "param":True}

class TestWorkFlowSolo(AbstractWorkFlow):
    tasks = [TestTask1]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return task.execute(crowd_request)

class TestWorkFlow1(AbstractWorkFlow):
    tasks = [TestTask1, TestTask2]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return task.execute(crowd_request)

class TestWorkFlow2(AbstractWorkFlow):
    tasks = [TestTask2, TestTask3]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return task.execute(crowd_request)

class TestWorkFlowSubTask(AbstractWorkFlow):
    tasks = [SubTask1]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return task.execute(crowd_request)

class TestWorkFlowURI(AbstractWorkFlow):
    tasks = [TestTaskURI]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return task.execute(crowd_request)

class TestWorkFlowBadTask(AbstractWorkFlow):
    tasks = [BadTask]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return task.execute(crowd_request)

class TestWorkFlowWithPipeline(AbstractWorkFlow):
    tasks = [TestTask1, TestTask2, TestTask3]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        if task.get_name() == "TestTask3":
            return task.execute(crowd_request)
        else:
            return self.pipeline(crowd_request, [TestTask1, TestTask2])

class TestWorkFlowPipelineIdenticalTasks(AbstractWorkFlow):
    tasks = [TestTask1, TestTask1, TestTask1]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return self.pipeline(crowd_request, [TestTask1, TestTask1, TestTask1])

class TestWorkFlowPipelineRepeat(AbstractWorkFlow):
    tasks = [TestTask1]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return self.repeat(crowd_request, 3)

class TestWorkFlowPipeline(AbstractWorkFlow):
    tasks = [TestTask1, TestTask2, TestTask3]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return self.pipeline(crowd_request)

    def pre_pipeline(self, task, pipe_data):
        pipe_data["test"] = True

    def post_pipeline(self, task, response, pipe_data):
        response.path = "/"

class TestWorkFlowPipelineURI(AbstractWorkFlow):
    tasks = [TestTaskURI, TestTaskURI2]
    def __init__(self, cr):
        self.crowdrouter = cr
    @workflow
    def run(self, task, crowd_request):
        return self.pipeline(crowd_request)

class TestWorkFlowRandom(TestWorkFlow1):
    @workflow
    def run(self, task, crowd_request):
        return self.random()

@workflow_auth_required
class TestWorkFlowAuth(TestWorkFlowSolo):
    def is_authenticated(self, crowd_request):
        return crowd_request.get_session().get("workflow_auth") == True

class TestWorkFlowNoAuthWithTaskAuth(AbstractWorkFlow):
    tasks = [TestTaskAuth]

    def __init__(self, cr):
        self.crowdrouter = cr
    @workflow
    def run(self, task, crowd_request):
        return task.execute(crowd_request)

@workflow_auth_required
class TestWorkFlowAuthWithTaskAuth(TestWorkFlowNoAuthWithTaskAuth):
    def is_authenticated(self, crowd_request):
        return crowd_request.get_session().get("workflow_auth") == True

class Choice2or3(AbstractCrowdChoice):
    t1 = TestTask2
    t2 = TestTask3

    def choice(self, crowd_request):
        if crowd_request.get_data()["param"] == True:
            return self.t1
        else:
            return self.t2

class Choice3or4(AbstractCrowdChoice):
    t1 = TestTask3
    t2 = SubTask1

    def choice(self, crowd_request):
        if crowd_request.get_data()["number"] == 1:
            return self.t1
        else:
            return self.t2

class TestWorkFlowSingleChoice(AbstractWorkFlow):
    tasks = [Choice2or3]
    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return task.execute(crowd_request)


class TestWorkFlowChoice(AbstractWorkFlow):
    tasks = [TestTaskChoice1, Choice2or3]
    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return self.pipeline(crowd_request)

class TestWorkFlowChoices(AbstractWorkFlow):
    tasks = [TestTaskChoice1, Choice2or3, TestTaskChoice2, Choice3or4]
    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return self.pipeline(crowd_request)

class TestWorkFlowConsecutiveChoices(AbstractWorkFlow):
    tasks = [TestTaskChoice1, Choice2or3, Choice3or4]
    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return self.pipeline(crowd_request)

class TestWorkFlowGuardedTasks(AbstractWorkFlow):
    tasks = [TestTask1, TestTaskGuard1]

    def __init__(self, cr):
        self.crowdrouter = cr

    @workflow
    def run(self, task, crowd_request):
        return self.pipeline(crowd_request)

    def pre_pipeline(self, task, pipe_data):
        pipe_data['param1'] = 10

class TestCrowdRouter(AbstractCrowdRouter):
    workflows = []

    def __init__(self):
        self.enable_crowd_statistics("test_crowd_statistics.db")

    @crowdrouter
    def route(self, workflow, crowd_request):
        return workflow.run(crowd_request)

    def is_authenticated(self, crowd_request):
        return crowd_request.get_session().get("username") == "admin" and crowd_request.get_session().get("password") == "password"

@crowdrouter_auth_required
class TestCrowdRouterAuth(TestCrowdRouter):
    pass
