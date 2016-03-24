from abc import ABCMeta, abstractmethod, abstractproperty
from ..workflow.abstract_workflow import AbstractWorkFlow
from ..utils import print_msg
from ..decorators import crowdrouter
from ..crowd_stats import CrowdStats
import ipdb

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
    task_visits = {} #Used to tally up task visits.
    auth_required = False #Used to flag whether authentication required for this class.
    crowd_stats = None #Helper class to manage crowd statistics

    @abstractmethod
    def __init__(self):
        self.num_allowable_requests = None
        self.whitelist = []
        self.blacklist = []
        #% authenticated users vs. non-authenticated
        #time taken to complete task.
        self.auth_required = False
        self.crowd_stats = CrowdStats()

    @abstractmethod
    @crowdrouter
    def route(self, workflow, crowd_request, **kwargs):
        return workflow.run(crowd_request, **kwargs)

    def pipeline(self, workflow, request, session=None, **kwargs):
        return self.route(workflow, task=None, request=request, session=session, **kwargs)

    #Method to initialize crowd stats.
    def enable_crowd_statistics(self, db_path):
        self.crowd_stats = CrowdStats(db_path, self.workflows)

    #Update Crowd Stats.
    def update_crowd_statistics(self, crowd_response):
        self.crowd_stats.update(crowd_response)

    #Report Crowd Stats.
    def report_crowd_statistics(self):
        return self.crowd_stats.report()

    def clear_crowd_statistics(self):
        self.crowd_stats.clear()

    #This boolean authentication function needs to be implemented if class decorator is declared.
    #Define authentication protocol for CrowdRouter here.
    def is_authenticated(self, request):
        raise NotImplementedError
