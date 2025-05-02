import os
import subprocess
import time

# Function to set uncore frequency
def set_uncore_frequency(uncore_freq, dry_run=False):
    print(f"Setting uncore frequency to {uncore_freq} kHz...")

    if dry_run:
        print("[Dry Run] Skipping actual uncore frequency setting.")
        return True

    # Find all package frequency directories
    package_dirs = []
    for root, dirs, files in os.walk("/sys/devices/system/cpu/intel_uncore_frequency/"):
        package_dirs.extend([os.path.join(root, d) for d in dirs if d.startswith("package_")])

    if not package_dirs:
        print("No package frequency directories found. Exiting...")
        return False

    # Write to max_freq_khz and min_freq_khz for each package directory
    for dir in package_dirs:
        print(f"Writing to {dir}/max_freq_khz and {dir}/min_freq_khz...")
        try:
            with open(os.path.join(dir, "max_freq_khz"), "w") as max_file:
                max_file.write(str(uncore_freq))

            with open(os.path.join(dir, "min_freq_khz"), "w") as min_file:
                min_file.write(str(uncore_freq))

            # Verify the values were set correctly
            with open(os.path.join(dir, "max_freq_khz"), "r") as max_file:
                max_freq = max_file.read().strip()

            with open(os.path.join(dir, "min_freq_khz"), "r") as min_file:
                min_freq = min_file.read().strip()

            if max_freq != str(uncore_freq) or min_freq != str(uncore_freq):
                print(f"Failed to set uncore frequency in {dir}. Exiting...")
                return False

        except Exception as e:
            print(f"Error while setting uncore frequency: {e}")
            return False

    print(f"Uncore frequency set to {uncore_freq} kHz successfully.")
    return True

# Function to calculate CPU ranges
def calculate_cpu_ranges(cores):
    offset = cores // 2 - 1
    cpu_ranges = f"0-{offset},28-{offset+28},56-{offset+56},84-{offset+84}"
    if offset == 0:
        return f"0,28,56,84"
    else:
        return cpu_ranges

# Function to adjust CPU idle state
def adjust_cpu_idle_state(cores, all_idle=False, dry_run=False):
    try:
        if all_idle:
            print("Setting all CPUs to idle...")
            if dry_run:
                print("[Dry Run] Skipping actual idle state adjustment.")
                return True
            result = subprocess.run([
                "cpupower", "idle-set", "-E"
            ])
        else:
            cpu_ranges = calculate_cpu_ranges(cores)
            print(f"Adjusting CPU idle state for CPU ranges {cpu_ranges}...")
            if dry_run:
                print("[Dry Run] Skipping actual idle state adjustment.")
                return True
            result = subprocess.run([
                "cpupower", "-c", cpu_ranges, "idle-set", "-D", "1"
            ])

        if result.returncode == 0:
            print("CPU idle state adjusted successfully.")
        else:
            print("Failed to adjust CPU idle state. Exiting...")
            return False

    except Exception as e:
        print(f"Error while adjusting CPU idle state: {e}")
        return False

    return True

# Function to set CPU frequency
def set_cpu_frequency(cores, freq, dry_run=False):
    cpu_ranges = calculate_cpu_ranges(cores)
    print(f"Setting CPU frequency for CPU ranges {cpu_ranges} to {freq} MHz...")
    if dry_run:
        print("[Dry Run] Skipping actual CPU frequency setting.")
        return True
    try:
        result = subprocess.run([
            "cpupower", "-c", cpu_ranges, "frequency-set", "--freq", str(freq)
        ])

        if result.returncode == 0:
            print("CPU frequency set successfully.")
        else:
            print("Failed to set CPU frequency. Exiting...")
            return False

    except Exception as e:
        print(f"Error while setting CPU frequency: {e}")
        return False

    return True

# Function to sweep through CPU load levels and generate load on active cores
def sweep_cpu_load(cores, load_levels, duration, dry_run=False):
    cpu_ranges = calculate_cpu_ranges(cores)
    for load in load_levels:
        print(f"Starting CPU load generation on CPU ranges {cpu_ranges} with load {load} for {duration} seconds...")
        if dry_run:
            print("[Dry Run] Skipping actual CPU load generation.")
            continue
        try:
            result = subprocess.run([
                "python3", "./CPULoadGenerator.py",
                "-c", cpu_ranges,
                "-l", str(load),
                "-d", str(duration)
            ])

            if result.returncode == 0:
                print(f"CPU load generation with load {load} completed successfully.")
            else:
                print(f"Failed to generate CPU load with load {load}. Exiting...")
                return False

        except Exception as e:
            print(f"Error during CPU load generation: {e}")
            return False

    return True

# Main workflow
if __name__ == "__main__":
    UNCORE_FREQ_800MHZ = "800000"  # kHz
    UNCORE_FREQ_2400MHZ = "2400000"  # kHz
    CPU_FREQ_800MHZ = "800MHz"
    CPU_FREQ_2400MHZ = "2000MHz"
    LOAD_LEVELS = [0.1, 0.2, 0.5, 0.8, 0.9]  # Example load levels in percentage
    DURATION = 120  # Example duration in seconds

    DRY_RUN = False  # Set to False to execute commands

    for active_cores in range(2, 56, 2):
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Running workflow for {active_cores} active cores...")

        steps = [
            (set_uncore_frequency, UNCORE_FREQ_800MHZ, DRY_RUN),
            (adjust_cpu_idle_state, 56, True, DRY_RUN),
            (set_cpu_frequency, 56, CPU_FREQ_800MHZ, DRY_RUN),
            (time.sleep, 30),
            (set_uncore_frequency, UNCORE_FREQ_2400MHZ, DRY_RUN),
            (adjust_cpu_idle_state, active_cores, False, DRY_RUN),
            (set_cpu_frequency, active_cores, CPU_FREQ_2400MHZ, DRY_RUN),
            (sweep_cpu_load, active_cores, LOAD_LEVELS, DURATION, DRY_RUN),
        ]

        for step in steps:
            func = step[0]
            args = step[1:]

            if func == time.sleep:
                func(*args)
                continue

            if not func(*args):
                print(f"Error during step {func.__name__}. Exiting...")
                break

        print(f"Workflow for {active_cores} active cores completed.\n")
        
    print("Main workflow completed.")

