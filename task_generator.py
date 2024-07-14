import random
import argparse
import csv
import numpy as np

DEFAULT_MIN_PERIOD = 1
DEFAULT_MAX_PERIOD = 5
DEFAULT_U = 1
DEFAULT_N = 50
DEFAULT_FILE_PATH = "./tasks.csv"


def UUniFast(U, n):
    utilizations = []
    sumU = round(U, 4)
    i = 0
    while len(utilizations) < n - 1:
        nextSumU = round(sumU * random.random() ** (1.0 / (n - i)), 4)
        nextU = sumU - nextSumU
        if nextU > 1:
            continue
        utilizations.append(nextU)
        i = i + 1
        sumU = nextSumU
    if sumU <= 1:
        utilizations.append(sumU)
    else:
        utilizations = UUniFast(U, n)
    return utilizations


def gen_tasks(U, n, minp, maxp):
    utilizations = UUniFast(U, n)
    tasks = []
    for (i, utilization )in enumerate(utilizations):
        period = random.randint(minp, maxp)
        exec_time = period * utilization
        dependencies = [] if i == 0 else ([i - j for j in range(1, 5)] if i % 5 == 0 else [int(i/5)*5])

        tasks.append({"id": i, "utilization": utilization, "period": period, "exec_time": exec_time, "dependencies": dependencies})
    return tasks


def write_tasks(path, tasks):
    with open(path, "w", newline='') as file:
        writer = csv.DictWriter(file, fieldnames = tasks[0].keys())
        writer.writeheader()
        writer.writerows(tasks)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = "Task Generator", description="This program creates a set of periodic tasks using the UUniFast algorithm")
    parser.add_argument("-u", "--utilization", default=DEFAULT_U, help="the sum of utilization of tasks", type=float)
    parser.add_argument("-n", "--numberoftasks", default=DEFAULT_N, help="the number of tasks to generate", type=int)
    parser.add_argument("-min", "--minperiod", default=DEFAULT_MIN_PERIOD, help="minimum period for periodic tasks", type=float)
    parser.add_argument("-max", "--maxperiod", default=DEFAULT_MAX_PERIOD, help="maximum period for periodic tasks", type=float)
    parser.add_argument("-p", "--filepath", default=DEFAULT_FILE_PATH, help="path to the csv file to store the tasks in")
    args = parser.parse_args()

    tasks = gen_tasks(args.utilization, args.numberoftasks, args.minperiod, args.maxperiod)
    write_tasks(args.filepath, tasks)