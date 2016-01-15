from utils import METHOD_GET

class CrowdRequest:
    _workflow_name = None
    _task_name = None
    _request = None

    def __init__(self, workflow_name, task_name, request):
        self._workflow_name = workflow_name
        self._task_name = task_name
        self._request = request

    def get_workflow_name(self):
        return self._workflow_name

    def get_task_name(self):
        return self._task_name

    def get_request(self):
        return self._request

    def get_method(self):
        return self._request.get("method")

    @staticmethod
    def response_to_request(crowd_response, workflow_name, next_task_name):
        return CrowdRequest(workflow_name, next_task_name, {
            "method": METHOD_GET,
            "prev_response": crowd_response.get_response()
        })

    def __repr__(self):
        return "<CrowdRequest: %s - %s>" % (self.get_task_name(), self.get_method())
