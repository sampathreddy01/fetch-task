# Endpoint Availability Monitor

This Python script continuously monitors the availability of configured HTTP endpoints and logs the cumulative availability by domain.

## Features

- Reads endpoint list from a YAML config file  
- Supports customizable methods, headers, and request bodies  
- Checks availability every 15 seconds  
- Endpoint is considered UP only if:
  - Status code is between 200–299  
  - Response time is <= 500ms  
- Ignores port numbers when calculating availability per domain  
- Logs availability reports and errors to both console and `monitor.log`  

---

## Getting Started

### Running the script 
python main.py config.yaml

---

## What was improved

### Issues in code

| Issue | Fix |
|-------|-----|
| No response time check | Measured elapsed time per request and verified <= 500ms |
| No domain normalization (included port) | Used urlparse.hostname to remove port from domain |
| Logging was missing | Added logging to both file and console with timestamps |
| Potential crash if body/headers were missing | Defaulted to None or {} where needed |
| Print-based reporting | Replaced with structured logging for clarity and recordkeeping |
| Check loop was naive | Used time.sleep with compensation for processing time |


---

## Logging

Logs are saved to:
- Console (with timestamp)
- File: `monitor.log`

Each cycle logs:
- Individual endpoint check result (status code and latency)
- Availability percentage per domain (cumulative)

--- 


## To Stop Monitoring

Use Ctrl+C to gracefully stop monitoring.

## Final Notes

- Fulfills all provided requirements
- Modular and production-friendly code