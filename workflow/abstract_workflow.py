from decorators import workflow
from task.abstract_task import AbstractTask
from abc import ABCMeta, abstractmethod, abstractproperty

#The AbstractWorkFlow class is a template class that consolidates, orders, and executes
#its Tasks in a particular way during runtime. Subclasses will extend this base class
#by implementing the run() method.
class AbstractWorkFlow:
    __metaclass__ = ABCMeta
    _tasks = [] #Must put AbstractTask subclass names inside this list.

    @abstractmethod
    @workflow
    def run(self, crowd_request):
        #1)Want to convert crowd request to Task based on parameters.
        task = AbstractTask(crowd_request)
        #2)Then, dynamically call execute() for Task based on parameters.
        crowd_response = task.execute()
        return crowd_response

    def run_task(self, task):
        if issubclass(task, AbstractTask) == False:
            raise TypeError("input argument '%s' is not of type Task." % task)
        task.execute()

    def tasks_getter(self):
        return self._task_counts
    def tasks_setter(self, task_name):
        self._tasks.append(task_name)

    tasks = property(tasks_getter, tasks_setter)
