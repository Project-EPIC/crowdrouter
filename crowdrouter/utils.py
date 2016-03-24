from errors import TaskError, NoTaskFoundError, NoWorkFlowFoundError
import re, hashlib

SESSION_PIPELINE_KEY = "cr_pipe"
SESSION_DATA_KEY = "cr_data"
METHOD_POST = "POST"
METHOD_GET = "GET"
CR_DEBUG=False

def print_msg(string):
    if CR_DEBUG == True:
        print(string)

def digest(workflow_name, task_name, index):
    return hashlib.sha1(workflow_name + task_name + str(index)).hexdigest()

def realize_workflow(workflow_class, crowdrouter):
    try: #1) workflow_class is a class object, 2) workflow_class is a string.
        from workflow.abstract_workflow import AbstractWorkFlow
        workflows = {workflow.__name__:workflow for workflow in crowdrouter.workflows}
        if workflow_class in crowdrouter.workflows and issubclass(workflow_class, AbstractWorkFlow):
            workflow = workflow_class(crowdrouter)
        else:
            workflow = workflows.get(workflow_class)(crowdrouter)
        if workflow == None:
            raise NoWorkFlowFoundError
        else:
            return workflow
    except:
        raise NoWorkFlowFoundError(value="WorkFlow %s not found. Ensure that the underlying CrowdRouter class has declared this WorkFlow." % workflow_class)


def realize_task(task_class, workflow):
    try:
        #1) task is class object, 2) task is string name, 3) no task.
        from task.abstract_task import AbstractTask
        tasks = {task.__name__:task for task in workflow.tasks}

        if task_class in workflow.tasks:
            task = task_class(workflow) #Class case.
        elif task_class != None:
            task = tasks.get(task_class)(workflow) #String case.
        else:
            task = workflow.tasks[0](workflow) #Null Case - choose the first Task.

        if task == None: #Type Checking for the Task instance.
            raise NoTaskFoundError
        else:
            return task
    except:
        raise NoTaskFoundError(value="Task %s not found. Ensure that the underlying Workflow class has declared this Task." % task_class)
