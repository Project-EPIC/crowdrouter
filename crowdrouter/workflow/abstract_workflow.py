from abc import ABCMeta, abstractmethod, abstractproperty
from ..decorators import workflow
from ..utils import METHOD_POST, METHOD_GET
from ..errors import NoTaskFoundError, PipelineError
from crowd_pipeline import CrowdPipeline
import hashlib, ipdb, random

#The AbstractWorkFlow class is a template class that consolidates, orders, and executes
#its Tasks in a particular way during runtime. Subclasses will extend this base class
#by implementing the run() method.
class AbstractWorkFlow:
    __metaclass__ = ABCMeta
    crowdrouter = None #Parent CrowdRouter.
    tasks = [] #Must put AbstractTask subclasses inside this list.
    auth_required = False

    @abstractmethod
    def __init__(self, crowdrouter):
        self.auth_required = False
        self.crowdrouter = crowdrouter

    @abstractmethod
    @workflow
    def run(self, task, crowd_request):
        return task.execute(crowd_request) #dynamically call execute() for Task based on parameters.

    #Repeat is used as a convenience for piping identical tasks some number of times.
    def repeat(self, crowd_request, count):
        ordering = [crowd_request.task.__class__ for x in xrange(count)]
        return self.pipeline(crowd_request, ordering=ordering)

    #Execute a Task at random.
    def random(self, crowd_request):
        return random.choice(self.tasks).execute(crowd_request)

    #Pipelining uses session state to preserve task ordering, as well as to provide pre, step, and
    #post function hooks for task-to-task transitions.
    def pipeline(self, crowd_request, ordering=None):
        return CrowdPipeline.execute(crowd_request, ordering)

    #The pre_pipeline() function is invoked before the pipeline begins, right before the
    #first task is executed. Place any logic in here to prepare the pipeline with data (use pipe_data).
    #By default, nothing is done.
    def pre_pipeline(self, task, pipe_data):
        pass

    #The step_pipeline() function is invoked after every pipe from one task to another. Place
    #logic in here for custom session data or custom redirection. By default, nothing is done.
    def step_pipeline(self, next_task, prev_task, response, pipe_data):
        pass

    #The post_pipeline() function is invoked at the end of the pipeline, when the last task
    #has finished. Place logic in here for redirection (e.g. response['path']) after all tasks
    #have finished. By default, an extra param 'pipeline_last' is added to the response, and the
    #path is set to redirect to /.
    def post_pipeline(self, task, response, pipe_data):
        setattr(response, "pipeline_last", True)
        setattr(response, "path", "/")

    #This boolean authentication function needs to be implemented if class decorator is declared.
    #Define authentication protocol for WorkFlow here.
    def is_authenticated(self, crowd_request):
        raise NotImplementedError

    def get_name(self):
        return self.__class__.__name__

    def __repr__(self):
        return "<WorkFlow: %s>" % (self.__class__.__name__)
