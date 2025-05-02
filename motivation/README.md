# Power Settings Test Suite

A bash script for testing system power configurations under various CPU utilization levels, with automated timestamp logging.

## Features

- **Power Configuration Testing**:
  - CPU C-State Control (`idle`)
  - CPU Frequency Scaling (`freq`)
  - Uncore Frequency Control (`uncore`)
  - Any combination of above configurations

- **Workload Simulation**:
  - Tests at 0%, 20%, 40%, 60%, and 80% CPU utilization
  - 120-second duration per utilization level
  - 15-second stabilization periods between tests

- **Automated Logging**:
  - Machine-readable CSV timestamp log
  - ISO 8601 formatted timestamps
  - Start/end times for each configuration

## Prerequisites

- Linux system with:
  - `cpupower` utility installed
  - Python 3.x
  - Sudo privileges
- CPU Load Generator Python script in path:
  ```bash
  git clone https://github.com/your-repo/CPULoadGenerator.git
  ```

## Installation

1. Clone repository:
   ```bash
   git clone https://github.com/your-repo/power-test-suite.git
   cd power-test-suite
   ```

2. Make script executable:
   ```bash
   chmod +x power_test.sh
   ```

3. Verify uncore path (adjust if needed):
   ```bash
   sudo find /sys/devices -name '*uncore*' $ -name 'max_freq_khz' -o -name 'min_freq_khz' $
   ```

## Usage

```bash
sudo ./power_test.sh [CONFIGURATIONS...]
```

### Examples

Test individual configurations:
```bash
sudo ./power_test.sh idle
sudo ./power_test.sh freq
sudo ./power_test.sh uncore
```

Test combined configurations:
```bash
sudo ./power_test.sh idle+freq
sudo ./power_test.sh freq+uncore
sudo ./power_test.sh idle+freq+uncore
```

Test multiple configurations in sequence:
```bash
sudo ./power_test.sh idle freq uncore idle+freq
```

## Output

1. **Console Output**:
   - Color-coded progress updates
   - Real-time status messages
   - Test duration estimates

2. **Timestamp Log (`power_tests_timestamps.csv`)**:
   ```csv
   configuration,start_time,end_time
   idle,2023-10-05T14:30:00+0200,2023-10-05T14:45:00+0200
   idle+freq,2023-10-05T14:46:00+0200,2023-10-05T15:05:00+0200
   ```

## Customization

1. **Workload Parameters**:
   - Modify `generate_workload()` function:
     ```bash
     # Current settings:
     -d 120  # Duration in seconds
     -l 0.8  # Load level (0.0-1.0)
     ```

2. **Power Settings**:
   - Adjust frequency values in:
     - `set_power_freq()`
     - `restore_power_freq()`
     - `set_power_uncore()`
     - `restore_power_uncore()`

3. **Add New Power Methods**:
   1. Add entry to `power_settings` array
   2. Create corresponding set/restore functions
   3. Update usage documentation

## Troubleshooting

**Permission Denied**:
```bash
sudo visudo -f /etc/sudoers.d/power_test
# Add line:
<your_user> ALL=(ALL) NOPASSWD: /usr/bin/cpupower, /bin/tee
```

**Missing Uncore Path**:
- Verify path exists:
  ```bash
  ls /sys/devices/system/cpu/intel_uncore*
  ```
- Update `UNCORE_GLOB_PATH` variable

**Workload Generator Not Found**:
- Verify Python script path:
  ```bash
  ls CPULoadGenerator/CPULoadGenerator/CPULoadGenerator.py
  ```

## License

MIT License - See [LICENSE](LICENSE) for details

---

**Note**: Always verify power setting changes with:
```bash
watch -n1 "cat /proc/cpuinfo | grep 'MHz'"
sudo turbostat --show Package,Core,CPU,Busy%,Bzy_MHz,PkgTmp,PkgWatt,IRQ,UncMHz -i 1
```
