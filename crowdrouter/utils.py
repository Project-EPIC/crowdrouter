from errors import TaskError
import re

METHOD_POST = "POST"
METHOD_GET = "GET"
CR_DEBUG=False

def print_msg(string):
    if CR_DEBUG == True:
        print(string)

def resolve_task_uri(task_uri, crowd_request):
    results = re.findall("<([a-z0-9\.\*\_]+)>", task_uri)
    for result in results:
        if crowd_request.get_data().has_key(result):
            task_uri = task_uri.replace("<%s>" % result, str(crowd_request.get_data()[result]))
        else:
            raise TaskError(value="Task parameter '%s' cannot be found in the CrowdRequest. Please put all needed params inside request.data as expected." % result)
    return task_uri
