from ..context import CrowdRequest
from ..utils import SESSION_DATA_KEY, SESSION_PIPELINE_KEY, METHOD_POST, METHOD_GET, digest
from ..errors import NoTaskFoundError, PipelineError
from ..task.abstract_crowd_choice import AbstractCrowdChoice
import ipdb

class CrowdPipeline:

    @staticmethod
    def next(pipeline, response):
        index, element = pipeline.next()
        if isinstance(element, AbstractCrowdChoice):
            return index, element.choice(response)
        else:
            return index, element

    @staticmethod
    def get_task_by_pipeline_key(workflow, pipeline_key):
        for index, task in enumerate(workflow.tasks):
            if digest(workflow.get_name(), task.__name__, index) == pipeline_key:
                return task
        raise PipelineError(value="Pipeline Key '%s' not found in the WorkFlow." % pipeline_key)

    @staticmethod
    def loop(crowd_request):
        condition = LoopConditionCrowdChoice(crowd_request)
        response = condition.execute(crowd_request, pipe_data=session[SESSION_DATA_KEY])
        return response

    @staticmethod
    def execute(crowd_request, ordering):
        task = crowd_request.task
        workflow = crowd_request.workflow
        session = crowd_request.get_session()
        if ordering is None:
            ordering = workflow.tasks
        pipeline = enumerate(ordering)

        #Iterate over tasks in pipeline.
        for index, current_task in pipeline:
            if current_task == task.__class__:
                #Grab the Pipeline position SHA1 Digest.
                current_position = session.get(SESSION_PIPELINE_KEY)

                #This is the first time creating state.
                if not current_position:
                    if index != 0: #But index is not the first.
                        raise PipelineError(value="Cannot execute Task %s to start pipeline." % task.get_name())

                    session[SESSION_DATA_KEY] = {}
                    session[SESSION_PIPELINE_KEY] = digest(workflow.get_name(), task.get_name(), index)

                    #First Task: before execution, invoke pre-pipeline logic.
                    workflow.pre_pipeline(task, session[SESSION_DATA_KEY])
                    return task.execute(crowd_request, pipe_data=session[SESSION_DATA_KEY])

                #If the SHA1 Signature matches, execute task as intended.
                if current_position == digest(workflow.get_name(), task.get_name(), index):

                    #Execute Task.
                    response = task.execute(crowd_request, pipe_data=session[SESSION_DATA_KEY])

                    if crowd_request.get_method() == METHOD_POST:
                        if index < len(ordering) - 1: #If task is NOT last, then pipe it to the next one.
                            next_index, next_task = pipeline.next()
                            
                            #Perform step logic.
                            workflow.step_pipeline(next_task, task, response, session[SESSION_DATA_KEY])

                            #Create new CrowdRequest and invoke next task in the pipeline.
                            crowd_request = CrowdRequest.to_crowd_request(response, next_task)
                            next_task = next_task(workflow)

                            session[SESSION_PIPELINE_KEY] = digest(workflow.get_name(), next_task.get_name(), next_index)
                            return next_task.execute(crowd_request, pipe_data=session[SESSION_DATA_KEY]) #Execute Task.

                        else: #Otherwise, we're done!
                            workflow.post_pipeline(task, response, session[SESSION_DATA_KEY]) #Perform post logic.
                            session[SESSION_DATA_KEY] = None
                            session[SESSION_PIPELINE_KEY] = None
                            return response
                    else:
                        return response #We're not ready to pipe yet/We're done pipelining.

        #Execution may flow here when historical session data did not allow new pipeline execution to begin.
        if session[SESSION_DATA_KEY] or session[SESSION_PIPELINE_KEY]:
            session[SESSION_DATA_KEY] = None
            session[SESSION_PIPELINE_KEY] = None
            return CrowdPipeline.execute(crowd_request, ordering) #Re-execute this pipeline with blank pipeline session data.
        else:
            raise NoTaskFoundError(value="No Task found in the pipeline. Please reset your session data and try again.")
