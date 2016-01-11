from workflow.abstract_workflow import AbstractWorkFlow
from utils import print_msg
from abc import ABCMeta, abstractmethod, abstractproperty
from decorators import crowdrouter

#CrowdRouter is a manager class that composes the workflow object to perform crowd tasks.
#It relies upon the workflow to manage and execute them, while it solely manages the
#crowd with metadata to provide run-time control alternatives. Extend the AbstractCrowdRouter
#class that handles its own call() method to implement pre and post conditions.
class AbstractCrowdRouter(object):
    __metaclass__ = ABCMeta
    _workflow = None
    _num_allowable_requests = None #Cap off allowable requests for crowdwork tasking.
    _whitelist = [] #Use whitelist to permit specific user IDs
    _blacklist = [] #Use blacklist to disallow specific user IDs
    _task_counts = {} #Used to tally up task executions.

    @abstractmethod
    def __init__(self, wf):
        self._workflow = wf
        self._task_counts = {task_name:0 for task_name in self._workflow._tasks}

    @abstractmethod
    @crowdrouter
    def call(self, crowd_request, *args, **kwargs):
        crowd_response = self._workflow.run(crowd_request)
        self._task_counts[crowd_response._task._name] += 1
        return crowd_response

    def workflow_getter(self):
        return self._workflow
    def workflow_setter(self, wf):
        self._workflow = wf
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
    def task_counts_setter(self, task_name, count):
        self._task_counts[task_name] = count

    workflow = property(workflow_getter, workflow_setter)
    num_allowable_requests = property(num_allowable_requests_getter, num_allowable_requests_setter)
    whitelist = property(whitelist_getter, whitelist_setter)
    blacklist = property(blacklist_getter, blacklist_setter)
    task_counts = property(task_counts_getter, task_counts_setter)
