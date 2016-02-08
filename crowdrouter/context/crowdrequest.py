from ..utils import METHOD_GET, resolve_task_uri
from ..errors import NoRequestFoundError, NoSessionFoundError, InvalidRequestError, InvalidSessionError
from abstract_request_strategy import AbstractRequestStrategy
import ipdb, inspect

class CrowdRequest(object):
    workflow_name = None
    task_name = None
    request_strategy = None
    previous_response = None

    def __init__(self, workflow_name, task_name, request_strategy, prev_response=None):
        self.workflow_name = workflow_name
        self.task_name = task_name
        self.request_strategy = request_strategy
        self.previous_response = prev_response

    @staticmethod
    def factory(workflow_name, task_name, request, session=None, prev_response=None, **kwargs):
        return CrowdRequest(workflow_name, task_name, AbstractRequestStrategy.factory(request, session, **kwargs), prev_response)

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
    def to_crowd_request(crowd_response, workflow_name, next_task):
        crowd_request = crowd_response.crowd_request
        crowd_request.request_strategy.method = "GET"
        crowd_request.task_name = next_task.__name__

        #Update Request Data with Response Data.
        crowd_request.request_strategy.data.update(crowd_response.response)

        try: #Use meta-programming to retrieve path value from method decorator.
            path = next_task.get.im_func.func_closure[1].cell_contents
        except:
            raise TaskError(value="Ensure that Task.get() for %s contains a path attribute in its decorator." % next_task.__name__)

        crowd_request.request_strategy.path = resolve_task_uri(path, crowd_request)
        return crowd_request

    def __repr__(self):
        return "<CrowdRequest: %s - %s - %s>" % (self.task_name, self.get_method(), self.request_strategy)
