from abc import ABCMeta, abstractmethod, abstractproperty
from ..workflow.abstract_workflow import AbstractWorkFlow
from ..utils import print_msg
from ..decorators import crowdrouter

#CrowdRouter is a manager class that composes the workflow object to perform crowd tasks.
#It relies upon the workflow to manage and execute them, while it solely manages the
#crowd with metadata to provide run-time control alternatives. Extend the AbstractCrowdRouter
#class that handles its own call() method to implement pre and post conditions.
class AbstractCrowdRouter:
    __metaclass__ = ABCMeta

    #Implement any/all of these attributes in your concrete class.
    workflows = [] #Put WorkFlow classes here.
    num_allowable_requests = None #Cap off allowable requests for crowdwork tasking.
    whitelist = [] #Use whitelist to permit specific user IDs
    blacklist = [] #Use blacklist to disallow specific user IDs
    task_counts = {} #Used to tally up task executions.

    @abstractmethod
    def __init__(self):
        self.workflows = []
        self.num_allowable_requests = None
        self.whitelist = []
        self.blacklist = []
        self.task_counts = {}

    @abstractmethod
    @crowdrouter
    def route(self, crowd_request, workflow):
        crowd_response = workflow.run(crowd_request)
        self.update_task_count(workflow, crowd_response.task.get_name())
        return crowd_response

    #Update task execution counts for the specified Workflow and Task.
    def update_task_count(self, workflow, task_name):
        workflow_name = workflow.get_name()
        if not self.task_counts.get(workflow_name):
            self.task_counts[workflow_name] = {task.__name__:0 for task in workflow.tasks}
        self.task_counts[workflow_name][task_name] += 1
