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
    _workflows = [] #Put WorkFlow classes here.
    _num_allowable_requests = None #Cap off allowable requests for crowdwork tasking.
    _whitelist = [] #Use whitelist to permit specific user IDs
    _blacklist = [] #Use blacklist to disallow specific user IDs
    _task_counts = {} #Used to tally up task executions.

    @abstractmethod
    def __init__(self):
        self._workflows = []
        self._num_allowable_requests = None
        self._whitelist = []
        self._blacklist = []
        self._task_counts = {}

    @abstractmethod
    @crowdrouter
    def route(self, crowd_request, workflow, *args, **kwargs):
        crowd_response = workflow.run(crowd_request)
        update_task_count(workflow, crowd_response.get_task().get_name())
        return crowd_response

    #Update task execution counts for the specified Workflow and Task.
    def update_task_count(self, workflow, task_name):
        if not self.task_counts.get(workflow.get_name()):
            self.task_counts[workflow.get_name()] = {task.__name__:0 for task in workflow.tasks}
        self.task_counts[workflow.get_name()][task_name] += 1

    def workflows_getter(self):
        return self._workflows
    def workflows_setter(self, wf):
        self._workflows = wf
    def num_allowable_requests_getter(self):
        return self._num_allowable_requests
    def num_allowable_requests_setter(self, num):
        self._num_allowable_requests = num
    def whitelist_getter(self):
        return self._whitelist
    def whitelist_setter(self, userid):
        self._whitelist.append(userid)
    def blacklist_getter(self):
        return self._blacklist
    def blacklist_setter(self, userid):
        self._blacklist.append(userid)
    def task_counts_getter(self):
        return self._task_counts
    def task_counts_setter(self, workflow_name, task_name, count):
        self._task_counts[workflow_name][task_name] = count

    workflows = property(workflows_getter, workflows_setter)
    num_allowable_requests = property(num_allowable_requests_getter, num_allowable_requests_setter)
    whitelist = property(whitelist_getter, whitelist_setter)
    blacklist = property(blacklist_getter, blacklist_setter)
    task_counts = property(task_counts_getter, task_counts_setter)
