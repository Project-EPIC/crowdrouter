from crowdrouter import AbstractCrowdRouter, AbstractWorkFlow, AbstractTask
from crowdrouter.decorators import *

class MockRequest(object):
    method = None
    session = None
    path = None
    data = None
    form = None

    def __init__(self, method, path, crowd_response=None, data=None, form=None):
        self.method = method
        self.path = path
        self.data = data
        self.form = form
        if crowd_response:
            self.session = crowd_response.crowd_request.get_session()
        else:
            self.session = {}

class TestTask1(AbstractTask):
    @task("/TestTask1")
    def get(self, **kwargs):
        print_msg("TEST [GET]-1")
        return {"status": "OK", "msg": "TEST [GET]"}

    @task("/TestTask1")
    def post(self, **kwargs):
        print_msg("TEST [POST]-1")
        return {"status": "OK", "msg": "TEST [POST]"}

class TestTask2(AbstractTask):
    @task("/TestTask2")
    def get(self, **kwargs):
        print_msg("TEST [GET]-2")
        return {"status": "OK", "msg": "TEST [GET]-2"}

    @task("/TestTask2")
    def post(self, **kwargs):
        print_msg("TEST [POST]-2")
        return {"status": "OK", "msg": "TEST [POST]-2"}

class TestTask3(AbstractTask):
    @task("/TestTask3")
    def get(self, **kwargs):
        print_msg("TEST [GET]-3")
        return {"status": "OK", "msg": "TEST [GET]-3"}

    @task("/TestTask3")
    def post(self, **kwargs):
        print_msg("TEST [POST]-3")
        return {"status": "OK", "msg": "TEST [POST]-3"}

class SubTask1(TestTask1):
    pass

@task_auth_required
class TestTaskAuth(AbstractTask):
    @task("/TestTaskAuth")
    def get(self, **kwargs):
        print_msg("TEST [GET]-TestTaskAuth")
        return {"status": "OK", "msg": "TEST [GET]-3"}

    @task("/TestTaskAuth")
    def post(self, **kwargs):
        print_msg("TEST [POST]-TestTaskAuth")
        return {"status": "OK", "msg": "TEST [POST]-3"}

    def is_authenticated(self, crowd_request):
        return crowd_request.get_session().get("task_auth") == True

class BadTask(AbstractTask):
    @task
    def get(self, **kwargs):
        return {"status": "OK", "msg": "TEST [GET] - BAD"}
    @task
    def post(self, **kwargs):
        return {"status": "OK", "msg": "TEST [POST] - BAD"}

class TestTaskURI(AbstractTask):
    @task("/TestTaskURI/<task_id>/test")
    def get(self, **kwargs):
        return {"status": "OK", "msg": "TEST [GET] - URI"}

    @task("/TestTaskURI/<task_id>/test")
    def post(self, **kwargs):
        return {"status": "OK", "msg": "TEST [POST] - URI"}

class TestWorkFlowSolo(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [TestTask1]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return task.execute()

class TestWorkFlow1(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [TestTask1, TestTask2]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return task.execute()

class TestWorkFlow2(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [TestTask2, TestTask3]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return task.execute()

class TestWorkFlowSubTask(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [SubTask1]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return task.execute()

class TestWorkFlowURI(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [TestTaskURI]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return task.execute()

class TestWorkFlowBadTask(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [BadTask]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return task.execute()

class TestWorkFlowWithPipeline(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [TestTask1, TestTask2, TestTask3]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        if task.get_name() == "TestTask3":
            return task.execute()
        else:
            return self.pipeline(task, [TestTask1, TestTask2])

class TestWorkFlowPipelineIdenticalTasks(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [TestTask1, TestTask1, TestTask1]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return self.pipeline(task, [TestTask1, TestTask1, TestTask1])

class TestWorkFlowPipelineRepeat(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [TestTask1]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return self.repeat(task, 3)

class TestWorkFlowPipeline(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [TestTask1, TestTask2, TestTask3]
        self.crowdrouter = cr

    @workflow
    def run(self, task):
        return self.pipeline(task)

    def pre_pipeline(self, task, pipe_data):
        pipe_data["test"] = True

    def post_pipeline(self, task, response, pipe_data):
        response.path = "/"

@workflow_auth_required
class TestWorkFlowAuth(TestWorkFlowSolo):
    def is_authenticated(self, crowd_request):
        return crowd_request.get_session().get("workflow_auth") == True

class TestWorkFlowNoAuthWithTaskAuth(AbstractWorkFlow):
    def __init__(self, cr):
        self.tasks = [TestTaskAuth]
        self.crowdrouter = cr
    @workflow
    def run(self, task):
        return task.execute()

@workflow_auth_required
class TestWorkFlowAuthWithTaskAuth(TestWorkFlowNoAuthWithTaskAuth):
    def is_authenticated(self, crowd_request):
        return crowd_request.get_session().get("workflow_auth") == True

class TestCrowdRouter(AbstractCrowdRouter):
    def __init__(self):
        self.workflows = []
        self.task_counts = {}

    @crowdrouter
    def route(self, crowd_request, workflow):
        crowd_response = workflow.run(crowd_request)
        self.update_task_count(workflow, crowd_response)
        return crowd_response

    def is_authenticated(self, crowd_request):
        return crowd_request.get_session().get("username") == "admin" and crowd_request.get_session().get("password") == "password"

@crowdrouter_auth_required
class TestCrowdRouterAuth(TestCrowdRouter):
    pass
