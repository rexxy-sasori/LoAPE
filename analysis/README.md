Here's a comprehensive README.md for running the energy consumption analysis:

```markdown
# Energy Consumption Analysis Toolkit

This toolkit analyzes server energy consumption using power metrics stored in InfluxDB, correlated with power configuration test timestamps.

## Prerequisites

1. **InfluxDB Setup**:
   - Running InfluxDB 2.x instance
   - Bucket created for power metrics
   - Token with read access to the bucket
   - Power metrics stored with proper measurement name (default: `power`)

2. **Python Environment**:
   - Python 3.8+
   - Required packages:
     ```bash
     pip install pandas influxdb-client scipy
     ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rexxy-sasori/LoAPE.git
   cd analysis
   ```

2. Configure InfluxDB connection:
   ```python
   # influxdb_api.py
   url = "http://localhost:8086"          # InfluxDB URL
   token = "your-auth-token"              # InfluxDB access token
   org = "your-org"                       # Organization name
   bucket = "power-metrics"               # Bucket name
   ```

## Usage

### 1. Run Power Configuration Tests
Generate timestamp log with the power test script:
```bash
sudo ./motivation/measure-power-sweeping-utilization.sh idle freq uncore idle+freq+uncore
```

### 2. Perform Energy Analysis
```bash
python analysis/plot-server-power.py \
  --servers <server-names> \
  --timestamp-log <bash's output csv file>
```

#### Command Line Arguments:
| Argument | Description | Example |
|----------|-------------|---------|
| `-s/--servers` | Comma-separated server list | `fusion-101,fusion-102` |
| `-t/--timestamp-log` | Path to timestamp CSV | `custom_times.csv` |
| `--help` | Show help message | |

### Example Output:
```
📡 Analyzing servers: fusion-101, fusion-102, fusion-103
📅 Using timestamp log: power_tests_timestamps.csv
📊 Loaded 3 configurations from power_tests_timestamps.csv

🔍 Analyzing idle (2024-04-08T10:00:00Z to 2024-04-08T10:15:00Z)
  fusion-101: 1500.32 J
  fusion-102: 1489.21 J
  fusion-103: 1523.15 J

🔍 Analyzing freq (2024-04-08T10:20:00Z to 2024-04-08T10:35:00Z)
  fusion-101: 1420.15 J
  ...
  
✅ Analysis complete. Results saved to:
  • Detailed data: energy_analysis.csv

  • Summary report: energy_summary.csv

```

## Output Files

1. **energy_analysis.csv**:
   ```csv
   configuration,start_time,end_time,total_energy,servers
   idle,2024-04-08T10:00:00Z,2024-04-08T10:15:00Z,4512.68,"[{'server': 'fusion-101', ...}]"
   ```

2. **energy_summary.csv**:
   ```csv
   configuration,start_time,end_time,total_energy
   idle,2024-04-08T10:00:00Z,2024-04-08T10:15:00Z,4512.68
   freq,2024-04-08T10:20:00Z,2024-04-08T10:35:00Z,4298.41
   ```

## Troubleshooting

**Common Issues**:
1. **Connection Errors**:
   - Verify InfluxDB URL and port
   - Check token permissions
   - Ensure network connectivity

2. **Missing Data**:
   - Confirm metric name matches InfluxDB measurement
   - Verify time range contains actual data
   - Check server naming consistency

3. **Timestamp Format**:
   - Ensure CSV format: `configuration,start_time,end_time`
   - Verify ISO 8601 timestamps in UTC

## Security Considerations

1. Store InfluxDB tokens in environment variables for production use
2. Use read-only tokens for analysis
3. Keep timestamp logs in secure storage

## Documentation

- [InfluxDB Python Client Documentation](https://github.com/influxdata/influxdb-client-python)
- [Power Metric Collection Setup Guide](https://docs.influxdata.com/)
- [Energy Calculation Methodology](#) (Internal document)

---

**Note**: The analysis calculates energy consumption by integrating power measurements over time (∫P(t)dt) using Riemann sum approximation.
``` 

This README provides:
1. Clear setup and configuration instructions
2. End-to-end usage examples
3. Troubleshooting guidance
4. Security considerations
5. Documentation references
6. Explanation of analysis methodology

The markdown structure ensures compatibility with GitHub/GitLab documentation rendering while maintaining readability in plain text editors.
