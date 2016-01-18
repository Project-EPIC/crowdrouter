from crowdrouter import AbstractCrowdRouter, AbstractWorkFlow, AbstractTask
from crowdrouter.decorators import *
from crowdrouter.errors import *
from crowdrouter.utils import *
import inspect, unittest, random, ipdb

class TestTask1(AbstractTask):
    def __init__(self, crowd_request, *args, **kwargs):
        super(TestTask1, self).__init__(crowd_request)
    @task
    def exec_request(self, *args, **kwargs):
        print_msg("TEST [GET]-1")
        return {"status": "OK", "msg": "TEST [GET]"}
    @task
    def exec_response(self, *args, **kwargs):
        print_msg("TEST [POST]-1")
        return {"status": "OK", "msg": "TEST [POST]"}

class TestTask2(AbstractTask):
    def __init__(self, crowd_request, *args, **kwargs):
        super(TestTask2, self).__init__(crowd_request)
    @task
    def exec_request(self, *args, **kwargs):
        print_msg("TEST [GET]-2")
        return {"status": "OK", "msg": "TEST [GET]-2"}
    @task
    def exec_response(self, *args, **kwargs):
        print_msg("TEST [POST]-2")
        return {"status": "OK", "msg": "TEST [POST]-2"}

class TestTask3(AbstractTask):
    def __init__(self, crowd_request, *args, **kwargs):
        super(TestTask3, self).__init__(crowd_request)
    @task
    def exec_request(self, *args, **kwargs):
        print_msg("TEST [GET]-3")
        return {"status": "OK", "msg": "TEST [GET]-3"}
    @task
    def exec_response(self, *args, **kwargs):
        print_msg("TEST [POST]-3")
        return {"status": "OK", "msg": "TEST [POST]-3"}

class TestWorkFlowSolo(AbstractWorkFlow):
    def __init__(self):
        self._tasks = [TestTask1]
    @workflow
    def run(self, task, *args, **kwargs):
        return task.execute(args, kwargs)

class TestWorkFlow1(AbstractWorkFlow):
    def __init__(self):
        self._tasks = [TestTask1, TestTask2]
    @workflow
    def run(self, task, *args, **kwargs):
        return task.execute(args, kwargs)

class TestWorkFlow2(AbstractWorkFlow):
    def __init__(self):
        self._tasks = [TestTask2, TestTask3]
    @workflow
    def run(self, task, *args, **kwargs):
        return task.execute(args, kwargs)

class TestWorkFlowWithPipeline(AbstractWorkFlow):
    def __init__(self):
        self._tasks = [TestTask1, TestTask2, TestTask3]
    @workflow
    def run(self, task, *args, **kwargs):
        if task.get_name() == "TestTask3":
            return task.execute()
        else:
            return self.pipeline(task, [TestTask1, TestTask2])

class TestCrowdRouter(AbstractCrowdRouter):
    def __init__(self):
        self._workflows = []
        self._task_counts = {}

    @crowdrouter
    def route(self, crowd_request, workflow, *args, **kwargs):
        crowd_response = workflow.run(crowd_request)
        self.update_task_count(workflow, crowd_response.get_task().get_name())
        return crowd_response

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
            self.cr.route("NONEXISTENT WORKFLOW", "NONEXISTENT TASK", {})
        except NoWorkFlowFoundError:
            pass

    def test_fail_run_workflow_task(self):
        try:
            self.cr.workflows = [TestWorkFlowSolo]
            self.cr.route("TestWorkFlowSolo", "NONEXISTENT TASK", {})
        except NoTaskFoundError:
            pass

    def test_success_run_workflow_task_get(self):
        self.cr.workflows = [TestWorkFlowSolo]
        response = self.cr.route("TestWorkFlowSolo", "TestTask1", {"method":"GET"})
        self.assertTrue(isinstance(response, CrowdResponse))

    def test_success_run_workflow_task_post(self):
        self.cr.workflows = [TestWorkFlowSolo]
        response = self.cr.route("TestWorkFlowSolo", "TestTask1", {"method":"POST"})
        self.assertTrue(isinstance(response, CrowdResponse))

    def test_success_tally_task_executions(self):
        self.cr.workflows = [TestWorkFlow1]
        rand_count = random.randint(1, 10)
        for i in range(0, rand_count):
            self.cr.route("TestWorkFlow1", "TestTask1", {"method":"GET"})
        self.assertEquals(self.cr.task_counts["TestWorkFlow1"]["TestTask1"], rand_count)

    def test_success_tally_multiple_task_executions(self):
        self.cr.workflows = [TestWorkFlow1]
        rand_count = random.randint(1, 10)
        for i in range(0, rand_count):
            response = self.cr.route("TestWorkFlow1", random.choice(["TestTask1", "TestTask2"]), {"method":random.choice(["GET", "POST"])})

        self.assertTrue(self.cr.task_counts["TestWorkFlow1"]["TestTask1"] <= rand_count)
        self.assertTrue(self.cr.task_counts["TestWorkFlow1"]["TestTask2"] <= rand_count)
        self.assertEquals(sum(self.cr.task_counts["TestWorkFlow1"].values()), rand_count)

    def test_pipeline_tasks1(self):
        self.cr.workflows = [TestWorkFlowWithPipeline]
        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask1", {"method": "GET"})
        self.assertTrue(response.get_status() == "OK")
        self.assertTrue(response.get_task().get_name() == "TestTask1")
        self.assertTrue(response.get_method() == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask1", {"method": "POST"})
        self.assertTrue(response.get_status() == "OK")
        self.assertTrue(response.get_task().get_name() == "TestTask2")
        self.assertTrue(response.get_method() == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask2", {"method": "POST"})
        self.assertTrue(response.get_status() == "OK")
        self.assertTrue(response.get_task().get_name() == "TestTask2")
        self.assertTrue(response.get_method() == "POST")

    def test_pipeline_tasks2(self):
        self.cr.workflows = [TestWorkFlowWithPipeline]
        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask3", {"method": "GET"})
        self.assertTrue(response.get_status() == "OK")
        self.assertTrue(response.get_task().get_name() == "TestTask3")
        self.assertTrue(response.get_method() == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask2", {"method": "GET"})
        self.assertTrue(response.get_task().get_name() == "TestTask2")
        self.assertTrue(response.get_method() == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask2", {"method":"POST"})
        self.assertTrue(response.get_task().get_name() == "TestTask2")
        self.assertTrue(response.get_method() == "POST")

if __name__ == '__main__':
    unittest.main()
