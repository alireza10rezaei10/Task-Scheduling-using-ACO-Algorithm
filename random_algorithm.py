import argparse
from Task import Task
from task_generator import gen_tasks, write_tasks
import numpy as np

DEFAULT_MIN_PERIOD = 1
DEFAULT_MAX_PERIOD = 5
DEFAULT_U = 1
DEFAULT_N = 500
DEFAULT_FILE_PATH = "./tasks.csv"
DEFAULT_CORES = 8
DEFAULT_SCHEDULE_TIME = 40


class Core:
    def __init__(self) -> None:
        self.available = True
        self.running_task = None
        # index of that instance in the list of all_instances
        self.finished_tasks = []


def create_tasks(U, n, minp, maxp, path):
    ts = gen_tasks(U, n, minp, maxp)
    write_tasks(path, ts)
    tasks = []
    for t in ts:
        tasks.append(Task(t["id"], t["period"], t["exec_time"], t["dependencies"]))
    return tasks


def select_instances(released_instances, finished_instances_Id, n):
    available_instances = []
    for index, instances in enumerate(released_instances):
        for task in instances:
            if task.is_running:
                continue
            # check the dependencies
            else:
                for dep in task.task.dependencies:
                    if dep not in finished_instances_Id[index]:
                        continue
        
            available_instances.append(task)

    if len(available_instances) >= n:
            return np.random.choice(available_instances, n, replace=False)  
    else:
        return available_instances


'''
    [
        [T1, T6, ...], # first instances
        [T1, T7, ...], # second instances
        [], # , ...
    ]
'''




def scheduler(tasks, n_cores, u_cores, total_time, verbose=False):
    # initial values
    initial_Pheromone = 0.2
    alpha = 1
    beta = 1
    e_rate = 0.7

    time = 0
    time_step = 0.001

    # [number of all instances of task 1, number of all instances of task 2, ...]
    all_task_instances_will_be_released = [total_time // task.period for task in tasks]
    count_all_instances = int(sum(all_task_instances_will_be_released))
    Pheromones = np.ones((count_all_instances, count_all_instances))*initial_Pheromone

    # [[first instances of all tasks], [second instances of all tasks], ...]
    released_instances = [[task.release(pheromine_id=ph_id) for ph_id, task in enumerate(tasks)]]
    last_pheromine_id = released_instances[-1][-1].pheromine_id

    # [[id of first instances of all tasks (task.id)], [second instances of all tasks], ...]
    finished_instances = [[] for _ in range(len(tasks))]

    
    cores = [Core() for _ in range(n_cores)]

    while time < total_time:
        count_available_cores = 0
        for core in cores:
            # means core is running sth...
            if not core.available:
                if core.running_task.finish_time <= time:
                    core.finished_tasks.append(core.running_task)
                    core.available = True

                    finished_instances[core.running_task.id].append(
                        core.running_task.task.id
                    )
                    released_instances[core.running_task.id].remove(core.running_task)
                    core.running_task.finished = True
                    core.running_task.finish_time = time

                    count_available_cores += 1
            else:
                count_available_cores += 1
        
        selected_instances = select_instances(released_instances, finished_instances, count_available_cores)
        selected_cores = np.random.choice(cores, len(selected_instances), replace=False)

        for i in range(len(selected_instances)):
            selected_cores[i].running_task = selected_instances[i]
            selected_cores[i].available = False
            selected_instances[i].is_running = True
            selected_instances[i].finish_time = time + selected_instances[i].task.exec_time/u_cores

        # releasing new instances
        for task in tasks:
            if task.next_release <= time:
                # checking if new generation of inctances have to be created
                if len(released_instances) <= task.count:
                    released_instances.append([])
                released_instances[task.count].append(task.release(last_pheromine_id))
                last_pheromine_id += 1

        time += time_step

    results = []
    for core in cores:
        for task in core.finished_tasks:
            if not task.finished:
                task.finish_time = task.deadline * 100
            results.append((
                task.finish_time,
                task.deadline
            ))
    results = sorted(results, key= lambda arr: arr[0])

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="LLF Scheduler", description="This program creates a set of periodic tasks and schedules the according to the LLF algorithm")
    parser.add_argument("-u", "--utilization", default=DEFAULT_U, help="the sum of utilization of tasks", type=float)
    parser.add_argument("-n", "--numberoftasks", default=DEFAULT_N, help="the number of tasks to generate", type=int)
    parser.add_argument("-min", "--minperiod", default=DEFAULT_MIN_PERIOD, help="minimum period for periodic tasks", type=float)
    parser.add_argument("-max", "--maxperiod", default=DEFAULT_MAX_PERIOD, help="maximum period for periodic tasks", type=float)
    parser.add_argument("-p", "--filepath", default=DEFAULT_FILE_PATH, help="path to the csv file to store the tasks in")
    parser.add_argument("-c", "--cores", default=DEFAULT_CORES, help="number of cores to schedule on", type=int)
    parser.add_argument("-t", "--time", default=DEFAULT_SCHEDULE_TIME, help="the duration of the simulation", type=int)
    # parser.add_argument("-v", "--verbose", action="store_true", help="if set, prints every step of the schedule to output")
    args = parser.parse_args()

    tasks = create_tasks(args.utilization, args.numberoftasks, args.minperiod, args.maxperiod, args.filepath)
    scheduler(tasks, args.cores, args.utilization / args.cores, args.time)#, args.verbose)
