from ..errors import ImproperResponseError
import ipdb

class CrowdResponse(object):
    crowd_request = None
    method = None
    status = None
    task = None
    response = None
    path = None

    def __init__(self, response, crowd_request, task):
        try:
            self.task = task
            self.crowd_request = crowd_request
            self.method = crowd_request.get_method()
            self.response = response
            self.status = response.get("status")
            self.path = response.get("path")
        except:
            raise ImproperResponseError(value="Invalid Response.")

    def __repr__(self):
        return "<CrowdResponse: %s-%s-%s>" % (self.task.get_name(), self.crowd_request.get_method(), self.status)
