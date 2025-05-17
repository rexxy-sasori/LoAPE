#!/bin/bash

# Starting RPS value
start_rps=7000
# Ending RPS valujie
end_rps=7500
# Increment in RPS
increment_rps=500
# gRPC call details (for ghz, adjust as per your actual call)
call="helloworld.Greeter/SayHello"

# Check if the tool, host, duration, and log_suffix arguments are provided
if [ $# -lt 4 ]; then
    echo "Usage: $0 <tool: ghz|k6> <host> <duration> <log_suffix> [<k6_script>]"
    exit 1
fi

# Get the tool, host, duration, and log_suffix from the command line arguments
tool=$1
host=$2
duration=$3
log_suffix=$4

# If k6 is selected, the fifth argument (k6_script) must be provided
if [ "$tool" == "k6" ]; then
    if [ $# -ne 5 ]; then
        echo "For k6, you must specify the path to a k6 script."
        echo "Usage: $0 k6 <host> <duration> <log_suffix> <k6_script>"
        exit 1
    fi
    k6_script=$5
    if [ ! -f "$k6_script" ]; then
        echo "Error: k6 script file '$k6_script' not found."
        exit 1
    fi
fi

# Combined output file
combined_file="load_test_summary_${tool}_${log_suffix}.log"

# Write a starting message to the combined file
echo "Starting RPS sweep using $tool. Results will be appended to $combined_file" > $combined_file

for ((rps=$start_rps; rps<=$end_rps; rps+=$increment_rps)); do
    # Add a header for each RPS value in the combined file
    echo "=========================================" >> $combined_file
    echo "Summary for RPS: $rps" >> $combined_file
    echo "=========================================" >> $combined_file

    if [ "$tool" == "ghz" ]; then
        # Run the ghz command with RPS
        ghz --insecure --call "$call" -c 100 -r $rps -z $duration --async "$host" >> $combined_file
    elif [ "$tool" == "k6" ]; then
        # For k6, calculate the number of VUs based on RPS and duration
        #vus=$((rps * duration / 1000)) # Simple calculation of virtual users (adjust if needed)
        vus=25
	k6 run --rps $rps -e VUS=$vus -e DURATION=$duration --summary-trend-stats 'avg,min,med,max,p(90),p(95),p(99)' $k6_script >> $combined_file
    else
        echo "Unsupported tool: $tool. Use 'ghz' or 'k6'." >> $combined_file
        exit 1
    fi
    sleep 30   
    echo "Completed test for RPS: $rps. Summary appended to $combined_file"
done

echo "All RPS sweep tests using $tool completed. You can find the combined summaries in $combined_file"

