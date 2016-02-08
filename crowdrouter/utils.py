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
    data = crowd_request.get_data()
    for result in results:
        if data.has_key(result):
            task_uri = task_uri.replace("<%s>" % result, str(data[result]))
        elif data.has_key("data") and isinstance(data["data"], dict) and data["data"].has_key(result): #Uncommon, but possible.
            task_uri = task_uri.replace("<%s>" % result, str(data["data"][result]))
        else:
            raise TaskError(value="Task parameter '%s' cannot be found in the CrowdRequest. Please put all needed params inside request.data as expected." % result)
    return task_uri
