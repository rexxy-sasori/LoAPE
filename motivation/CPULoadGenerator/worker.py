import time
import os
import numpy as np

CPU_COUNT = os.cpu_count()
DURATION_SECS = 60 * 24 * 3600 # run for 72 hours
SECS_IN_ONE_DAY = 24 * 3600
script_path = "python /CPULoadGenerator/CPULoadGenerator.py"
EXECUTE_CMD = True

def exec_cmd(cmd, execute):
    if execute:
        ret = os.system(cmd)
        if ret != 0:
            print(f"At {time.time()}, crashed: {cmd}")
            raise ValueError("Command ot successfully executed")

def complete_random_walk(
        cpu_core_ranges, utilization_ranges,
        current_num_core_idx, current_util_idx,
        iteration_idx
):
    util_idx = np.random.randint(len(utilization_ranges))
    util = utilization_ranges[util_idx]

    cpu_core_idx = np.random.randint(len(cpu_core_ranges))
    num_cores = cpu_core_ranges[cpu_core_idx]

    duration = 10 * 60

    core_args = ""
    for core_id in range(num_cores):
        core_args += f"-c {int(core_id)} "

    util_args = f"-l {util}"
    cmd = f"{script_path} -f 0 {util_args} {core_args} -d {duration}"
    ret = exec_cmd(cmd, EXECUTE_CMD)

    return cpu_core_idx, util_idx


def periodic_walk(
        cpu_core_ranges, utilization_ranges,
        current_num_core_idx, current_util_idx,
        iteration_idx
):
    cpu_option_length = len(cpu_core_ranges)
    util_option_length = len(utilization_ranges)

    if int(iteration_idx/cpu_option_length) % 2 == 0:
        next_core_idx = (current_num_core_idx + 1) % len(cpu_core_ranges)
    else:
        next_core_idx = (current_num_core_idx - 1) % len(cpu_core_ranges)

    if int(iteration_idx / util_option_length) % 2 == 0:
        next_util_idx = (current_util_idx + 1) % len(utilization_ranges)
    else:
        next_util_idx = (current_util_idx - 1) % len(utilization_ranges)

    num_cores = cpu_core_ranges[next_core_idx]
    util = utilization_ranges[next_util_idx]
    
    #duration_list = [60 * 2, 60 * 4]
    
    #duration = duration_list[np.random.randint(len(duration_list))]
    
    duration = 60 * 2

    core_args = ""
    for core_id in range(num_cores):
        core_args += f"-c {int(core_id)} "

    util_args = f"-l {util}"
    cmd = f"{script_path} -f 0 {util_args} {core_args} -d {duration}"
    ret = exec_cmd(cmd, EXECUTE_CMD)
    return next_core_idx, next_util_idx
    
    
def time_correlated_walk(
        cpu_core_ranges, utilization_ranges,
        current_num_core_idx, current_util_idx,
        iteration_idx
):
    direction_options = [1, -1]
    core_direction = direction_options[np.random.randint(len(direction_options))]
    util_direction = direction_options[np.random.randint(len(direction_options))]

    next_core_idx = (current_num_core_idx + core_direction) % len(cpu_core_ranges)
    next_util_idx = (current_util_idx + core_direction) % len(utilization_ranges)

    if iteration_idx % 500 == 0:
        next_core_idx = np.random.randint(len(cpu_core_ranges))
        next_util_idx = np.random.randint(len(utilization_ranges))

    num_cores = cpu_core_ranges[next_core_idx]
    util = utilization_ranges[next_util_idx]

    duration = 2 * 60

    core_args = ""
    for core_id in range(num_cores):
        core_args += f"-c {int(core_id)} "

    util_args = f"-l {util}"

    cmd = f"{script_path} -f 0 {util_args} {core_args} -d {duration}"
    ret = exec_cmd(cmd, EXECUTE_CMD)
    return next_core_idx, next_util_idx


func_maps = [
    complete_random_walk,
    periodic_walk,
    time_correlated_walk
]

if __name__ == "__main__":
    cpu_core_ranges = np.linspace(2, CPU_COUNT, 10).astype(np.int32)
    utilization_ranges = np.linspace(0.05, 0.9, 10)

    start = time.time()

    iteration_idx = 0

    current_num_core_idx = 0
    current_util_idx = 0

    current = time.time() 
    while (current - start) < DURATION_SECS:
        if int(current - start) % SECS_IN_ONE_DAY == 0:
            mode = np.random.randint(len(func_maps))
            func = func_maps[mode]
            time.sleep(1)

        #func = func_maps[mode]

        ret = func(cpu_core_ranges, utilization_ranges, current_num_core_idx, current_util_idx, iteration_idx)

        current_num_core_idx, current_util_idx = ret
        iteration_idx += 1
        current = time.time()


