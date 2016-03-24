from ..utils import METHOD_GET
from ..errors import NoRequestFoundError, NoSessionFoundError, InvalidRequestError, InvalidSessionError
from abstract_request_strategy import AbstractRequestStrategy
import ipdb, inspect

class CrowdRequest(object):
    workflow = None
    task = None
    request_strategy = None
    previous_response = None

    def __init__(self, workflow, task, request_strategy, prev_response=None):
        self.workflow = workflow
        self.task = task
        self.request_strategy = request_strategy
        self.previous_response = prev_response

    @staticmethod
    def factory(workflow, task, request_strategy=None, request=None, session=None, prev_response=None, **kwargs):
        if not isinstance(request_strategy, AbstractRequestStrategy):
            return CrowdRequest(workflow, task, request_strategy, prev_response)
        else:
            return CrowdRequest(workflow, task, AbstractRequestStrategy.factory(request, session, **kwargs), prev_response)

    #Getters
    def get_request(self):
        return self.request_strategy.request
    def get_method(self):
        return self.request_strategy.method
    def get_path(self):
        return self.request_strategy.path
    def get_session(self):
        return self.request_strategy.session
    def get_form(self):
        return self.request_strategy.form
    def get_data(self):
        return self.request_strategy.data

    @staticmethod
    def to_crowd_request(crowd_response, next_task):
        crowd_request = crowd_response.crowd_request
        crowd_request.request_strategy.method = "GET"
        crowd_request.task = next_task.__name__
        #Update Request Data with Response Data.
        crowd_request.request_strategy.data.update(crowd_response.response)
        return crowd_request

    def __repr__(self):
        return "<CrowdRequest: %s - %s - %s - %s>" % (self.workflow, self.task, self.get_method(), self.request_strategy)
