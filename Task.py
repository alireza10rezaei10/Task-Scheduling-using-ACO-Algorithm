class Task_Instance:
    def __init__(self, task, pheromine_id):
        self.task = task
        self.id = task.count
        task.count += 1
        self.deadline = task.next_release
        self.remaining_time = task.exec_time

        # attributes below used in aco algorithm
        self.finish_time = task.exec_time
        self.pheromine_id = pheromine_id
        self.is_running = False
        self.finished = False
        # previous task
        self.pretask = None

    def __lt__(self, other):
        return self.id < other.id

    def get_laxity(self, time):
        return round(self.deadline - self.remaining_time - time, 6)
    
    def get_utilization(self):
        return self.remaining_time / self.task.period
    




class Task:
    def __init__(self, id, period, exec_time, dependencies):
        self.id = id
        self.period = period
        self.exec_time = exec_time
        self.dependencies = dependencies
        self.next_release = 0
        self.count = 0

    def __lt__(self, other):
        return self.id < other.id
    
    def release(self, pheromine_id=0):
        self.next_release = round(self.next_release + self.period, 6)
        new_instance = Task_Instance(self, pheromine_id)
        return new_instance
    
    def reset(self):
        self.next_release = 0
        self.count = 0
    