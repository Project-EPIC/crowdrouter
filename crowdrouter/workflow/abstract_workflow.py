from abc import ABCMeta, abstractmethod, abstractproperty
from ..task.abstract_task import AbstractTask
from ..crowdrequest import CrowdRequest
from ..decorators import workflow
from ..utils import METHOD_POST
import hashlib, ipdb

#The AbstractWorkFlow class is a template class that consolidates, orders, and executes
#its Tasks in a particular way during runtime. Subclasses will extend this base class
#by implementing the run() method.
class AbstractWorkFlow:
    __metaclass__ = ABCMeta
    tasks = [] #Must put AbstractTask subclasses inside this list.

    @abstractmethod
    def __init__(self):
        self.tasks = []

    @abstractmethod
    @workflow
    def run(self, task):
        crowd_response = task.execute() #dynamically call execute() for Task based on parameters.
        return crowd_response

    def repeat(self, task, count):
        ordering = [task.__class__ for x in xrange(count)]
        return self.pipeline(task, ordering=ordering)

    #Use the pipeline function to preserve Task ordering.
    def pipeline(self, task, ordering=tasks):
        task_order = enumerate(ordering)
        crowd_request = task.crowd_request
        session = crowd_request.session

        #Iterate over tasks in ordering list.
        for index, current_task in task_order:
            if current_task == task.__class__:
                current_position = session.get("cr_current")

                #This is the first time creating state.
                if not current_position:
                    session["cr_current"] = self.digest(task, index)
                    return task.execute()

                if current_position == self.digest(task, index):
                    response = task.execute() #Execute this task as intended.

                    #Then, if this task is NOT the last one, then we need to pipe it to the next one.
                    if crowd_request.method == METHOD_POST and index < len(ordering) - 1:
                        next_index, next_task = task_order.next()
                        crowd_request = CrowdRequest.to_crowd_request(response, self.get_name(), next_task.__name__)
                        next_task = next_task(crowd_request)
                        session["cr_current"] = self.digest(next_task, next_index)
                        return next_task.execute()
                    else:
                        return response #Not Ready to Pipe yet.
        return NoTaskFoundError

    def digest(self, task, index):
        return hashlib.sha1(self.get_name() + task.get_name() + str(index)).hexdigest()

    def get_name(self):
        return self.__class__.__name__
