import sys
import time
import yaml
import requests
import logging
from urllib.parse import urlparse
from collections import defaultdict

# Constants
CHECK_INTERVAL = 15  # seconds
RESPONSE_TIMEOUT = 0.5  # seconds (500ms)

# Configure logger
logger = logging.getLogger("endpoint_monitor")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("monitor.log")
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def extract_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.hostname  # Ignores port numbers

def check_endpoint(endpoint):
    url = endpoint.get("url")
    method = endpoint.get("method", "GET")
    headers = endpoint.get("headers", {})
    body = endpoint.get("body")

    try:
        start_time = time.time()
        response = requests.request(method, url, headers=headers, json=yaml.safe_load(body) if body else None, timeout=RESPONSE_TIMEOUT)
        elapsed_ms = (time.time() - start_time) * 1000

        is_up = 200 <= response.status_code < 300 and elapsed_ms <= 500
        status = "UP" if is_up else "DOWN"

        logger.info(f"Checked {url} [{status}] - Status: {response.status_code}, Time: {elapsed_ms:.2f}ms")
        return is_up

    except requests.RequestException as e:
        logger.error(f"Error checking {url}: {e}")
        return False

def monitor_endpoints(config_path):
    config = load_config(config_path)
    if not isinstance(config, list):
        logger.error("Invalid YAML structure: Expected a list of endpoints")
        sys.exit(1)

    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})
    next_run = time.time()
    while True:
        cycle_start = time.time()
        for endpoint in config:
            url = endpoint.get("url")
            if not url:
                logger.warning("Skipping endpoint with missing URL")
                continue

            domain = extract_domain(url)
            is_up = check_endpoint(endpoint)

            domain_stats[domain]["total"] += 1
            if is_up:
                domain_stats[domain]["up"] += 1

        logger.info("\n--- Availability Report ---")
        for domain, stats in domain_stats.items():
            availability = (stats["up"] / stats["total"]) * 100
            logger.info(f"{domain} - Availability: {availability:.2f}%")

        next_run += CHECK_INTERVAL
        sleep_time = max(0, next_run - time.time())
        time.sleep(sleep_time)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file.yaml>")
        sys.exit(1)

    try:
        monitor_endpoints(sys.argv[1])
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user.")
