import ipdb, pickledb

class CrowdStats:
    #Crowd Statistics
    task_counts = None
    db_path = None

    def __init__(self, db_path, workflow_classes):
        self.db_path = db_path
        db = pickledb.load(self.db_path, True)
        self.task_counts = db.db.get("task_counts") or {}

        #Base Case when choosing to enable Crowd Statistics.
        for workflow_class in workflow_classes:
            if not self.task_counts.get(workflow_class.__name__):
                self.task_counts[workflow_class.__name__] = {task.__name__: {"GET":0, "POST":0} for task in workflow_class.tasks}

    #Update task execution counts for the specified Workflow and Task.
    def update(self, workflow, crowd_response):
        task_name = crowd_response.task.get_name()
        workflow_name = workflow.get_name()
        db = pickledb.load(self.db_path, True)

        #Base case - initialize any extra workflow keys in task_counts.
        if not self.task_counts.get(workflow_name):
            self.task_counts[workflow_name] = {task.__name__: {"GET":0, "POST":0} for task in workflow.tasks}

        #Task Counts
        method = crowd_response.crowd_request.get_method()
        self.task_counts[workflow_name][task_name][method] += 1

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
