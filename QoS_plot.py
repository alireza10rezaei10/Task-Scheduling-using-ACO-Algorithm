import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import argparse
from aco import create_tasks
from LLF_scheduler import scheduler as LLF_scheduler
from aco import scheduler as ACO_scheduler
matplotlib.rc('axes.formatter', useoffset=False)


DEFAULT_MIN_PERIOD = 1
DEFAULT_MAX_PERIOD = 5
DEFAULT_U = 0.3
DEFAULT_N = 50
DEFAULT_FILE_PATH = "./tasks.csv"
DEFAULT_CORES = 32
DEFAULT_SCHEDULE_TIME = 40


def utility_function(f_i, D_i, x=2):
    if f_i <= D_i:
        return 1
    elif D_i < f_i <= x * D_i:
        return (D_i - f_i) / (D_i * (x - 1)) + 1
    else:
        return 0


def compute_qos_over_time(results):
    n = len(results)
    time_points = []
    qos_values = []
    sum = 0

    for i in range(n):
        sum += utility_function(results[i][0], results[i][1])
        qos_values.append(sum / (i+1))
        time_points.append(results[i][0])

    return time_points, qos_values


def plot_qos(time_points, qos_values, title):
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, qos_values, marker='o')
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel('QoS')
    plt.grid(True)
    plt.show()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="QoS plot", description="This program schedules a set of periodic tasks and displays the QoS plot")
    parser.add_argument("-u", "--utilization", default=DEFAULT_U, help="the sum of utilization of tasks", type=float)
    parser.add_argument("-n", "--numberoftasks", default=DEFAULT_N, help="the number of tasks to generate", type=int)
    parser.add_argument("-min", "--minperiod", default=DEFAULT_MIN_PERIOD, help="minimum period for periodic tasks", type=float)
    parser.add_argument("-max", "--maxperiod", default=DEFAULT_MAX_PERIOD, help="maximum period for periodic tasks", type=float)
    parser.add_argument("-p", "--filepath", default=DEFAULT_FILE_PATH, help="path to the csv file to store the tasks in")
    parser.add_argument("-c", "--cores", default=DEFAULT_CORES, help="number of cores to schedule on", type=int)
    parser.add_argument("-t", "--time", default=DEFAULT_SCHEDULE_TIME, help="the duration of the simulation", type=int)
    parser.add_argument("-a", "--algorithm", default="ACO", help="the algorithm used", type=str)
    args = parser.parse_args()

    for utilization, cores in [(0.25, 16), (0.5, 16), (0.3, 32), (0.7, 32)]:
        tasks = create_tasks(utilization, args.numberoftasks, args.minperiod, args.maxperiod, args.filepath)
        if args.algorithm == "LLF":
            results = LLF_scheduler(tasks, cores, utilization / cores, args.time, False)
        else:
            results = ACO_scheduler(tasks, cores, utilization / cores, args.time, False)
        
        time_points, qos_values = compute_qos_over_time(results)
        
        plot_qos(time_points, qos_values, f"QoS Over Time ({cores} core, {utilization} U)")
    # plot_qos(time_points, qos_values, f"QoS Over Time ({args.cores} core, {args.utilization/args.cores} U)")