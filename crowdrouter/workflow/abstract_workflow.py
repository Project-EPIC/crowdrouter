from decorators import workflow
from task.abstract_task import AbstractTask
from abc import ABCMeta, abstractmethod, abstractproperty
from crowdrequest import CrowdRequest
from utils import METHOD_POST

#The AbstractWorkFlow class is a template class that consolidates, orders, and executes
#its Tasks in a particular way during runtime. Subclasses will extend this base class
#by implementing the run() method.
class AbstractWorkFlow:
    __metaclass__ = ABCMeta
    _tasks = [] #Must put AbstractTask subclasses inside this list.

    @abstractmethod
    def __init__(self):
        self._tasks = []

    @abstractmethod
    @workflow
    def run(self, task):
        crowd_response = task.execute() #dynamically call execute() for Task based on parameters.
        return crowd_response

    #Use the pipeline function to preserve Task ordering.
    def pipeline(self, task, ordering=_tasks):
        task_order = iter(ordering)
        for current_task in task_order:
            if current_task == task.__class__:
                response = task.execute() #Execute this task as intended.
                #Then, if this task is NOT the last one, then we need to pipe it to the next one.
                if response.get_method() == METHOD_POST and current_task != ordering[-1]:
                    next_task = task_order.next()
                    crowd_request = CrowdRequest.response_to_request(response, self.get_name(), next_task.__name__)
                    next_task = next_task(crowd_request)
                    return next_task.execute()
                else:
                    return response #Not Ready to Pipe yet.
        return NoTaskFoundError()

    def get_name(self):
        return self.__class__.__name__
    def tasks_getter(self):
        return self._tasks
    def tasks_setter(self, task_class):
        self._tasks.append(task_class)
    tasks = property(tasks_getter, tasks_setter)
