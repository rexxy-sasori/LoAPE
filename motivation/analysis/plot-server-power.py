#!/usr/bin/env python3
import pandas as pd
import argparse
from influxdb_api import init_query_api, get_host_power, execute_query, get_energy
from datetime import datetime
import os

# Default configuration
DEFAULT_TIMESTAMP_LOG = "power_tests_timestamps.csv"
RESULTS_FILE = "energy_analysis.csv"

def analyze_energy(configurations, server_group):
    """Main analysis workflow"""
    query_api = init_query_api()
    results = []
    
    for idx, row in configurations.iterrows():
        config = row['configuration']
        start = row['start_time']
        end = row['end_time']
        
        print(f"\n🔍 Analyzing {config} ({start} to {end})")
        
        total_energy = 0
        server_data = []
        
        for server in server_group:
            try:
                # Query power data
                qc = get_host_power(start, end, server, deltat='1s')
                ts = execute_query(query_api, qc).reset_index()
                ts.columns = ["time", "values"]
                
                # Calculate energy
                energy = get_energy(ts)
                total_energy += energy
                server_data.append({
                    'server': server,
                    'energy': energy,
                    'data_points': len(ts)
                })
                
                print(f"  {server}: {energy:.2f} J")
                
            except Exception as e:
                print(f"  ❌ Error with {server}: {str(e)}")
                server_data.append({'server': server, 'error': str(e)})
        
        # Save results
        results.append({
            'configuration': config,
            'start_time': start,
            'end_time': end,
            'total_energy': total_energy,
            'servers': server_data
        })
        
        # Save incremental results
        pd.DataFrame(results).to_csv(RESULTS_FILE, index=False)
    
    return results

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Energy consumption analyzer for power tests')
    parser.add_argument('-s', '--servers', required=True,
                        help='Comma-separated list of server names (e.g., "fusion-101,fusion-102")')
    parser.add_argument('-t', '--timestamp-log', default=DEFAULT_TIMESTAMP_LOG,
                        help=f'Path to timestamp CSV file (default: {DEFAULT_TIMESTAMP_LOG})')
    args = parser.parse_args()
    
    # Process server group
    server_group = [s.strip() for s in args.servers.split(',')]
    print(f"📡 Analyzing servers: {', '.join(server_group)}")
    print(f"📅 Using timestamp log: {args.timestamp_log}")

    # Load test configurations
    if not os.path.exists(args.timestamp_log):
        print(f"❌ Timestamp log not found: {args.timestamp_log}")
        return

    configs = pd.read_csv(args.timestamp_log)
    print(f"📊 Loaded {len(configs)} configurations from {args.timestamp_log}")
    
    # Run analysis
    results = analyze_energy(configs, server_group)
    
    # Generate final report
    summary = pd.DataFrame([{
        'configuration': r['configuration'],
        'start_time': r['start_time'],
        'end_time': r['end_time'],
        'total_energy': r['total_energy']
    } for r in results])
    
    summary.to_csv("energy_summary.csv", index=False)
    print(f"\n✅ Analysis complete. Results saved to:")
    print(f"  - Detailed data: {RESULTS_FILE}")
    print(f"  - Summary report: energy_summary.csv")

if __name__ == "__main__":
    main()
