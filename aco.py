import argparse
from Task import Task
from task_generator import gen_tasks, write_tasks
import numpy as np

DEFAULT_MIN_PERIOD = 1
DEFAULT_MAX_PERIOD = 5
DEFAULT_U = 1
DEFAULT_N = 50
DEFAULT_FILE_PATH = "./tasks.csv"
DEFAULT_CORES = 8
DEFAULT_SCHEDULE_TIME = 10

# ACO parameters
alpha = 0
beta = 1
# evaporation rate
rho = 0.3
Q = 1

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


def find_available_instances(released_instances, finished_instances_Id):
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

    return available_instances


def find_potential(Pheromones, pheromine_id, next_task):
    ph = Pheromones[pheromine_id][next_task.pheromine_id]
    d = next_task.deadline - next_task.task.exec_time

    return d**alpha * ph**beta


def select_instances(Pheromones, available_cores, available_instances):
    n = len(available_cores)

    # select cores randomly
    if len(available_instances) < n:
        selected_cores = np.random.choice(available_cores, len(available_instances), replace=False)    
    else:
        selected_cores = np.random.choice(available_cores, n, replace=False)

    next_tasks = []
    for core in selected_cores:
        if len(core.finished_tasks) > 0:
            last_task_ph_id = core.finished_tasks[-1].pheromine_id

            all_moves_probabilities = np.array([find_potential(Pheromones, last_task_ph_id, next_task) for next_task in available_instances])
            all_moves_probabilities = all_moves_probabilities / all_moves_probabilities.sum()
            next_tasks.append((core, np.random.choice(available_instances, p=all_moves_probabilities)))
            available_instances.remove(next_tasks[-1][1])
        # first task
        else:
            next_tasks.append((core, np.random.choice(available_instances)))
            available_instances.remove(next_tasks[-1][1])

    return next_tasks


def L(task):
    '''Cost (lost) of running task 2 after task 1'''

    return task.deadline - task.finish_time if task.deadline > task.finish_time else 0


def release_ant(tasks, Pheromones, n_cores, total_time, u_cores, time_step, want_results=False):

    # [[first instances of all tasks], [second instances of all tasks], ...]
    released_instances = [[task.release(pheromine_id=ph_id) for ph_id, task in enumerate(tasks)]]
    last_pheromine_id = released_instances[-1][-1].pheromine_id

    # [[id of first instances of all tasks (task.id)], [second instances of all tasks], ...]
    finished_instances = [[] for _ in range(len(tasks))]

    cores = [Core() for _ in range(n_cores)]
    
    time = 0
    while time < total_time:
        available_cores = []
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

                    core.running_task.pretask = core.finished_tasks[-2] if len(core.finished_tasks)>=2 else None
                    available_cores.append(core)
            else:
                available_cores.append(core)
        
        # selecting new instances to run
        available_instances = find_available_instances(released_instances, finished_instances)
        next_tasks = select_instances(Pheromones, available_cores, available_instances)

        for core, task in next_tasks:
            core.running_task = task
            core.available = False
            task.is_running = True
            task.finish_time = time + task.task.exec_time/u_cores

        # releasing new instances
        for task in tasks:
            if task.next_release <= time:
                # checking if new generation of inctances have to be created
                if len(released_instances) <= task.count:
                    released_instances.append([])
                released_instances[task.count].append(task.release(last_pheromine_id))
                last_pheromine_id += 1

        time += time_step
    
    if want_results:
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

    else:
        return cores

def scheduler(tasks, n_cores, u_cores, total_time, verbose=False):
    # initial values
    initial_Pheromone = 0.2

    # how many times ACO algorithm runs
    iterations = 2
    ants = 2

    time_step = 0.001

    # [number of all instances of task 1, number of all instances of task 2, ...]
    all_task_instances_will_be_released = [total_time // task.period + 1 for task in tasks]
    count_all_instances = int(sum(all_task_instances_will_be_released))
    Pheromones = np.ones((count_all_instances, count_all_instances))*initial_Pheromone

    results = []
    for iteration in range(iterations):
        cores_data_after_iteration = []

        for ant in range(ants):
            # reset tasks
            for task in tasks:
                task.reset()

            cores = release_ant(tasks, Pheromones, n_cores, total_time, u_cores, time_step)
            
            cores_data_after_iteration.append(cores)
            
        for cores_of_an_ant in cores_data_after_iteration:
            for core in cores_of_an_ant:
                # calculating delta pheromenie
                l = 0
                for task in core.finished_tasks:
                    if not task.finished:
                        task.finish_time = task.deadline * 10

                    l += L(task)
                
                # updating the phromines
                for task in core.finished_tasks:
                    if task.pretask:
                        Pheromones[task.pretask.pheromine_id][task.pheromine_id] += Q*l
           
    for task in tasks:
        task.reset()
    results = release_ant(tasks, Pheromones, n_cores, total_time, u_cores, time_step, want_results=True)
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
