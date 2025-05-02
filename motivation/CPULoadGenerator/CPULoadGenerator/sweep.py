import os
import time
from datetime import datetime

load_script_path = "CPULoadGenerator.py"
idle_script_path = "cpupower idle-set"
freq_script_path = "cpupower frequency-set"
uncore0_path = "/sys/devices/system/cpu/intel_uncore_frequency/package_00_die_00"
uncore1_path = "/sys/devices/system/cpu/intel_uncore_frequency/package_01_die_00"

tested_loads = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
num_cpus = os.cpu_count()
execute = True
duration = 300 if execute else 0
reset_duration = 300 if execute else 0

def exec_cmd(cmd, execute):
    if execute:
        print(f"At {datetime.now()}, starting: {cmd}")
        ret = os.system(cmd)
        if ret != 0:
            print(f"At {time.time()}, crashed: {cmd}")
            raise ValueError("Command ot successfully executed")
    else:
        print(cmd)

def reset():
    cmd1 = "cpupower frequency-set -f 2000000"
    exec_cmd(cmd1, execute)

    cmd2 = "cpupower idle-set -D 1"
    exec_cmd(cmd2, execute)

    cmd = f"echo 2400000 >> {uncore0_path}/max_freq_khz"
    exec_cmd(cmd, execute)

    cmd = f"echo 2400000 >> {uncore0_path}/min_freq_khz"
    exec_cmd(cmd, execute)

    cmd = f"echo 2400000 >> {uncore1_path}/max_freq_khz"
    exec_cmd(cmd, execute)

    cmd = f"echo 2400000 >> {uncore1_path}/min_freq_khz"
    exec_cmd(cmd, execute)
    
    time.sleep(reset_duration)

def set_uncores_lowest_freq():
    cmd = f"echo 800000 >> {uncore0_path}/max_freq_khz"
    exec_cmd(cmd, execute)

    cmd = f"echo 800000 >> {uncore0_path}/min_freq_khz"
    exec_cmd(cmd, execute)

    cmd = f"echo 800000 >> {uncore1_path}/max_freq_khz"
    exec_cmd(cmd, execute)

    cmd = f"echo 800000 >> {uncore1_path}/min_freq_khz"
    exec_cmd(cmd, execute)

    time.sleep(reset_duration)


def set_all_cores_to_lowest_freq():
    cmd1 = "cpupower frequency-set -f 800000"
    exec_cmd(cmd1, execute)
    time.sleep(duration)


def allow_highest_c_states():
    cmd1 = "cpupower idle-set -E"
    exec_cmd(cmd1, execute)
    time.sleep(duration)


def add_load(load):
    if load == 0:
        time.sleep(duration)
    else:
        cmd = f"python {load_script_path} -l {load} -d {duration}"
        exec_cmd(cmd, execute)

def add_load_baseline():
    reset()
    for l in tested_loads:
        add_load(l)

def add_load_lowest_core_freq():
    reset()
    set_all_cores_to_lowest_freq()
    for l in tested_loads:
        add_load(l)


def add_load_highest_c_states():
    reset()
    allow_highest_c_states()
    for l in tested_loads:
        add_load(l)


def add_load_lowest_uncore_freq():
    reset()
    set_uncores_lowest_freq()
    for l in tested_loads:
        add_load(l)

def composite():
    reset()
    set_all_cores_to_lowest_freq()
    allow_highest_c_states()
    set_uncores_lowest_freq()
    print(f"At {datetime.now()}, starting: load")
    for l in tested_loads:
        add_load(l)

def main():
    print(f"At {datetime.now()}, starting: exp1")
    add_load_baseline()

    print(f"At {datetime.now()}, starting: exp2")
    add_load_lowest_core_freq()

    print(f"At {datetime.now()}, starting: exp3")
    add_load_highest_c_states()

    print(f"At {datetime.now()}, starting: exp4")
    add_load_lowest_uncore_freq()


if __name__ == "__main__":
    reset()
