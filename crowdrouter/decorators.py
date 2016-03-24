from context import CrowdRequest
from context import CrowdResponse
from context import AbstractRequestStrategy
from utils import *
from errors import *
from crowd_stats import CrowdStats
import ipdb

def choice(choice_func):
    def _wrapper(self, crowd_response):
        import ipdb; ipdb.set_trace()
        task = choice_func(crowd_response)
        if task in [self.t1, self.t2]:
            return task
        else:
            raise CrowdChoiceError(value="Invalid return type for %s.choice(). Please use either %s or %s." % (self, self.t1, self.t2))
    return _wrapper

#Task Decorator
def task(run_func):
    def _wrapper(self, crowd_request, **kwargs):
        print_msg("@task called for %s." % self)
        if self.auth_required == True:
            if not self.is_authenticated(crowd_request): #If Authentication is Turned ON.
                raise AuthenticationError(value="Authentication failed for this request through Task %s." % self)

        #Run the Task.
        if crowd_request.get_method() == "GET":
            response = run_func(self, crowd_request, crowd_request.get_data(), **kwargs)
        else:
            response = run_func(self, crowd_request, crowd_request.get_data(), crowd_request.get_form(), **kwargs)

        #Craft the Crowd Response.
        crowd_response = CrowdResponse(response, crowd_request, self)

        #If Crowd Statistics Gathering is turned ON.
        cr = self.workflow.crowdrouter
        if isinstance(cr.crowd_stats, CrowdStats):
            cr.update_crowd_statistics(crowd_response)
        return crowd_response
    return _wrapper

#Workflow Decorator
def workflow(run_func):
    def _wrapper(self, crowd_request, **kwargs):
        print_msg("@workflow called for %s." % self)
        if self.auth_required == True:
            if not self.is_authenticated(crowd_request): #If Authentication is Turned ON.
                raise AuthenticationError(value="Authentication failed for this request through WorkFlow %s." % self)
        #Run the WorkFlow.
        return run_func(self, crowd_request.task, crowd_request)
    return _wrapper

#CrowdRouter Decorator
def crowdrouter(run_func):
    def _wrapper(self, workflow, task=None, request=None, session=None, **kwargs):
        try:
            print_msg("@crowdrouter called for %s" % self)
            #Create a proper request strategy.
            request_strategy = AbstractRequestStrategy.factory(request, session, **kwargs)

            #Realize the WorkFlow object.
            workflow = realize_workflow(workflow, self)

            #Realize the Task object - accommodate pipeline-based Task instances.
            if task == None and request_strategy.session.get(SESSION_PIPELINE_KEY):
                from workflow.crowd_pipeline import CrowdPipeline
                task = CrowdPipeline.get_task_by_pipeline_key(workflow, request_strategy.session[SESSION_PIPELINE_KEY])
            task = realize_task(task, workflow)

            #Craft the CrowdRequest object.
            crowd_request = CrowdRequest.factory(workflow, task, request_strategy, request, session, **kwargs)

            #If Authentication is Turned ON.
            if self.auth_required == True:
                if not self.is_authenticated(crowd_request):
                    raise AuthenticationError(value="Authentication failed for this request through CrowdRouter %s." % self)

            #Run the Route.
            response = run_func(self, workflow, crowd_request)

            if not isinstance(response, CrowdResponse): #Ensure a CrowdResponse is returned.
                raise TypeError("CrowdRouter must return a CrowdResponse instance.")

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
