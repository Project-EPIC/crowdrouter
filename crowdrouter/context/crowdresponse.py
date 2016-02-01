from ..errors import ImproperResponseError
import ipdb

class CrowdResponse(object):
    crowd_request = None
    status = None
    task = None
    response = None
    path = None

    def __init__(self, response, task):
        try:
            self.task = task
            self.crowd_request = task.crowd_request
            self.response = response
            self.status = response["status"]
            self.path = response["path"]
        except:
            raise ImproperResponseError(value="Required parameter not found. Ensure that CrowdResponse contains both 'status' and 'path'.")

    def __repr__(self):
        return "<CrowdResponse: %s-%s-%s>" % (self.task.get_name(), self.crowd_request.get_method(), self.status)
