from prometheus_client import start_http_server, Gauge
import requests
import time
import re

# Base URLs for APIs
METRICS_API = "http://rating-api.rating.svc.cluster.local:80/metrics"
INSTANCE_API = "http://rating-api.rating.svc.cluster.local:80/instances/get?name="

def sanitize_metric_name(metric_name):
    """Replace invalid characters in metric names with underscores."""
    return re.sub(r'[^a-zA-Z0-9_:]', '_', metric_name)

metrics = {}

def fetch_metrics_from_api():
    """Fetch all metric names from the metrics API."""
    try:
        response = requests.get(METRICS_API)
        response.raise_for_status()
        data = response.json()
        return [item["metric"] for item in data.get("results", [])]
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return []

def fetch_promql_for_metric(metric_name):
    """Fetch PromQL and replace placeholders for a given metric."""
    try:
        instance_name = f"rating-rule-instance-{metric_name}"
        response = requests.get(INSTANCE_API + instance_name)
        response.raise_for_status()
        data = response.json()
        spec = data.get("results", {}).get("spec", {})
        
        promql = spec.get("metric", "")
        replacements = {
            "{price}": spec.get("price", "0"),
            "{memory}": spec.get("memory", "1"),
            "{cpu}": spec.get("cpu", "1"),
        }

        # Replace all placeholders with actual values
        for placeholder, value in replacements.items():
            promql = promql.replace(placeholder, value)
        
        return promql
    except Exception as e:
        print(f"Error fetching PromQL for {metric_name}: {e}")
        return None

def update_metrics():
    """Fetch and update all metrics."""
    global metrics
    metric_names = fetch_metrics_from_api()

    for raw_metric_name in metric_names:
        # Use the original name for fetching PromQL
        promql = fetch_promql_for_metric(raw_metric_name)
        if promql:
            # Sanitize the metric name for Prometheus
            sanitized_metric_name = sanitize_metric_name(raw_metric_name)
            if sanitized_metric_name not in metrics:
                # Create a new Prometheus Gauge if it doesn't exist
                metrics[sanitized_metric_name] = Gauge(
                    sanitized_metric_name, f"Metric for {raw_metric_name}"
                )

            try:
                # Query Prometheus for the PromQL
                prometheus_response = requests.get(
                    "http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090/api/v1/query",
                    params={"query": promql},
                )
                prometheus_response.raise_for_status()
                prometheus_data = prometheus_response.json()

                # Update metric value
                if prometheus_data["status"] == "success" and prometheus_data["data"]["result"]:
                    value = float(prometheus_data["data"]["result"][0]["value"][1])
                    metrics[sanitized_metric_name].set(value)
                else:
                    metrics[sanitized_metric_name].set(0)  # Default to 0 if no data
            except Exception as e:
                print(f"Error updating metric {raw_metric_name}: {e}")

if __name__ == "__main__":
    # Start Prometheus HTTP server
    start_http_server(8000)  # Expose metrics on port 8000

    # Periodically update metrics
    while True:
        update_metrics()
        time.sleep(20)  # Adjust interval as needed
