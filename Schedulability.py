import matplotlib.pyplot as plt
import argparse
from task_generator import gen_tasks
from LLF_scheduler import scheduler as LLF_scheduler
from aco import scheduler as ACO_scheduler
from random_algorithm import scheduler as random_scheduler
from Task import Task


DEFAULT_N = 50
DEFAULT_SCHEDULE_TIME = 5


def is_feasible(results):
    for entry in results:
        if entry[0] > 2 * entry[1]:
            return False
    return True


def get_schedulability(U, cores, scheduler):
    success = 0
    for _ in range(100):
        print(f"{_}% done...")
        ts = gen_tasks(U, DEFAULT_N, 1, 5)
        tasks = []
        for t in ts:
            tasks.append(Task(t["id"], t["period"], t["exec_time"], t["dependencies"]))
        results = scheduler(tasks, cores, U / cores, DEFAULT_SCHEDULE_TIME, False)
        if is_feasible(results):
            success += 1
    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="schedulability plot", description="This program schedules a set of periodic tasks and displays the QoS plot")
    parser.add_argument("-a", "--algorithm", default="ACO", help="the algorithm used", type=str)
    args = parser.parse_args()
    
    systems = [(0.25, 16), (0.5, 16), (0.3, 32), (0.7, 32)]

    x = []
    y = []
    color = []
    for system in systems:
        print("system 1 started")
        x.append(f"{system[1]} core {system[0]} U")
        if args.algorithm == "LLF":
            current_y = get_schedulability(system[0] * system[1], system[1], LLF_scheduler)
        elif args.algorithm == "ACO":
            current_y = get_schedulability(system[0] * system[1], system[1], ACO_scheduler)
        else:
            current_y = get_schedulability(system[0] * system[1], system[1], random_scheduler)

        y.append(current_y)
        color.append('#185c17' if current_y == 100 else '#17475c' if current_y >= 50 else '#781e1d')
    bars = plt.bar(x, y, color = color)
    plt.bar_label(bars)
    plt.title("Schedulability")
    plt.ylabel("Percentage of Schedulable tasksets")
    plt.show()
