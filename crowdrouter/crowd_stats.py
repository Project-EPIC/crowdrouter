import ipdb, pickledb

class CrowdStats:
    #Crowd Statistics
    task_counts = None
    db_path = None

    def __init__(self, db_path, workflow_classes):
        self.db_path = db_path
        db = pickledb.load(self.db_path, True)
        self.refresh_stats(db, workflow_classes)

    def refresh_stats(self, db, workflow_classes, task_class=None):
        # import ipdb; ipdb.set_trace()
        stats = db.db
        try:
            task_counts = stats.get("task_counts") or {}
        except:
            task_counts = {}

        #Base Case when choosing to enable Crowd Statistics.
        from task.abstract_crowd_choice import AbstractCrowdChoice
        for workflow_class in workflow_classes:
            if not task_counts.get(workflow_class.__name__):
                workflow_key = task_counts[workflow_class.__name__] = {} #Add WorkFlow here.
                for task in workflow_class.tasks:
                    if issubclass(task, AbstractCrowdChoice):
                        workflow_key[task.t1.__name__] = {"GET": 0, "POST":0}
                        workflow_key[task.t2.__name__] = {"GET": 0, "POST":0}
                    else:
                        workflow_key[task.__name__] = {"GET": 0, "POST":0}

            #If we have a task class and we DO NOT yet have this task as a key in this workflow...
            elif task_class and not task_counts[workflow_class.__name__].get(task_class.__name__):
                task_counts[workflow_class.__name__][task_class.__name__] = {"GET": 0, "POST":0}

        self.task_counts = task_counts
        db.dump()


    #Update task execution counts for the specified Workflow and Task.
    def update(self, crowd_response):
        task = crowd_response.task
        workflow = task.workflow
        crowdrouter = workflow.crowdrouter
        db = pickledb.load(self.db_path, True)
        # import ipdb; ipdb.set_trace()

        #Base case - initialize any extra task keys in task_counts.
        self.refresh_stats(db, crowdrouter.workflows, task.__class__)

        #Task Counts
        method = crowd_response.crowd_request.get_method()
        self.task_counts[workflow.get_name()][task.get_name()][method] += 1

        #DB set and save.
        db.db["task_counts"] = self.task_counts
        db.dump()


    #Creates report to render on web page.
    def report(self):
        db = pickledb.load(self.db_path, True)
        return db.db

    def clear(self):
        db = pickledb.load(self.db_path, True)
        self.task_counts = self.task_visits = {}
        db.deldb()
