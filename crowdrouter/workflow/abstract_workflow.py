from abc import ABCMeta, abstractmethod, abstractproperty
from ..task.abstract_task import AbstractTask
from ..context import CrowdRequest
from ..decorators import workflow
from ..utils import METHOD_POST, METHOD_GET
from ..errors import NoTaskFoundError, PipelineError
import hashlib, ipdb

SESSION_PIPELINE_KEY = "cr_pipe"
SESSION_DATA_KEY = "cr_data"

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
    def run(self, task):
        crowd_response = task.execute() #dynamically call execute() for Task based on parameters.
        return crowd_response

    #Repeat is used as a convenience for piping identical tasks some number of times.
    def repeat(self, task, count):
        ordering = [task.__class__ for x in xrange(count)]
        return self.pipeline(task, ordering=ordering)

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

    #Pipelining uses session state to preserve task ordering, as well as to provide pre, step, and
    #post function hooks for task-to-task transitions.
    def pipeline(self, task, ordering=None):
        if ordering is None:
            ordering = self.tasks
        task_order = enumerate(ordering)
        crowd_request = task.crowd_request
        session = crowd_request.get_session()

        #Iterate over tasks in ordering list.
        for index, current_task in task_order:
            if current_task == task.__class__:
                #Grab the Pipeline position SHA1 Digest.
                current_position = session.get(SESSION_PIPELINE_KEY)

                #This is the first time creating state.
                if not current_position:
                    if index != 0: #But index is not the first.
                        raise PipelineError(value="Cannot execute Task %s to start pipeline." % task.get_name())

                    session[SESSION_DATA_KEY] = {}
                    session[SESSION_PIPELINE_KEY] = self.digest(task, index)
                    return task.execute(pipe_data=session[SESSION_DATA_KEY])

                #If the SHA1 Signature matches, execute task as intended.
                if current_position == self.digest(task, index):
                    #First Task: before execution, invoke pre-pipeline logic.
                    if index == 0 and crowd_request.get_method() == METHOD_GET:
                        self.pre_pipeline(task, session[SESSION_DATA_KEY])

                    response = task.execute(pipe_data=session[SESSION_DATA_KEY]) #Execute Task.

                    if crowd_request.get_method() == METHOD_POST:
                        if index < len(ordering) - 1: #If task is NOT last, then pipe it to the next one.
                            next_index, next_task = task_order.next()
                            #Perform step logic.
                            self.step_pipeline(next_task, task, response, session[SESSION_DATA_KEY])

                            #Create new CrowdRequest and invoke next task in the pipeline.
                            crowd_request = CrowdRequest.to_crowd_request(response, self.get_name(), next_task)
                            next_task = next_task(crowd_request, self)
                            session[SESSION_PIPELINE_KEY] = self.digest(next_task, next_index)
                            return next_task.execute(pipe_data=session[SESSION_DATA_KEY])

                        else: #Otherwise, we're done!
                            session[SESSION_PIPELINE_KEY] = {} #Clear out this key for another pipeline later.
                            self.post_pipeline(task, response, session[SESSION_DATA_KEY]) #Perform post logic.
                            return response
                    else:
                        return response #We're not ready to pipe yet/We're done pipelining.

        #Execution may flow here when historical session data did not allow new pipeline execution to begin.
        if session[SESSION_DATA_KEY] or session[SESSION_PIPELINE_KEY]:
            session[SESSION_DATA_KEY] = {}
            session[SESSION_PIPELINE_KEY] = {}
            return self.pipeline(task, ordering) #Re-execute this pipeline with blank pipeline session data.
        else:
            raise NoTaskFoundError(value="No Task found in the pipeline. Please reset your session data and try again.")

    #This boolean authentication function needs to be implemented if class decorator is declared.
    #Define authentication protocol for WorkFlow here.
    def is_authenticated(self, request):
        raise NotImplementedError

    def digest(self, task, index):
        return hashlib.sha1(self.get_name() + task.get_name() + str(index)).hexdigest()

    def get_name(self):
        return self.__class__.__name__
