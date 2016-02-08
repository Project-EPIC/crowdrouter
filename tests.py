from crowdrouter import AbstractCrowdRouter, AbstractWorkFlow, AbstractTask
from crowdrouter.workflow.abstract_workflow import SESSION_DATA_KEY, SESSION_PIPELINE_KEY
from crowdrouter.decorators import *
from crowdrouter.errors import *
from crowdrouter.utils import *
from test_classes import *
import inspect, unittest, random, ipdb

class Testing(unittest.TestCase):
    def setUp(self):
        self.cr = TestCrowdRouter()
        self.cr.clear_crowd_statistics()

    def test_fail_create_crowdrouter(self):
        try:
            cr = AbstractCrowdRouter()
        except TypeError as e:
            pass

    def test_success_create_crowdrouter(self):
        self.assertTrue(isinstance(self.cr, TestCrowdRouter))
        self.assertTrue(isinstance(self.cr, AbstractCrowdRouter))

    def test_fail_run_workflow(self):
        try:
            self.cr.workflows = [TestWorkFlowSolo]
            self.cr.route("NONEXISTENT WORKFLOW", "NONEXISTENT TASK", MockRequest("GET", "/"))
        except NoWorkFlowFoundError as e:
            pass

    def test_fail_run_workflow_task(self):
        try:
            self.cr.workflows = [TestWorkFlowSolo]
            self.cr.route("TestWorkFlowSolo", "NONEXISTENT TASK", MockRequest("GET", "/TestTask1"))
        except NoTaskFoundError as e:
            pass

    def test_success_run_workflow_task_get(self):
        self.cr.workflows = [TestWorkFlowSolo]
        response = self.cr.route("TestWorkFlowSolo", "TestTask1", MockRequest("GET", "/TestTask1"))
        self.assertTrue(isinstance(response, CrowdResponse))

    def test_fail_run_workflow_task_get_wrong_uri(self):
        self.cr.workflows = [TestWorkFlowSolo]
        try:
            response = self.cr.route("TestWorkFlowSolo", "TestTask1", MockRequest("GET", "/WRONG_URI"))
        except TaskError as e:
            pass

    def test_success_run_workflow_task_post(self):
        self.cr.workflows = [TestWorkFlowSolo]
        response = self.cr.route("TestWorkFlowSolo", "TestTask1", MockRequest("POST", "/TestTask1"))
        self.assertTrue(isinstance(response, CrowdResponse))

    def test_switch_workflows(self):
        self.cr.workflows = [TestWorkFlow1]
        response = self.cr.route("TestWorkFlow1", "TestTask1", MockRequest("POST", "/TestTask1"))
        self.assertTrue(response.status == "OK")
        self.cr.workflows = [TestWorkFlow2]
        response = self.cr.route("TestWorkFlow2", "TestTask2", MockRequest("POST", "/TestTask2"))
        self.assertTrue(response.status == "OK")

    def test_switch_workflows_wrong_task(self):
        self.cr.workflows = [TestWorkFlow1]
        response = self.cr.route("TestWorkFlow1", "TestTask1", MockRequest("POST", "/TestTask1"))
        self.cr.workflows = [TestWorkFlow2]
        try:
            response = self.cr.route("TestWorkFlow2", "TestTask1", MockRequest("POST", "/TestTask1"))
        except NoTaskFoundError as e:
            pass

    def test_execute_task_multiple_workflows(self):
        self.cr.workflows = [TestWorkFlow1, TestWorkFlow2]
        response = self.cr.route("TestWorkFlow1", "TestTask2", MockRequest("POST", "/TestTask2"))
        self.assertTrue(response.crowd_request.workflow_name == "TestWorkFlow1")
        response = self.cr.route("TestWorkFlow2", "TestTask2", MockRequest("POST", "/TestTask2"))
        self.assertTrue(response.crowd_request.workflow_name == "TestWorkFlow2")

    def test_send_request_no_session(self):
        self.cr.workflows = [TestWorkFlowSolo]
        try:
            mock_request = MockRequest("GET", "/TestTask1")
            mock_request.session = None
            self.cr.route("TestWorkFlowSolo", "TestTask1", mock_request)
        except NoSessionFoundError as e:
            pass

    def test_send_request_no_method(self):
        self.cr.workflows = [TestWorkFlowSolo]
        try:
            mock_request = MockRequest("GET", "/TestTask1")
            mock_request.method = None
            self.cr.route("TestWorkFlowSolo", "TestTask1", mock_request)
        except InvalidRequestError as e:
            pass

    def test_send_request_data(self):
        self.cr.workflows = [TestWorkFlowSolo]
        test_data = {"test":1}
        response = self.cr.route("TestWorkFlowSolo", "TestTask1", MockRequest("GET", "/TestTask1", data=test_data))
        self.assertEquals(response.crowd_request.get_data(), test_data)

    def test_send_request_form_data(self):
        self.cr.workflows = [TestWorkFlowSolo]
        test_data = {"test":1}
        response = self.cr.route("TestWorkFlowSolo", "TestTask1", MockRequest("POST", "/TestTask1", form=test_data))
        self.assertEquals(response.crowd_request.get_form(), test_data)

    def test_success_tally_task_executions(self):
        self.cr.workflows = [TestWorkFlow1]
        rand_count = random.randint(1, 10)
        for i in range(0, rand_count):
            self.cr.route("TestWorkFlow1", "TestTask1", MockRequest("GET", "/TestTask1"))
        self.assertEquals(self.cr.crowd_stats.task_visits["TestWorkFlow1"]["TestTask1"]["GET"], rand_count)

    def test_success_tally_multiple_task_executions(self):
        self.cr.workflows = [TestWorkFlow1]
        rand_count = random.randint(1, 10)
        for i in range(0, rand_count):
            task = random.choice(["TestTask1", "TestTask2"])
            response = self.cr.route("TestWorkFlow1", task, MockRequest(random.choice(["GET", "POST"]), "/%s" % task))

        task_counts = self.cr.crowd_stats.task_counts["TestWorkFlow1"]
        self.assertTrue(task_counts["TestTask1"]["GET"] <= rand_count)
        self.assertTrue(task_counts["TestTask2"]["POST"] <= rand_count)
        self.assertEquals(sum(task_counts["TestTask1"].values()) + sum(task_counts["TestTask2"].values()), rand_count)

    def test_success_tally_multiple_workflow_executions(self):
        self.cr.workflows = [TestWorkFlow1, TestWorkFlow2, TestWorkFlowSolo]
        self.cr.enable_crowd_statistics("test_crowd_statistics.db")

        rand_count = random.randint(1, 20)
        for i in range(0, rand_count):
            r = random.random()
            if r < 0.33:
                workflow = "TestWorkFlow1"
                task = random.choice(["TestTask1", "TestTask2"])
            elif r < 0.66:
                workflow = "TestWorkFlow2"
                task = random.choice(["TestTask2", "TestTask3"])
            else:
                workflow = "TestWorkFlowSolo"
                task = random.choice(["TestTask1"])
            response = self.cr.route(workflow, task, MockRequest(random.choice(["GET", "POST"]), "/%s" % task))

        task_counts_1 = self.cr.crowd_stats.task_counts["TestWorkFlow1"]
        self.assertTrue(task_counts_1.get("TestTask1").get("GET") or 0 <= rand_count)
        self.assertTrue(task_counts_1["TestTask2"]["POST"] or 0 <= rand_count)
        self.assertTrue(sum(task_counts_1["TestTask1"].values()) + sum(task_counts_1["TestTask2"].values()) <= rand_count)

        task_counts_2 = self.cr.crowd_stats.task_counts["TestWorkFlow2"]
        self.assertTrue(task_counts_2["TestTask2"]["GET"] <= rand_count)
        self.assertTrue(task_counts_2["TestTask3"]["POST"] <= rand_count)
        self.assertTrue(sum(task_counts_2["TestTask2"].values()) + sum(task_counts_2["TestTask3"].values()) <= rand_count)

        task_counts_solo = self.cr.crowd_stats.task_counts["TestWorkFlowSolo"]
        self.assertTrue(task_counts_1["TestTask1"]["GET"] <= rand_count)
        self.assertTrue(sum(task_counts_1["TestTask1"].values()) <= rand_count)
        self.assertTrue(sum([sum(v.values()) for v in [i for s in [v.values() for v in self.cr.crowd_stats.task_counts.values()] for i in s]]) == rand_count)

    def test_pipeline_tasks1(self):
        self.cr.workflows = [TestWorkFlowWithPipeline]
        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask1", MockRequest("GET", "/TestTask1"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask2")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask2", MockRequest("POST", "/TestTask2", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask2")
        self.assertTrue(response.crowd_request.get_method() == "POST")

    def test_pipeline_tasks2(self):
        self.cr.workflows = [TestWorkFlowWithPipeline]
        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask3", MockRequest("GET", "/TestTask3"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask3")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask1", MockRequest("GET", "/TestTask1", crowd_response=response))
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route("TestWorkFlowWithPipeline", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.task.get_name() == "TestTask2")
        self.assertTrue(response.crowd_request.get_method() == "GET")

    def test_pipeline_identical_tasks(self):
        self.cr.workflows = [TestWorkFlowPipelineIdenticalTasks]
        response = self.cr.route("TestWorkFlowPipelineIdenticalTasks", "TestTask1", MockRequest("GET", "/TestTask1"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route("TestWorkFlowPipelineIdenticalTasks", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")
        self.assertTrue(hasattr(response.crowd_request, "previous_response"))

        response = self.cr.route("TestWorkFlowPipelineIdenticalTasks", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")
        self.assertTrue(hasattr(response.crowd_request, "previous_response"))

        response = self.cr.route("TestWorkFlowPipelineIdenticalTasks", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "POST")

    def test_pipeline_repeat(self):
        self.cr.workflows = [TestWorkFlowPipelineRepeat]
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("GET", "/TestTask1"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")
        self.assertTrue(hasattr(response.crowd_request, "previous_response"))

        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "POST")

    def test_pre_pipeline(self):
        self.cr.workflows = [TestWorkFlowPipeline]
        response = self.cr.route("TestWorkFlowPipeline", "TestTask1", MockRequest("GET", "/TestTask1"))
        self.assertTrue(response.crowd_request.get_session().has_key(SESSION_DATA_KEY))

    def test_step_pipeline(self):
        self.cr.workflows = [TestWorkFlowPipeline]
        response = self.cr.route("TestWorkFlowPipeline", "TestTask1", MockRequest("GET", "/TestTask1"))
        response = self.cr.route("TestWorkFlowPipeline", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.path == "/TestTask2")
        response = self.cr.route("TestWorkFlowPipeline", "TestTask2", MockRequest("POST", "/TestTask2", crowd_response=response))
        self.assertTrue(response.path == "/TestTask3")

    def test_post_pipeline(self):
        self.cr.workflows = [TestWorkFlowPipelineRepeat]
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("GET", "/TestTask1"))
        self.assertFalse(hasattr(response, "pipeline_last"))
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertFalse(hasattr(response, "pipeline_last"))
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertFalse(hasattr(response, "pipeline_last"))
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.pipeline_last == True)

    def test_multiple_pipelines(self):
        self.cr.workflows = [TestWorkFlowPipelineRepeat]
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("GET", "/TestTask1"))
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.path == "/")
        self.assertTrue(response.crowd_request.get_session()[SESSION_PIPELINE_KEY] == {})
        #Now, do it again.
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("GET", "/TestTask1"))
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        response = self.cr.route("TestWorkFlowPipelineRepeat", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.path == "/")
        self.assertTrue(response.crowd_request.get_session()[SESSION_PIPELINE_KEY] == {})

    def test_task_uri_success(self):
        self.cr.workflows = [TestWorkFlowURI]
        response = self.cr.route("TestWorkFlowURI", "TestTaskURI", MockRequest("GET", "/TestTaskURI/1/test", data={"task_id":1}))
        self.assertTrue(response.path == "/TestTaskURI/1/test")

    def test_task_uri_extra_request_data_packaged(self):
        self.cr.workflows = [TestWorkFlowURI]
        response = self.cr.route("TestWorkFlowURI", "TestTaskURI", MockRequest("GET", "/TestTaskURI/1/test"), data={"task_id":1})
        self.assertTrue(response.path == "/TestTaskURI/1/test")

    def test_task_uri_extra_request_data_unpackaged(self):
        self.cr.workflows = [TestWorkFlowURI]
        response = self.cr.route("TestWorkFlowURI", "TestTaskURI", MockRequest("GET", "/TestTaskURI/1/test"), task_id=1)
        self.assertTrue(response.path == "/TestTaskURI/1/test")

    def test_task_uri_fail(self):
        self.cr.workflows = [TestWorkFlowURI]
        try:
            response = self.cr.route("TestWorkFlowURI", "TestTaskURI", MockRequest("GET", "/TestTaskURI", data={"bad_param":1}))
        except TaskError as e:
            pass

    def test_subclass_task(self):
        self.cr.workflows = [TestWorkFlowSubTask]
        response = self.cr.route("TestWorkFlowSubTask", "SubTask1", MockRequest("GET", "/TestTask1"))
        self.assertTrue(response.path == "/TestTask1")

    def test_error_bad_task(self):
        self.cr.workflows = [TestWorkFlowBadTask]
        try:
            response = self.cr.route("TestWorkFlowBadTask", "BadTask", MockRequest("GET", "/BadTask"))
        except TaskError as e:
            pass

    def test_pipeline_error(self):
        self.cr.workflows = [TestWorkFlowPipeline]
        response = self.cr.route("TestWorkFlowPipeline", "TestTask1", MockRequest("GET", "/TestTask1"))
        try:
            response = self.cr.route("TestWorkFlowPipeline", "TestTask2", MockRequest("GET", "/TestTask1", crowd_response=response))
        except PipelineError as e:
            pass

    def test_pipeline_restart(self):
        self.cr.workflows = [TestWorkFlowPipeline]
        response = self.cr.route("TestWorkFlowPipeline", "TestTask1", MockRequest("GET", "/TestTask1"))
        position = response.crowd_request.get_session()[SESSION_PIPELINE_KEY]
        response = self.cr.route("TestWorkFlowPipeline", "TestTask1", MockRequest("POST", "/TestTask1", crowd_response=response))
        response = self.cr.route("TestWorkFlowPipeline", "TestTask2", MockRequest("POST", "/TestTask2", crowd_response=response))
        response = self.cr.route("TestWorkFlowPipeline", "TestTask1", MockRequest("GET", "/TestTask1", crowd_response=response))
        self.assertEquals(response.crowd_request.get_session()[SESSION_PIPELINE_KEY], position)
        self.assertTrue(response.path == "/TestTask1")

    def test_crowdrouter_auth_success(self):
        self.cr.workflows = [TestWorkFlow1]
        self.cr.auth_required = True
        mr = MockRequest("GET", "/TestTask1")
        mr.session["username"] = "admin"
        mr.session["password"] = "password"
        response = self.cr.route("TestWorkFlow1", "TestTask1", mr)
        self.assertTrue(self.cr.is_authenticated(response.crowd_request))

    def test_crowdrouter_auth_fail(self):
        self.cr.workflows = [TestWorkFlow1]
        self.cr.auth_required = True
        mr = MockRequest("GET", "/TestTask1")
        mr.session["username"] = ""
        mr.session["password"] = "password"
        try:
            response = self.cr.route("TestWorkFlow1", "TestTask1", mr)
        except AuthenticationError as e:
            pass

    def test_workflow_auth_success(self):
        self.cr.workflows = [TestWorkFlowAuth]
        mr = MockRequest("GET", "/TestTask1")
        mr.session["workflow_auth"] = True
        response = self.cr.route("TestWorkFlowAuth", "TestTask1", mr)
        self.assertTrue(response.task.workflow.is_authenticated(response.crowd_request))

    def test_workflow_auth_fail(self):
        self.cr.workflows = [TestWorkFlowAuth]
        mr = MockRequest("GET", "/TestTask1")
        mr.session["workflow_auth"] = False
        try:
            response = self.cr.route("TestWorkFlowAuth", "TestTask1", mr)
        except AuthenticationError as e:
            pass

    def test_task_auth_success(self):
        self.cr.workflows = [TestWorkFlowNoAuthWithTaskAuth]
        mr = MockRequest("GET", "/TestTaskAuth")
        mr.session["task_auth"] = True
        response = self.cr.route("TestWorkFlowNoAuthWithTaskAuth", "TestTaskAuth", mr)
        self.assertTrue(response.task.is_authenticated(response.crowd_request))

    def test_task_auth_fail(self):
        self.cr.workflows = [TestWorkFlowNoAuthWithTaskAuth]
        mr = MockRequest("GET", "/TestTaskAuth")
        mr.session["task_auth"] = False
        try:
            response = self.cr.route("TestWorkFlowNoAuthWithTaskAuth", "TestTaskAuth", mr)
        except AuthenticationError as e:
            pass

    def test_auth_all(self):
        self.cr = TestCrowdRouterAuth()
        self.cr.workflows = [TestWorkFlowAuthWithTaskAuth]
        mr = MockRequest("GET", "/TestTaskAuth")
        mr.session["username"] = "admin"
        mr.session["password"] = "password"
        mr.session["workflow_auth"] = True
        mr.session["task_auth"] = True
        response = self.cr.route("TestWorkFlowAuthWithTaskAuth", "TestTaskAuth", mr)
        self.assertTrue(self.cr.is_authenticated(response.crowd_request))
        self.assertTrue(response.task.workflow.is_authenticated(response.crowd_request))
        self.assertTrue(response.task.is_authenticated(response.crowd_request))

    def test_swap_workflow_dynamically(self):
        self.cr.workflows = [TestWorkFlowSolo]
        response = self.cr.route("TestWorkFlowSolo", "TestTask1", MockRequest("GET", "/TestTask1"))
        self.assertTrue(response.path == "/TestTask1")
        self.cr.workflows = [TestWorkFlow1]
        response = self.cr.route("TestWorkFlow1", "TestTask2", MockRequest("GET", "/TestTask2"))
        self.assertTrue(response.path == "/TestTask2")

    def test_swap_task_dynamically(self):
        t = TestWorkFlowSolo
        t.tasks = [TestTask2] #Instead of TestTask1
        self.cr.workflows = [t]
        response = self.cr.route("TestWorkFlowSolo", "TestTask2", MockRequest("GET", "/TestTask2"))
        self.assertTrue(response.path == "/TestTask2")
        t.tasks = [TestTask1] #Swap back.

    def test_add_extra_request_data(self):
        self.cr.workflows = [TestWorkFlowSolo]
        extra_data = {"test_id": 1000}
        response = self.cr.route("TestWorkFlowSolo", "TestTask1", MockRequest("GET", "/TestTask1"), data=extra_data)
        self.assertTrue(extra_data == response.crowd_request.get_data().get("data"))

if __name__ == '__main__':
    unittest.main()
