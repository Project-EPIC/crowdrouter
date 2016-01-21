from crowdrouter import AbstractCrowdRouter, AbstractWorkFlow, AbstractTask
from crowdrouter.decorators import *
from crowdrouter.errors import *
from crowdrouter.utils import *
import inspect, unittest, random, ipdb, requests

class TestTask1(AbstractTask):
    def __init__(self, crowd_request):
        self.crowd_request = crowd_request
    @task
    def exec_request(self):
        print_msg("TEST [GET]-1")
        return {"status": "OK", "msg": "TEST [GET]"}
    @task
    def exec_response(self):
        print_msg("TEST [POST]-1")
        return {"status": "OK", "msg": "TEST [POST]"}

class TestTask2(AbstractTask):
    def __init__(self, crowd_request):
        self.crowd_request = crowd_request
    @task
    def exec_request(self):
        print_msg("TEST [GET]-2")
        return {"status": "OK", "msg": "TEST [GET]-2"}
    @task
    def exec_response(self):
        print_msg("TEST [POST]-2")
        return {"status": "OK", "msg": "TEST [POST]-2"}

class TestTask3(AbstractTask):
    def __init__(self, crowd_request):
        self.crowd_request = crowd_request
    @task
    def exec_request(self):
        print_msg("TEST [GET]-3")
        return {"status": "OK", "msg": "TEST [GET]-3"}
    @task
    def exec_response(self):
        print_msg("TEST [POST]-3")
        return {"status": "OK", "msg": "TEST [POST]-3"}

class TestWorkFlowSolo(AbstractWorkFlow):
    def __init__(self):
        self.tasks = [TestTask1]
    @workflow
    def run(self, task):
        return task.execute()

class TestWorkFlow1(AbstractWorkFlow):
    def __init__(self):
        self.tasks = [TestTask1, TestTask2]
    @workflow
    def run(self, task):
        return task.execute()

class TestWorkFlow2(AbstractWorkFlow):
    def __init__(self):
        self.tasks = [TestTask2, TestTask3]
    @workflow
    def run(self, task):
        return task.execute()

class TestWorkFlowWithPipeline(AbstractWorkFlow):
    def __init__(self):
        self.tasks = [TestTask1, TestTask2, TestTask3]
    @workflow
    def run(self, task):
        if task.get_name() == "TestTask3":
            return task.execute()
        else:
            return self.pipeline(task, [TestTask1, TestTask2])

class TestWorkFlowPipelineWithIdenticalTasks(AbstractWorkFlow):
    def __init__(self):
        self.tasks = [TestTask1, TestTask1, TestTask1]
    @workflow
    def run(self, task):
        return self.pipeline(task, [TestTask1, TestTask1, TestTask1])

class TestWorkFlowPipelineRepeat(AbstractWorkFlow):
    def __init__(self):
        self.tasks = [TestTask1, TestTask1, TestTask1]
    @workflow
    def run(self, task):
        return self.repeat(task, 3)

class TestCrowdRouter(AbstractCrowdRouter):
    def __init__(self):
        self.workflows = []
        self.task_counts = {}

    @crowdrouter
    def route(self, crowd_request, workflow):
        crowd_response = workflow.run(crowd_request)
        self.update_task_count(workflow, crowd_response.task.get_name())
        return crowd_response

class MockRequest:
    method = None
    session = None
    path = None

    def __init__(self, method, response=None):
        self.method = method
        self.path = "/" #Doesn't matter.
        if response:
            self.session = response.crowd_request.session
        else:
            self.session = {}

