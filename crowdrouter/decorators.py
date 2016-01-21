from crowdresponse import CrowdResponse
from crowdrequest import CrowdRequest
from utils import *
from errors import *
import ipdb

def task(run_func):
    def _wrapper(self):
        print_msg("@task called for %s." % self)
        response = run_func(self)
        return CrowdResponse(response, self)
    return _wrapper

def workflow(run_func):
    def _wrapper(self, crowd_request):
        print_msg("@workflow called for %s." % self)
        tasks = {task.__name__:task for task in self.tasks}
        try:
            task = tasks.get(crowd_request.task_name)(crowd_request)
            if task == None: #Type Checking for the Task instance.
                raise NoTaskFoundError
        except:
            raise NoTaskFoundError("Task %s not found. Ensure that the underlying Workflow class has declared this instance." % crowd_request.task_name)
        return run_func(self, task)
    return _wrapper

def crowdrouter(run_func):
    def _wrapper(self, workflow_name, task_name, request):
        print_msg("@crowdrouter called for %s" % self)
        workflows = {workflow.__name__:workflow for workflow in self.workflows}
        try:
            workflow = workflows.get(workflow_name)() #Realize the WorkFlow.
            if workflow == None:
                raise NoWorkFlowFoundError
        except:
            raise NoWorkFlowFoundError("Workflow %s not found. Ensure that the underlying CrowdRouter class has declared this instance." % workflow_name)

        crowd_request = CrowdRequest(workflow_name, task_name, request)
        response = run_func(self, crowd_request, workflow) #Run the Route.

        if not isinstance(response, CrowdResponse): #Ensure a CrowdResponse is returned.
            raise TypeError("CrowdRouter must return a CrowdResponse instance.")
        return response
    return _wrapper
