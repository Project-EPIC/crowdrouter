from utils import METHOD_GET
from errors import NoRequestFoundError, NoSessionFoundError, InvalidRequestError, InvalidSessionError
import ipdb

class CrowdRequest(object):
    workflow_name = None
    task_name = None
    session = None
    method = None

    def __init__(self, workflow_name, task_name, request):
        self.workflow_name = workflow_name
        self.task_name = task_name
        self.bind_session(request)
        self.bind_request(request)

    #Hunt down the request object.
    @staticmethod
    def find_request(request):
        if isinstance(request, CrowdRequest):
            return request
        if hasattr(request, "method") and request.method != None:
            return request
        if isinstance(request, dict) and request.has_key("method"):
            return request
        if isinstance(request, dict) and request.has_key("request"):
            return CrowdRequest.find_request(request["request"])
        raise NoRequestFoundError

    #Bind Request parameters to CrowdRequest.
    def bind_request(self, request):
        #If prev_response exists, bind it for client-tracking.
        if isinstance(request, dict) and request.has_key("prev_response"):
            self.prev_response = request["prev_response"]

        request = CrowdRequest.find_request(request)
        #Bind additional request parameters as needed.
        self.bind_request_param(request, "method", required=True)
        self.bind_request_param(request, "data")
        self.bind_request_param(request, "path")
        self.bind_request_param(request, "form")

    def bind_request_param(self, request, param, required=False):
        if param in self.__dict__.keys():
            raise InvalidRequestError
        if hasattr(request, param):
            setattr(self, param, getattr(request, param))
        elif isinstance(request, dict) and request.has_key(param):
            setattr(self, param, request[param])
        else:
            if required:
                raise InvalidRequestError

    #Hunt down the session object.
    @staticmethod
    def find_session(request):
        if hasattr(request, "session") and request.session != None:
            return request.session
        if isinstance(request, dict) and request.has_key("session"):
            return request['session']
        raise NoSessionFoundError

    #Bind the session object to CrowdRequest.
    def bind_session(self, request):
        session = CrowdRequest.find_session(request)
        if hasattr(session, "update") and hasattr(session, "keys"):
            self.session = session
        else:
            raise InvalidSessionError

    @staticmethod
    def to_crowd_request(crowd_response, workflow_name, next_task_name):
        crowd_request = crowd_response.crowd_request
        crowd_request.method = "GET"
        return CrowdRequest(workflow_name, next_task_name, {
            "request": crowd_request,
            "session": crowd_request.session,
            "prev_response": crowd_response.response
        })

    def __repr__(self):
        return "<CrowdRequest: %s - %s>" % (self.task_name, self.method)
