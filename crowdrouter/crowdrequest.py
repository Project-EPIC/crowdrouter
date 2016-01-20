from utils import METHOD_GET
from errors import NoRequestFoundError, NoSessionFoundError
import ipdb

class CrowdRequest:
    _workflow_name = None
    _task_name = None
    _request = None
    _session = None

    def __init__(self, workflow_name, task_name, request):
        self._workflow_name = workflow_name
        self._task_name = task_name
        self._request = self.bind_request(request)
        self._session = self.bind_session(request)

    #Hunt down the request object.
    def bind_request(self, request):
        if hasattr(request, "method"):
            return request
        if isinstance(request, dict) and request.has_key("method"):
            return request
        if isinstance(request, dict) and request.has_key("request"):
            return self.bind_request(request["request"])
        raise NoRequestFoundError()

    #Hunt down the session object.
    def bind_session(self, request):
        if hasattr(request, "session"):
            return request.session
        if isinstance(request, dict) and request.has_key("session"):
            return request['session']
        raise NoSessionFoundError()

    def get_workflow_name(self):
        return self._workflow_name

    def get_task_name(self):
        return self._task_name

    def get_request(self):
        return self._request

    def get_session(self):
        return self._session

    def get_method(self):
        return self._request.get("method")

    @staticmethod
    def response_to_request(crowd_response, workflow_name, next_task_name):
        request = crowd_response.get_crowd_request().get_request()
        request["method"] = "GET"
        return CrowdRequest(workflow_name, next_task_name, {
            "request": request,
            "session": crowd_response.get_crowd_request().get_session(),
            "prev_response": crowd_response.get_response()
        })

    def __repr__(self):
        return "<CrowdRequest: %s - %s>" % (self.get_task_name(), self.get_method())
