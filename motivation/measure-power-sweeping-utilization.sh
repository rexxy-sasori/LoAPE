#!/bin/bash
set -e

# Timestamp configuration
TS_LOG="power_tests_timestamps.csv"
TS_FORMAT="%Y-%m-%dT%H:%M:%S%z"
echo "configuration,start_time,end_time" > "$TS_LOG"

# Power adjustment configurations
declare -A power_settings=(
    ["idle"]="set_power_idle restore_power_idle"
    ["freq"]="set_power_freq restore_power_freq"
    ["uncore"]="set_power_uncore restore_power_uncore"
)

# CPU Power Functions
set_power_idle() { sudo cpupower idle-set -E; }
restore_power_idle() { sudo cpupower idle-set -D 1; }

set_power_freq() { sudo cpupower frequency-set -f 800MHz; }
restore_power_freq() { sudo cpupower frequency-set -f 2000MHz; }

# Uncore Frequency Control
UNCORE_GLOB_PATH="/sys/devices/system/cpu/intel_uncore*"

set_power_uncore() {
    for uncore_dir in $UNCORE_GLOB_PATH; do
        max_path="$uncore_dir/max_freq_khz"
        min_path="$uncore_dir/min_freq_khz"
        echo "800000" | sudo tee "$max_path" "$min_path" >/dev/null
    done
}

restore_power_uncore() {
    for uncore_dir in $UNCORE_GLOB_PATH; do
        max_path="$uncore_dir/max_freq_khz"
        min_path="$uncore_dir/min_freq_khz"
        echo "2400000" | sudo tee "$max_path" "$min_path" >/dev/null
    done
}

# Timestamp logging
log_timestamp() {
    echo "$1,$2,$3" >> "$TS_LOG"
}

# Common functions
show_header() {
    echo -e "\n\033[1;34m=== [$(date +"%F %T")] Testing: $1 ===\033[0m"
}

wait_stabilization() {
    echo "⏳ [$(date +"%T")] Stabilizing for 15s..."
    sleep 15
}

generate_workload() {
    local level=$1
    local load=$(awk "BEGIN {printf "%.2f", $level/100}")
    echo -e "\n🔧 [$(date +"%T")] Generating ${level}% load"
    python CPULoadGenerator/CPULoadGenerator/CPULoadGenerator.py -l $load -d 120
}

run_configuration() {
    local config=$1
    local start_ts=$(date +"$TS_FORMAT")
    
    show_header "$config"
    
    # Apply settings
    IFS='+' read -ra methods <<< "$config"
    for method in "${methods[@]}"; do
        ${power_settings[$method]%% *}
    done

    # Run tests
    for cpu in 0 20 40 60 80; do
        echo -e "\n\033[1;36m[$(date +"%T")] Testing ${cpu}%\033[0m"
        wait_stabilization
        generate_workload $cpu
        wait_stabilization
    done

    # Restore settings
    for ((i=${#methods[@]}-1; i>=0; i--)); do
        ${power_settings[${methods[i]}]#* }
    done

    # Log timestamps
    local end_ts=$(date +"$TS_FORMAT")
    log_timestamp "$config" "$start_ts" "$end_ts"
}

# Main execution
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 [config1] [config2] ..."
    echo "Available configs: individual (idle,freq,uncore) or combined (idle+freq etc)"
    exit 1
fi

echo "=============================================="
echo " Power Test Suite"
echo " Started: $(date +"$TS_FORMAT")"
echo " Timestamp log: $TS_LOG"
echo "=============================================="

for config in "$@"; do
    run_configuration "$config"
done

echo -e "\n\033[1;32m✅ All tests completed! Timestamps saved to $TS_LOG\033[0m"
