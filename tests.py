from workflow.abstract_workflow import AbstractWorkFlow
from task.abstract_task import AbstractTask
from crowdrouter.abstract_crowdrouter import AbstractCrowdRouter
from crowdresponse import CrowdResponse
from crowdrequest import CrowdRequest
from errors import *
from decorators import *
from utils import *
import inspect, unittest, random

class TestTask1(AbstractTask):
    def __init__(self, crowd_request, *args, **kwargs):
        super(TestTask1, self).__init__(crowd_request)

    @task
    def exec_request(self, *args, **kwargs):
        return "TEST [GET]"

    @task
    def exec_response(self, *args, **kwargs):
        return {"status": "ok"}

    @task
    def execute(self, *args, **kwargs):
        if self.get_method() == "GET":
            return self.exec_request(args, kwargs)
        elif self.get_method() == "POST":
            return self.exec_response(args, kwargs)
        return NoTaskFoundError()

class TestTask2(AbstractTask):
    def __init__(self, crowd_request, *args, **kwargs):
        super(TestTask2, self).__init__(crowd_request)

    @task
    def exec_request(self, *args, **kwargs):
        return "TEST--2 [GET]"

    @task
    def exec_response(self, *args, **kwargs):
        return {"status": "ok"}

class TestWorkFlowSolo(AbstractWorkFlow):
    _tasks = ["TestTask1"]

    @workflow
    def run(self, crowd_request, *args, **kwargs):
        if crowd_request.get_task_name() == "TestTask1":
            task = TestTask1(crowd_request, args, kwargs)
            return task.execute(args, kwargs)
        raise NoTaskFoundError()

class TestWorkFlow(AbstractWorkFlow):
    _tasks = ["TestTask1", "TestTask2"]

    @workflow
    def run(self, crowd_request, *args, **kwargs):
        if crowd_request.get_task_name() == "TestTask1":
            task = TestTask1(crowd_request, args, kwargs)
            return task.execute(args, kwargs)
        elif crowd_request.get_task_name() == "TestTask2":
            task = TestTask2(crowd_request, args, kwargs)
            return task.execute(args, kwargs)
        raise NoTaskFoundError()

class TestWorkFlowWithPipeline(AbstractWorkFlow):
    _tasks = ["TestTask1", "TestTask2"]

    @workflow
    def run(self, crowd_request, *args, **kwargs):
        if crowd_request.get_task_name() == "TestTask1":
            task = TestTask1(crowd_request, args, kwargs)
            response = task.execute()
            if crowd_request.get_pipeline() != None:


class TestCrowdRouter(AbstractCrowdRouter):
    def __init__(self, wf):
        super(TestCrowdRouter, self).__init__(wf)

    @crowdrouter
    def call(self, crowd_request, *args, **kwargs):
        if crowd_request.get_task_name() in ["TestTask1", "TestTask2"]:
            response = self._workflow.run(crowd_request, args, kwargs)
            self.task_counts[crowd_request.get_task_name()] += 1
            return response
        raise NoTaskFoundError()

class CrowdRouterTesting(unittest.TestCase):
    def setUp(self):
        self.cr = TestCrowdRouter(TestWorkFlowSolo())

    def test_fail_create_crowdrouter(self):
        try:
            cr = AbstractCrowdRouter()
        except TypeError:
            pass

    def test_success_create_crowdrouter(self):
        self.assertTrue(isinstance(self.cr, TestCrowdRouter))
        self.assertTrue(isinstance(self.cr, AbstractCrowdRouter))
        self.assertTrue(isinstance(self.cr._workflow, TestWorkFlowSolo))
        self.assertTrue(isinstance(self.cr._workflow, AbstractWorkFlow))

    def test_fail_run_workflow_task(self):
        try:
            self.cr.call("NONEXISTENT TASK", {})
        except NoTaskFoundError:
            pass

    def test_success_run_workflow_task_get(self):
        response = self.cr.call("TestTask1", {"method":"GET"})
        self.assertTrue(isinstance(response, CrowdResponse))

    def test_success_run_workflow_task_post(self):
        response = self.cr.call("TestTask1", {"method":"POST"})
        self.assertTrue(isinstance(response, CrowdResponse))

    def test_success_tally_task_executions(self):
        rand_count = random.randint(0, 10)
        for i in range(0, rand_count):
            self.cr.call("TestTask1", {"method":"GET"})
        self.assertEquals(self.cr.task_counts["TestTask1"], rand_count)

    def test_success_tally_multiple_task_executions(self):
        self.cr = TestCrowdRouter(TestWorkFlow())
        rand_count1 = random.randint(0, 10)
        rand_count2 = random.randint(0, 10)
        for i in range(0, rand_count1):
            response = self.cr.call("TestTask1", {"method":random.choice(["GET", "POST"])})
        for i in range(0, rand_count2):
            response = self.cr.call("TestTask2", {"method":random.choice(["GET", "POST"])})
        self.assertEquals(self.cr.task_counts["TestTask1"], rand_count1)
        self.assertEquals(self.cr.task_counts["TestTask2"], rand_count2)

if __name__ == '__main__':
    unittest.main()