class Testing(unittest.TestCase):
    def setUp(self):
        self.cr = TestCrowdRouter()

    def test_fail_create_crowdrouter(self):
        try:
            cr = AbstractCrowdRouter()
        except TypeError:
            pass

    def test_success_create_crowdrouter(self):
        self.assertTrue(isinstance(self.cr, TestCrowdRouter))
        self.assertTrue(isinstance(self.cr, AbstractCrowdRouter))

    def test_fail_run_workflow(self):
        try:
            self.cr.workflows = [TestWorkFlowSolo]
            self.cr.route("NONEXISTENT WORKFLOW", "NONEXISTENT TASK", MockRequest("GET"))
        except NoWorkFlowFoundError:
            pass

    def test_fail_run_workflow_task(self):
        try:
            self.cr.workflows = [TestWorkFlowSolo]
            self.cr.route("TestWorkFlowSolo", "NONEXISTENT TASK", MockRequest("GET"))
        except NoTaskFoundError:
            pass

    def test_success_run_workflow_task_get(self):
        self.cr.workflows = [TestWorkFlowSolo]
        response = self.cr.route("TestWorkFlowSolo", "TestTask1", MockRequest("GET"))
        self.assertTrue(isinstance(response, CrowdResponse))

    def test_success_run_workflow_task_post(self):
        self.cr.workflows = [TestWorkFlowSolo]
        response = self.cr.route("TestWorkFlowSolo", "TestTask1", MockRequest("POST"))
        self.assertTrue(isinstance(response, CrowdResponse))

    def test_send_request_no_session(self):
        self.cr.workflows = [TestWorkFlowSolo]
        try:
            mock_request = MockRequest("GET")
            mock_request.session = None
            self.cr.route("TestWorkFlowSolo", "TestTask1", mock_request)
        except NoSessionFoundError:
            pass

    def test_send_request_no_method(self):
        self.cr.workflows = [TestWorkFlowSolo]
        try:
            mock_request = MockRequest("GET")
            mock_request.method = None
            self.cr.route("TestWorkFlowSolo", "TestTask1", mock_request)
        except NoRequestFoundError:
            pass

    def test_success_tally_task_executions(self):
        self.cr.workflows = [TestWorkFlow1]
        rand_count = random.randint(1, 10)
        for i in range(0, rand_count):
            self.cr.route("TestWorkFlow1", "TestTask1", MockRequest("GET"))
        self.assertEquals(self.cr.task_counts["TestWorkFlow1"]["TestTask1"], rand_count)

    def test_success_tally_multiple_task_executions(self):
        self.cr.workflows = [TestWorkFlow1]
        rand_count = random.randint(1, 10)
        for i in range(0, rand_count):
            response = self.cr.route("TestWorkFlow1", random.choice(["TestTask1", "TestTask2"]), MockRequest(random.choice(["GET", "POST"])))

        self.assertTrue(self.cr.task_counts["TestWorkFlow1"]["TestTask1"] <= rand_count)
        self.assertTrue(self.cr.task_counts["TestWorkFlow1"]["TestTask2"] <= rand_count)
        self.assertEquals(sum(self.cr.task_counts["TestWorkFlow1"].values()), rand_count)

    def test_pipeline_tasks1(self):
        self.cr.workflows = [TestWorkFlowWithPipeline]
        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask1", MockRequest("GET"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.method == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask1", MockRequest("POST", response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask2")
        self.assertTrue(response.crowd_request.method == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask2", MockRequest("POST", response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask2")
        self.assertTrue(response.crowd_request.method == "POST")

    def test_pipeline_tasks2(self):
        self.cr.workflows = [TestWorkFlowWithPipeline]
        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask3", MockRequest("GET"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask3")
        self.assertTrue(response.crowd_request.method == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask2", MockRequest("GET", response=response))
        self.assertTrue(response.task.get_name() == "TestTask2")
        self.assertTrue(response.crowd_request.method == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask2", MockRequest("POST", response=response))
        self.assertTrue(response.task.get_name() == "TestTask2")
        self.assertTrue(response.crowd_request.method == "POST")

    def test_pipeline_identical_tasks(self):
        self.cr.workflows = [TestWorkFlowPipelineWithIdenticalTasks]
        response = self.cr.route("TestWorkFlowPipelineWithIdenticalTasks", "TestTask1", MockRequest("GET"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.method == "GET")

        response = self.cr.route("TestWorkFlowPipelineWithIdenticalTasks", "TestTask1", MockRequest("POST", response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.method == "GET")
        self.assertTrue(hasattr(response.crowd_request, "prev_response"))

        response = self.cr.route("TestWorkFlowPipelineWithIdenticalTasks", "TestTask1", MockRequest("POST", response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.method == "GET")
        self.assertTrue(hasattr(response.crowd_request, "prev_response"))

        response = self.cr.route("TestWorkFlowPipelineWithIdenticalTasks", "TestTask1", MockRequest("POST", response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.method == "POST")

    def test_pipeline_repeat(self):
        self.cr.workflows = [TestWorkFlowPipelineRepeat]
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("GET"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.method == "GET")

        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.method == "GET")

        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.method == "GET")
        self.assertTrue(hasattr(response.crowd_request, "prev_response"))

        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.method == "POST")

if __name__ == '__main__':
    unittest.main()
