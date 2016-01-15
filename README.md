# crowdrouter
Tired of having messy crowdsourcing code? Ever thought about swapping in a new task or workflow for an old one but felt reluctant about how much refactoring that would cause? Ever wish you could separate crowdsourcing from your app in general?

Enter the **crowdrouter**, a developer framework for architecting tasks to the crowd. Plug it in to your favorite Python web framework and go. Implement crowd workflows and tasks as first-class objects, and then route them using the CrowdRouter object. Create task pipelines that connect tasks together to provide a fluid tasking environment. 

Basically, the crowdrouter is designed to get you thinking about crowdsourcing as a module rather than spaghetti code.

## How it works

There are three components: 

**CrowdRouter**: guards and passes client requests, keeping track of crowd statistics such as number of allowable requests, whitelists and blacklists to check against, task counts, and more. Your own CrowdRouter instance defines which WorkFlow instances it can pass requests to. 

**WorkFlow**: handles the template for how crowdwork is performed. For example, Task A needs to always happen before Task B. Task C can be executed by anyone, anytime. Task D, however, requires authentication. Multiple WorkFlows instances means that your web application needs coordinated crowdsourcing for various use cases.

**Task**: encapsulates a unit of crowdwork. Each Task instance defines a request and response action, mirroring the HTTP GET and POST requests on the web. Use a Task to define what template to serve back to the client, data to validate or create via a database call, or remote API to call. Your crowdwork belongs inside Tasks.

Here's a simple CrowdRouter:

```
class TestCrowdRouter(AbstractCrowdRouter):
	def __init__(self):
		self._workflows = [] #Put in workflow classes here.
		self._task_counts = {} #Initialize as-is to keep track of task counts.
		
	@crowdrouter
	def route(self, crowd_request, workflow):
		crowd_response = workflow.run(crowd_request)
		self.update_task_count(workflow, crowd_response.get_task().get_name())
		return crowd_response

```

Here's a simple WorkFlow that accepts any request.

```
class TestWorkFlow(AbstractWorkFlow):
	def __init__(self):
		_tasks = [TestTask1, TestTask2] #Put Task classes here.
	
	@workflow
	def run(self, task):
		return task.execute(args, kwargs)

```

And here's TestTask1:

```
class TestTask1(AbstractTask):
	def __init__(self, crowd_request):
		super(TestTask1, self).__init__(crowd_request)
		
	@task
	def exec_request(self):
		return {"status": "OK", "msg": "TEST [GET]"}
		
	@task
	def exec_response(self):
		return {"status": "OK", "msg": "TEST [POST]"}
		

```

That's it! Just globally initialize `crowdrouter = TestCrowdRouter()` and you're good to go. Try putting your CrowdRouter instance in various controller actions and re-organize those actions into Task instances:

```
def report(request):
	...
	crowdrouter.route(request, "TestWorkFlow", "TestTask1")
	...
	
```

The crowdrouter will do the work in converting these arguments into a CrowdRequest that will get properly routed to the specified Task in the specified WorkFlow. 


##Questions?
Email me at mario dot barrenechea at colorado dot edu.