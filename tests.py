from crowdrouter import AbstractCrowdRouter, AbstractWorkFlow, AbstractTask
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
            self.cr.route(TestWorkFlowSolo, "NONEXISTENT TASK", MockRequest("GET"))
        except NoTaskFoundError as e:
            pass

    def test_success_run_workflow_task_get(self):
        self.cr.workflows = [TestWorkFlowSolo]
        response = self.cr.route(TestWorkFlowSolo, TestTask1, MockRequest("GET"))
        self.assertTrue(isinstance(response, CrowdResponse))

    def test_success_run_workflow_task_post(self):
        self.cr.workflows = [TestWorkFlowSolo]
        response = self.cr.route(TestWorkFlowSolo, TestTask1, MockRequest("POST"))
        self.assertTrue(isinstance(response, CrowdResponse))

    def test_switch_workflows(self):
        self.cr.workflows = [TestWorkFlow1]
        response = self.cr.route(TestWorkFlow1, TestTask1, MockRequest("POST"))
        self.assertTrue(response.status == "OK")
        self.cr.workflows = [TestWorkFlow2]
        response = self.cr.route(TestWorkFlow2, TestTask2, MockRequest("POST"))
        self.assertTrue(response.status == "OK")

    def test_switch_workflows_wrong_task(self):
        self.cr.workflows = [TestWorkFlow1]
        response = self.cr.route(TestWorkFlow1, TestTask1, MockRequest("POST"))
        self.cr.workflows = [TestWorkFlow2]
        try:
            response = self.cr.route(TestWorkFlow2, TestTask1, MockRequest("POST"))
        except NoTaskFoundError as e:
            pass

    def test_execute_task_multiple_workflows(self):
        self.cr.workflows = [TestWorkFlow1, TestWorkFlow2]
        response = self.cr.route(TestWorkFlow1, TestTask2, MockRequest("POST"))
        self.assertTrue(response.crowd_request.workflow.__class__ == TestWorkFlow1)
        response = self.cr.route(TestWorkFlow2, TestTask2, MockRequest("POST"))
        self.assertTrue(response.crowd_request.workflow.__class__ == TestWorkFlow2)

    def test_send_request_no_session(self):
        self.cr.workflows = [TestWorkFlowSolo]
        try:
            mock_request = MockRequest("GET")
            mock_request.session = None
            self.cr.route(TestWorkFlowSolo, TestTask1, mock_request)
        except NoSessionFoundError as e:
            pass

    def test_send_request_no_method(self):
        self.cr.workflows = [TestWorkFlowSolo]
        try:
            mock_request = MockRequest("GET")
            mock_request.method = None
            self.cr.route(TestWorkFlowSolo, TestTask1, mock_request)
        except InvalidRequestError as e:
            pass

    def test_send_request_data(self):
        self.cr.workflows = [TestWorkFlowSolo]
        test_data = {"test":1}
        response = self.cr.route(TestWorkFlowSolo, TestTask1, MockRequest("GET", data=test_data))
        self.assertEquals(response.crowd_request.get_data(), test_data)

    def test_send_request_form_data(self):
        self.cr.workflows = [TestWorkFlowSolo]
        test_data = {"test":1}
        response = self.cr.route(TestWorkFlowSolo, TestTask1, MockRequest("POST", form=test_data))
        self.assertEquals(response.crowd_request.get_form(), test_data)

    def test_success_tally_task_executions(self):
        self.cr.workflows = [TestWorkFlow1]
        rand_count = random.randint(1, 10)
        for i in range(0, rand_count):
            self.cr.route(TestWorkFlow1, TestTask1, MockRequest("GET"))
        self.assertEquals(self.cr.crowd_stats.task_counts["TestWorkFlow1"]["TestTask1"]["GET"], rand_count)

    def test_success_tally_multiple_task_executions(self):
        self.cr.workflows = [TestWorkFlow1]
        rand_count = random.randint(1, 10)
        for i in range(0, rand_count):
            task = random.choice([TestTask1, TestTask2])
            response = self.cr.route(TestWorkFlow1, task, MockRequest(random.choice(["GET", "POST"])))

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
                task = random.choice([TestTask1, TestTask2])
            elif r < 0.66:
                workflow = "TestWorkFlow2"
                task = random.choice([TestTask2, TestTask3])
            else:
                workflow = "TestWorkFlowSolo"
                task = random.choice([TestTask1])
            response = self.cr.route(workflow, task, MockRequest(random.choice(["GET", "POST"])))

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
        response = self.cr.route(TestWorkFlowWithPipeline, TestTask1, MockRequest("GET"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route(TestWorkFlowWithPipeline, "TestTask1", MockRequest("POST", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask2")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route(TestWorkFlowWithPipeline, "TestTask2", MockRequest("POST", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask2")
        self.assertTrue(response.crowd_request.get_method() == "POST")

    def test_pipeline_tasks2(self):
        self.cr.workflows = [TestWorkFlowWithPipeline]
        response = self.cr.route(TestWorkFlowWithPipeline, TestTask3, MockRequest("GET"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask3")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route(TestWorkFlowWithPipeline, TestTask1, MockRequest("GET", crowd_response=response))
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route(TestWorkFlowWithPipeline, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.get_name() == "TestTask2")
        self.assertTrue(response.crowd_request.get_method() == "GET")

    def test_pipeline_identical_tasks(self):
        self.cr.workflows = [TestWorkFlowPipelineIdenticalTasks]
        response = self.cr.route(TestWorkFlowPipelineIdenticalTasks, TestTask1, MockRequest("GET"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route(TestWorkFlowPipelineIdenticalTasks, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")
        self.assertTrue(hasattr(response.crowd_request, "previous_response"))

        response = self.cr.route(TestWorkFlowPipelineIdenticalTasks, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")
        self.assertTrue(hasattr(response.crowd_request, "previous_response"))

        response = self.cr.route(TestWorkFlowPipelineIdenticalTasks, TestTask1, MockRequest("POST", "/TestTask1", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "POST")

    def test_pipeline_repeat(self):
        self.cr.workflows = [TestWorkFlowPipelineRepeat]
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("GET"))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")

        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "GET")
        self.assertTrue(hasattr(response.crowd_request, "previous_response"))

        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.status == "OK")
        self.assertTrue(response.task.get_name() == "TestTask1")
        self.assertTrue(response.crowd_request.get_method() == "POST")

    def test_pre_pipeline(self):
        self.cr.workflows = [TestWorkFlowPipeline]
        response = self.cr.route(TestWorkFlowPipeline, TestTask1, MockRequest("GET"))
        self.assertTrue(response.crowd_request.get_session().has_key(SESSION_DATA_KEY))

    def test_step_pipeline(self):
        self.cr.workflows = [TestWorkFlowPipeline]
        response = self.cr.route(TestWorkFlowPipeline, TestTask1, MockRequest("GET"))
        response = self.cr.route(TestWorkFlowPipeline, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask2)
        response = self.cr.route(TestWorkFlowPipeline, TestTask2, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask3)

    def test_post_pipeline(self):
        self.cr.workflows = [TestWorkFlowPipelineRepeat]
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("GET"))
        self.assertFalse(hasattr(response, "pipeline_last"))
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertFalse(hasattr(response, "pipeline_last"))
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertFalse(hasattr(response, "pipeline_last"))
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.pipeline_last == True)

    def test_multiple_pipelines(self):
        self.cr.workflows = [TestWorkFlowPipelineRepeat]
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("GET"))
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.crowd_request.get_session()[SESSION_PIPELINE_KEY] == None)
        #Now, do it again.
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("GET"))
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        response = self.cr.route(TestWorkFlowPipelineRepeat, TestTask1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.crowd_request.get_session()[SESSION_PIPELINE_KEY] == None)

    def test_task_extra_request_data_packaged(self):
        self.cr.workflows = [TestWorkFlowURI]
        response = self.cr.route(TestWorkFlowURI, TestTaskURI, MockRequest("GET", data={"task_id":1}))
        self.assertTrue(response.crowd_request.get_data()["task_id"] == 1)

    def test_task_extra_request_data_unpackaged(self):
        self.cr.workflows = [TestWorkFlowURI]
        response = self.cr.route(TestWorkFlowURI, TestTaskURI, MockRequest("GET"), task_id=1)
        self.assertTrue(response.crowd_request.get_data()["task_id"] == 1)

    def test_task_uri_fail(self):
        self.cr.workflows = [TestWorkFlowURI]
        try:
            response = self.cr.route(TestWorkFlowURI, TestTaskURI, MockRequest("GET", data={"bad_param":1}))
        except TaskError as e:
            pass

    def test_subclass_task(self):
        self.cr.workflows = [TestWorkFlowSubTask]
        response = self.cr.route(TestWorkFlowSubTask, SubTask1, MockRequest("GET"))
        self.assertTrue(response.task.__class__ == SubTask1)

    def test_error_bad_task(self):
        self.cr.workflows = [TestWorkFlowBadTask]
        try:
            response = self.cr.route(TestWorkFlowBadTask, BadTask, MockRequest("GET"))
        except TaskError as e:
            pass

    def test_pipeline_error(self):
        self.cr.workflows = [TestWorkFlowPipeline]
        response = self.cr.route(TestWorkFlowPipeline, TestTask1, MockRequest("GET"))
        try:
            response = self.cr.route(TestWorkFlowPipeline, TestTask2, MockRequest("GET", crowd_response=response))
        except PipelineError as e:
            pass

    def test_pipeline_restart(self):
        self.cr.workflows = [TestWorkFlowPipeline]
        response = self.cr.route(TestWorkFlowPipeline, TestTask1, MockRequest("GET"))
        position = response.crowd_request.get_session()[SESSION_PIPELINE_KEY]
        response = self.cr.route(TestWorkFlowPipeline, TestTask1, MockRequest("POST", crowd_response=response))
        response = self.cr.route(TestWorkFlowPipeline, TestTask2, MockRequest("POST", crowd_response=response))
        response = self.cr.route(TestWorkFlowPipeline, TestTask1, MockRequest("GET", crowd_response=response))
        self.assertEquals(response.crowd_request.get_session()[SESSION_PIPELINE_KEY], position)

    def test_crowdrouter_auth_success(self):
        self.cr.workflows = [TestWorkFlow1]
        self.cr.auth_required = True
        mr = MockRequest("GET")
        mr.session["username"] = "admin"
        mr.session["password"] = "password"
        response = self.cr.route(TestWorkFlow1, TestTask1, mr)
        self.assertTrue(self.cr.is_authenticated(response.crowd_request))

    def test_crowdrouter_auth_fail(self):
        self.cr.workflows = [TestWorkFlow1]
        self.cr.auth_required = True
        mr = MockRequest("GET")
        mr.session["username"] = ""
        mr.session["password"] = "password"
        try:
            response = self.cr.route(TestWorkFlow1, TestTask1, mr)
        except AuthenticationError as e:
            pass

    def test_workflow_auth_success(self):
        self.cr.workflows = [TestWorkFlowAuth]
        mr = MockRequest("GET")
        mr.session["workflow_auth"] = True
        response = self.cr.route(TestWorkFlowAuth, TestTask1, mr)
        self.assertTrue(response.task.workflow.is_authenticated(response.crowd_request))

    def test_workflow_auth_fail(self):
        self.cr.workflows = [TestWorkFlowAuth]
        mr = MockRequest("GET")
        mr.session["workflow_auth"] = False
        try:
            response = self.cr.route(TestWorkFlowAuth, TestTask1, mr)
        except AuthenticationError as e:
            pass

    def test_task_auth_success(self):
        self.cr.workflows = [TestWorkFlowNoAuthWithTaskAuth]
        mr = MockRequest("GET")
        mr.session["task_auth"] = True
        response = self.cr.route(TestWorkFlowNoAuthWithTaskAuth, TestTaskAuth, mr)
        self.assertTrue(response.task.is_authenticated(response.crowd_request))

    def test_task_auth_fail(self):
        self.cr.workflows = [TestWorkFlowNoAuthWithTaskAuth]
        mr = MockRequest("GET")
        mr.session["task_auth"] = False
        try:
            response = self.cr.route(TestWorkFlowNoAuthWithTaskAuth, TestTaskAuth, mr)
        except AuthenticationError as e:
            pass

    def test_auth_all(self):
        self.cr = TestCrowdRouterAuth()
        self.cr.workflows = [TestWorkFlowAuthWithTaskAuth]
        mr = MockRequest("GET")
        mr.session["username"] = "admin"
        mr.session["password"] = "password"
        mr.session["workflow_auth"] = True
        mr.session["task_auth"] = True
        response = self.cr.route(TestWorkFlowAuthWithTaskAuth, TestTaskAuth, mr)
        self.assertTrue(self.cr.is_authenticated(response.crowd_request))
        self.assertTrue(response.task.workflow.is_authenticated(response.crowd_request))
        self.assertTrue(response.task.is_authenticated(response.crowd_request))

    def test_swap_workflow_dynamically(self):
        self.cr.workflows = [TestWorkFlowSolo]
        response = self.cr.route(TestWorkFlowSolo, TestTask1, MockRequest("GET"))
        self.assertTrue(response.task.__class__ == TestTask1)
        self.cr.workflows = [TestWorkFlow1]
        response = self.cr.route(TestWorkFlow1, TestTask2, MockRequest("GET"))

    def test_swap_task_dynamically(self):
        t = TestWorkFlowSolo
        t.tasks = [TestTask2] #Instead of TestTask1
        self.cr.workflows = [t]
        response = self.cr.route(TestWorkFlowSolo, TestTask2, MockRequest("GET"))
        t.tasks = [TestTask1] #Swap back.

    def test_add_extra_request_data(self):
        self.cr.workflows = [TestWorkFlowSolo]
        extra_data = {"test_id": 1000}
        response = self.cr.route(TestWorkFlowSolo, TestTask1, MockRequest("GET"), data=extra_data)
        self.assertTrue(extra_data == response.crowd_request.get_data().get("data"))

    def test_task_uri_with_pipeline(self):
        self.cr.workflows = [TestWorkFlowPipelineURI]
        response = self.cr.route(TestWorkFlowPipelineURI, TestTaskURI, MockRequest("GET"), task_id=10)
        response = self.cr.route(TestWorkFlowPipelineURI, TestTaskURI, MockRequest("POST", crowd_response=response), task_id=10)

    def test_new_task_crowd_stats(self):
        self.cr.workflows = [TestWorkFlow1]
        t = TestWorkFlow1
        t.tasks = [TestTask3]
        response = self.cr.route(TestWorkFlow1, TestTask3, MockRequest("GET", "/TestTask3"))
        report = self.cr.crowd_stats.report()
        self.assertTrue(report["task_counts"]["TestWorkFlow1"].has_key("TestTask3"))
        t.tasks = [TestTask1, TestTask2] #Swap back.

    def test_pipeline_stats(self):
        self.cr.workflows = [TestWorkFlowPipeline]
        response = self.cr.route(TestWorkFlowPipeline, TestTask1, MockRequest("GET"))
        response = self.cr.route(TestWorkFlowPipeline, TestTask1, MockRequest("POST", crowd_response=response))
        report = self.cr.crowd_stats.report()["task_counts"]["TestWorkFlowPipeline"]["TestTask1"]
        self.assertTrue(report["GET"] == report["POST"] == 1)

    def test_crowd_stats_report(self):
        self.cr.workflows = [TestWorkFlowSolo, TestWorkFlow1]
        response = self.cr.route(TestWorkFlowSolo, TestTask1, MockRequest("GET"))
        response = self.cr.route(TestWorkFlow1, TestTask1, MockRequest("GET"))
        response = self.cr.route(TestWorkFlow1, TestTask1, MockRequest("POST"))
        report = self.cr.report_crowd_statistics()
        self.assertTrue(report["task_counts"].keys(), ["TestWorkFlowSolo", "TestWorkFlow1"])
        self.assertTrue(report["task_counts"]["TestWorkFlowSolo"]["TestTask1"]["GET"] == 1)
        self.assertTrue(report["task_counts"]["TestWorkFlow1"]["TestTask1"]["GET"] == 1)
        self.assertTrue(report["task_counts"]["TestWorkFlow1"]["TestTask1"]["POST"] == 1)

    def test_crowdrouter_pipeline(self):
        self.cr.workflows = [TestWorkFlowPipeline]
        response = self.cr.pipeline(TestWorkFlowPipeline, MockRequest("GET"))
        response = self.cr.pipeline(TestWorkFlowPipeline, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask2)
        self.assertTrue(response.method == "GET")
        response = self.cr.pipeline(TestWorkFlowPipeline, MockRequest("GET", crowd_response=response))
        response = self.cr.pipeline(TestWorkFlowPipeline, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask3)
        self.assertTrue(response.method == "GET")
        response = self.cr.pipeline(TestWorkFlowPipeline, MockRequest("GET", crowd_response=response))
        response = self.cr.pipeline(TestWorkFlowPipeline, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask3)
        self.assertTrue(response.method == "POST")

    def test_workflow_choice(self):
        self.cr.workflows = [TestWorkFlowSingleChoice]
        response = self.cr.route(TestWorkFlowSingleChoice, Choice2or3, MockRequest("GET"), param=True)
        self.assertTrue(response.task.__class__ == TestTask2)


    def test_workflow_pipeline_choice(self):
        self.cr.workflows = [TestWorkFlowChoice]
        response = self.cr.route(TestWorkFlowChoice, TestTaskChoice1, MockRequest("GET"))
        response = self.cr.route(TestWorkFlowChoice, TestTaskChoice1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask2)
        self.assertTrue(response.method == "GET")
        response = self.cr.route(TestWorkFlowChoice, Choice2or3, MockRequest("POST", crowd_response=response), param=True)
        self.assertTrue(response.task.__class__ == TestTask2)
        self.assertTrue(response.method == "POST")

    def test_workflow_pipeline_choice_with_cr_pipeline(self):
        self.cr.workflows = [TestWorkFlowChoice]
        response = self.cr.pipeline(TestWorkFlowChoice, MockRequest("GET"))
        response = self.cr.pipeline(TestWorkFlowChoice, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask2)
        self.assertTrue(response.method == "GET")
        response = self.cr.pipeline(TestWorkFlowChoice, MockRequest("POST", crowd_response=response), param=True)
        self.assertTrue(response.task.__class__ == TestTask2)
        self.assertTrue(response.method == "POST")

    def test_workflow_pipeline_choices(self):
        self.cr.workflows = [TestWorkFlowChoices]
        response = self.cr.route(TestWorkFlowChoices, TestTaskChoice1, MockRequest("GET"))
        response = self.cr.route(TestWorkFlowChoices, TestTaskChoice1, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask2)
        self.assertTrue(response.method == "GET")

        response = self.cr.route(TestWorkFlowChoices, Choice2or3, MockRequest("POST", crowd_response=response), param=True)
        self.assertTrue(response.task.__class__ == TestTaskChoice2)
        self.assertTrue(response.method == "GET")

        response = self.cr.route(TestWorkFlowChoices, TestTaskChoice2, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask3)
        self.assertTrue(response.method == "GET")

        response = self.cr.route(TestWorkFlowChoices, Choice3or4, MockRequest("POST", crowd_response=response), number=1)
        self.assertTrue(response.task.__class__ == TestTask3)
        self.assertTrue(response.method == "POST")

    def test_workflow_pipeline_choices_with_cr_pipeline(self):
        self.cr.workflows = [TestWorkFlowChoices]
        response = self.cr.pipeline(TestWorkFlowChoices, MockRequest("GET"))
        response = self.cr.pipeline(TestWorkFlowChoices, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask2)
        self.assertTrue(response.method == "GET")

        response = self.cr.pipeline(TestWorkFlowChoices, MockRequest("POST", crowd_response=response), param=True)
        self.assertTrue(response.task.__class__ == TestTaskChoice2)
        self.assertTrue(response.method == "GET")

        response = self.cr.pipeline(TestWorkFlowChoices, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTask3)
        self.assertTrue(response.method == "GET")

        response = self.cr.pipeline(TestWorkFlowChoices, MockRequest("POST", crowd_response=response), number=1)
        self.assertTrue(response.task.__class__ == TestTask3)
        self.assertTrue(response.method == "POST")

    def test_workflow_pipeline_consecutive_choices(self):
        pass

    def test_workflow_guarded_tasks(self):
        self.cr.workflows = [TestWorkFlowGuardedTasks]
        response = self.cr.pipeline(TestWorkFlowGuardedTasks, MockRequest("GET"))
        response = self.cr.pipeline(TestWorkFlowGuardedTasks, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTaskGuard1)
        self.assertTrue(response.crowd_request.get_session()[SESSION_DATA_KEY]['param1'] == 10)
        self.assertTrue(response.method == "GET")
        self.assertTrue(response.crowd_request.get_session()["modified"] == True)

        response = self.cr.pipeline(TestWorkFlowGuardedTasks, MockRequest("GET", crowd_response=response))
        response = self.cr.pipeline(TestWorkFlowGuardedTasks, MockRequest("POST", crowd_response=response))
        self.assertTrue(response.task.__class__ == TestTaskGuard1)
        self.assertTrue(response.method == "POST")
        self.assertTrue(response.crowd_request.get_session()[SESSION_DATA_KEY] == None)
        self.assertTrue(response.crowd_request.get_session()[SESSION_PIPELINE_KEY] == None)
        self.assertTrue(response.crowd_request.get_session()["modified"] == True)


    #TODO: Test cr.pipline when there is no pipeline.

    # def test_workflow_random(self):
    #     self.cr.workflows = [TestWorkFlowRandom]
    #     response = self.cr.route(TestWorkFlow2, TestTask1, MockRequest("GET", "/TestTask1"))



if __name__ == '__main__':
    unittest.main()
