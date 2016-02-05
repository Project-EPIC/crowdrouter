from context import CrowdRequest
from context import CrowdResponse
from utils import *
from errors import *
from crowd_stats import CrowdStats
import ipdb

#Task Decorator
def task(task_uri):
    def task_decorator(run_func):
        def _wrapper(self, **kwargs):
            print_msg("@task called for %s." % self)
            if self.auth_required == True:
                if not self.is_authenticated(self.crowd_request): #If Authentication is Turned ON.
                    raise AuthenticationError(value="Authentication failed for this request through Task %s." % self)

            #Resolve Task URI with CrowdRequest params.
            path = resolve_task_uri(task_uri, self.crowd_request)

            #URI and Path must check out.
            if path != self.crowd_request.get_path():
                raise TaskError(value="Task URI '%s' does not match CrowdRequest URI '%s'." % (path, self.crowd_request.get_path()))

            response = run_func(self, **kwargs) #Run the Task.
            if not response.get("path"):
                response["path"] = path
            return CrowdResponse(response, self)

        #Each Task exec function must have a string URI value that maps its action to a URI.
        if not isinstance(task_uri, str) and not callable(run_func):
            raise TaskError(value="Invalid Task URI value. Please check that Task %s has a URI value in its declaration." % run_func.get_name())
        return _wrapper
    return task_decorator

#Workflow Decorator
def workflow(run_func):
    def _wrapper(self, crowd_request):
        print_msg("@workflow called for %s." % self)
        if self.auth_required == True:
            if not self.is_authenticated(crowd_request): #If Authentication is Turned ON.
                raise AuthenticationError(value="Authentication failed for this request through WorkFlow %s." % self)

        tasks = {task.__name__:task for task in self.tasks}
        try:
            task = tasks.get(crowd_request.task_name)(crowd_request, self)
            if task == None: #Type Checking for the Task instance.
                raise NoTaskFoundError
        except:
            raise NoTaskFoundError(value="Task %s not found. Ensure that the underlying Workflow class has declared this instance." % crowd_request.task_name)
        return run_func(self, task)
    return _wrapper

#CrowdRouter Decorator
def crowdrouter(run_func):
    def _wrapper(self, workflow_name, task_name, request, session=None):
        try:
            print_msg("@crowdrouter called for %s" % self)
            workflows = {workflow.__name__:workflow for workflow in self.workflows}

            try: #Realize the WorkFlow.
                workflow = workflows.get(workflow_name)(self)
                if workflow == None:
                    raise NoWorkFlowFoundError
            except:
                raise NoWorkFlowFoundError(value="Workflow %s not found. Ensure that the underlying CrowdRouter class has declared this instance." % workflow_name)

            #Craft the CrowdRequest object.
            crowd_request = CrowdRequest.factory(workflow_name, task_name, request, session)

            #If Authentication is Turned ON.
            if self.auth_required == True:
                if not self.is_authenticated(crowd_request):
                    raise AuthenticationError(value="Authentication failed for this request through CrowdRouter %s." % self)
            response = run_func(self, crowd_request, workflow) #Run the Route.

            if not isinstance(response, CrowdResponse): #Ensure a CrowdResponse is returned.
                raise TypeError("CrowdRouter must return a CrowdResponse instance.")

            #If Crowd Statistics Gathering is turned ON.
            if isinstance(self.crowd_stats, CrowdStats):
                self.update_crowd_statistics(workflow, response)

            return response
        except CrowdRouterError as e:
            print "[" + e.__class__.__name__ + "]: " + e.value
            raise e
    return _wrapper

#Authentication Class Decorators
def crowdrouter_auth_required(clazz):
    clazz.auth_required = True
    return clazz
def workflow_auth_required(clazz):
    clazz.auth_required = True
    return clazz
def task_auth_required(clazz):
    clazz.auth_required = True
    return clazz
