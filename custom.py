from prometheus_client import start_http_server, Gauge
import requests
import time
import re
from datetime import datetime, timedelta

INSTANCES_LIST_API = "http://rating-api.rating.svc.cluster.local:80/instances/list"
INSTANCE_GET_API = "http://rating-api.rating.svc.cluster.local:80/instances/get?name="
PROMETHEUS_URL = "http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"

def sanitize_metric_name(metric_name):
    return re.sub(r'[^a-zA-Z0-9_:]', '_', metric_name)

regular_metrics = {}
pod_metrics = {}
energy_reduction_metrics = {}
carbon_reduction_metrics = {}
energy_performance_metrics = {}
capacity_utilization_metrics = {}
network_slice_metrics = {}
energy_efficiency_metrics = {}

def fetch_instances_from_api():
    try:
        response = requests.get(INSTANCES_LIST_API)
        response.raise_for_status()
        data = response.json()
        instance_names = data.get("results", [])
        
        metric_names = []
        for instance_name in instance_names:
            instance_response = requests.get(INSTANCE_GET_API + instance_name)
            if instance_response.status_code == 200:
                instance_data = instance_response.json()
                spec = instance_data.get("results", {}).get("spec", {})
                
                metric_name = spec.get("name")
                if metric_name:
                    metric_names.append({
                        "metric_name": metric_name,
                        "instance_name": instance_name,
                        "spec": spec
                    })
                    
        return metric_names
    except Exception as e:
        print(f"Error fetching instances: {e}")
        return []

def fetch_running_pods():
    try:
        query = 'kube_pod_info{pod!=""}'
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        response.raise_for_status()
        data = response.json()
        
        pods = []
        if data["status"] == "success" and data["data"]["result"]:
            for result in data["data"]["result"]:
                labels = result.get("metric", {})
                pod_name = labels.get("pod", "")
                namespace = labels.get("namespace", "")
                if pod_name and namespace:
                    if namespace not in ["kube-system", "kube-public", "kube-node-lease"]:
                        pods.append({
                            "pod": pod_name,
                            "namespace": namespace
                        })
        
        return pods
    except Exception as e:
        print(f"Error fetching pods: {e}")
        return []

def fetch_active_namespaces():
    try:
        pods = fetch_running_pods()
        namespaces = set()
        for pod in pods:
            namespaces.add(pod["namespace"])
        
        unique_namespaces = sorted(list(namespaces))
        print(f"DEBUG: Found {len(unique_namespaces)} unique active namespaces: {unique_namespaces}")
        return unique_namespaces
    except Exception as e:
        print(f"Error fetching namespaces: {e}")
        return []

def extract_prometheus_value(prometheus_data):
    try:
        if prometheus_data["status"] != "success":
            return None
            
        result = prometheus_data["data"]["result"]
        result_type = prometheus_data["data"].get("resultType", "")
        
        if not result:
            return 0
        
        if result_type == "scalar":
            if isinstance(result, list) and len(result) >= 2:
                return float(result[1])
            
        elif result_type == "vector":
            if isinstance(result, list) and len(result) > 0:
                first_result = result[0]
                if isinstance(first_result, dict) and "value" in first_result:
                    if isinstance(first_result["value"], list) and len(first_result["value"]) >= 2:
                        return float(first_result["value"][1])
        
        if isinstance(result, list) and len(result) > 0:
            first_result = result[0]
            if isinstance(first_result, dict) and "value" in first_result:
                if isinstance(first_result["value"], list) and len(first_result["value"]) >= 2:
                    return float(first_result["value"][1])
            elif isinstance(first_result, (int, float)):
                return float(first_result)
        
        if isinstance(result, (int, float)):
            return float(result)
            
        if isinstance(result, str):
            try:
                return float(result)
            except ValueError:
                pass
        
        return 0
        
    except Exception as e:
        print(f"Error extracting Prometheus value: {e}")
        return 0

def get_pod_memory_gb(pod_name, namespace):
    query = f'''
    sum(container_memory_usage_bytes{{
        pod="{pod_name}",
        namespace="{namespace}",
        container!="POD",
        container!=""
    }}) / (1024*1024*1024)
    '''
    
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        response.raise_for_status()
        data = response.json()
        return extract_prometheus_value(data)
    except Exception as e:
        print(f"Error getting pod memory for {pod_name}: {e}")
        return 0

def get_pod_cpu_cores(pod_name, namespace, timeframe="5m"):
    query = f'''
    sum(rate(container_cpu_usage_seconds_total{{
        pod="{pod_name}",
        namespace="{namespace}",
        container!="POD",
        container!=""
    }}[{timeframe}]))
    '''
    
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        response.raise_for_status()
        data = response.json()
        return extract_prometheus_value(data)
    except Exception as e:
        print(f"Error getting pod CPU for {pod_name}: {e}")
        return 0

def get_pod_storage_gb(pod_name, namespace):
    network_usage = get_pod_network_bytes_per_sec(pod_name, namespace)
    
    storage_gb_approx = network_usage / (1024*1024) * 0.1
    
    return max(storage_gb_approx, 0.1)

def get_pod_cpu_usage_rate(pod_name, namespace, timeframe="5m"):
    cores_used = get_pod_cpu_cores(pod_name, namespace, timeframe)
    
    return min(cores_used, 1.0)

def get_pod_disk_io_rate(pod_name, namespace, timeframe="5m"):
    cpu_usage = get_pod_cpu_usage_rate(pod_name, namespace, timeframe)
    
    disk_io_rate = cpu_usage * 0.1
    
    return disk_io_rate

def get_pod_network_bytes_per_sec(pod_name, namespace, timeframe="5m"):
    query = f'''
    sum(rate(container_network_transmit_bytes_total{{
        pod="{pod_name}",
        namespace="{namespace}"
    }}[{timeframe}])) + 
    sum(rate(container_network_receive_bytes_total{{
        pod="{pod_name}",
        namespace="{namespace}"
    }}[{timeframe}]))
    '''
    
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        response.raise_for_status()
        data = response.json()
        return extract_prometheus_value(data)
    except Exception as e:
        print(f"Error getting pod network for {pod_name}: {e}")
        return 0

def calculate_carbon_direct(pod_name, namespace, price):
    memory_gb = get_pod_memory_gb(pod_name, namespace)
    cpu_cores = get_pod_cpu_cores(pod_name, namespace)
    storage_gb = get_pod_storage_gb(pod_name, namespace)
    
    carbon_value = (memory_gb + cpu_cores + storage_gb) * 220 / 1000 * float(price)
    
    return carbon_value

def calculate_energy_direct(pod_name, namespace):
    cpu_usage = get_pod_cpu_usage_rate(pod_name, namespace)
    memory_gb = get_pod_memory_gb(pod_name, namespace)
    disk_io = get_pod_disk_io_rate(pod_name, namespace)
    network_bytes_sec = get_pod_network_bytes_per_sec(pod_name, namespace)
    
    base_power = 25
    cpu_component = 100 * cpu_usage
    memory_component = 3 * memory_gb / 8
    constant_1 = 2
    disk_component = 6 * disk_io
    constant_2 = 5
    network_component = 10 * network_bytes_sec / (100 * 1024 * 1024)
    constant_3 = 15
    psu_efficiency = 0.92
    
    total_before_efficiency = (base_power + cpu_component + memory_component + 
                             constant_1 + disk_component + constant_2 + 
                             network_component + constant_3)
    
    energy_value = total_before_efficiency / psu_efficiency
    
    return energy_value

def get_prometheus_current_value(query):
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success" and data["data"]["result"]:
            current_value = float(data["data"]["result"][0]["value"][1])
            return current_value
        
        return 0
        
    except Exception as e:
        print(f"Error getting current value: {e}")
        return 0

def calculate_energy_efficiency_pod(pod_name, namespace):
    try:
        query = f'''
        (
          sum(rate(container_cpu_usage_seconds_total{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}}[5m])) * 
          sum(container_memory_working_set_bytes{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}})
        ) / scalar(server_energy_consumption_by_pod{{pod="{pod_name}", namespace="{namespace}"}})
        '''
        
        efficiency_value = get_prometheus_current_value(query)
        
        if efficiency_value == 0:
            query_fallback = f'''
            (
              sum(rate(container_cpu_usage_seconds_total{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}}[5m])) * 
              sum(container_memory_working_set_bytes{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}})
            ) / on() server_energy_consumption_by_pod{{pod="{pod_name}", namespace="{namespace}"}}
            '''
            efficiency_value = get_prometheus_current_value(query_fallback)
            if efficiency_value > 0:
                print(f"   Used fallback on() method for {namespace}/{pod_name}")
        
        return efficiency_value
        
    except Exception as e:
        print(f"Error calculating energy efficiency for pod {namespace}/{pod_name}: {e}")
        return 0

def calculate_energy_efficiency_cluster():
    try:
        query = '''
        (
          avg(rate(container_cpu_usage_seconds_total{container!="POD", container!=""}[5m])) * 
          avg(container_memory_working_set_bytes{container!="POD", container!=""})
        ) / sum(server_energy_consumption)
        '''
        
        efficiency_value = get_prometheus_current_value(query)
        
        return efficiency_value
        
    except Exception as e:
        print(f"Error calculating cluster energy efficiency: {e}")
        return 0

def calculate_energy_efficiency_namespace(namespace):
    try:
        query = f'''
        (
          avg(rate(container_cpu_usage_seconds_total{{namespace="{namespace}", container!="POD", container!=""}}[5m])) * 
          avg(container_memory_working_set_bytes{{namespace="{namespace}", container!="POD", container!=""}})
        ) / sum(server_energy_consumption_by_pod{{namespace="{namespace}"}})
        '''
        
        efficiency_value = get_prometheus_current_value(query)
        
        return efficiency_value
        
    except Exception as e:
        print(f"Error calculating namespace energy efficiency for {namespace}: {e}")
        return 0

def update_energy_efficiency_metrics():
    global energy_efficiency_metrics
    
    print("⚡ Updating Energy Efficiency (Resource Utilization) metrics...")
    
    pod_metric_name = "energy_efficiency_utilization_by_pod"
    if pod_metric_name not in energy_efficiency_metrics:
        energy_efficiency_metrics[pod_metric_name] = Gauge(
            pod_metric_name,
            "Energy efficiency based on CPU and Memory utilization per pod ((CPU_rate * Memory_bytes) / Energy_W)",
            ["pod", "namespace", "efficiency_class"]
        )
    
    namespace_metric_name = "energy_efficiency_utilization_by_namespace"
    if namespace_metric_name not in energy_efficiency_metrics:
        energy_efficiency_metrics[namespace_metric_name] = Gauge(
            namespace_metric_name,
            "Energy efficiency based on CPU and Memory utilization per namespace",
            ["namespace", "efficiency_class"]
        )
    
    cluster_metric_name = "energy_efficiency_utilization_cluster"
    if cluster_metric_name not in energy_efficiency_metrics:
        energy_efficiency_metrics[cluster_metric_name] = Gauge(
            cluster_metric_name,
            "Energy efficiency based on CPU and Memory utilization for entire cluster"
        )
    
    cpu_efficiency_metric = "energy_efficiency_cpu_by_pod"
    if cpu_efficiency_metric not in energy_efficiency_metrics:
        energy_efficiency_metrics[cpu_efficiency_metric] = Gauge(
            cpu_efficiency_metric,
            "CPU efficiency per watt by pod (CPU_rate / Energy_W)",
            ["pod", "namespace"]
        )
    
    memory_efficiency_metric = "energy_efficiency_memory_by_pod"
    if memory_efficiency_metric not in energy_efficiency_metrics:
        energy_efficiency_metrics[memory_efficiency_metric] = Gauge(
            memory_efficiency_metric,
            "Memory efficiency per watt by pod (Memory_bytes / Energy_W)",
            ["pod", "namespace"]
        )
    
    resource_score_metric = "resource_utilization_score_by_pod"
    if resource_score_metric not in energy_efficiency_metrics:
        energy_efficiency_metrics[resource_score_metric] = Gauge(
            resource_score_metric,
            "Combined CPU and Memory utilization score by pod (CPU_rate * Memory_bytes)",
            ["pod", "namespace"]
        )
    
    try:
        cluster_efficiency = calculate_energy_efficiency_cluster()
        energy_efficiency_metrics[cluster_metric_name].set(cluster_efficiency)
        print(f"✅ Updated {cluster_metric_name} = {cluster_efficiency:.6e}")
    except Exception as e:
        print(f"❌ Error updating cluster energy efficiency: {e}")
        energy_efficiency_metrics[cluster_metric_name].set(0)
    
    active_namespaces = fetch_active_namespaces()
    namespace_results = []
    
    for namespace in active_namespaces:
        try:
            namespace_efficiency = calculate_energy_efficiency_namespace(namespace)
            
            if namespace_efficiency > 0:
                if namespace_efficiency > 1e6:
                    efficiency_class = "excellent"
                elif namespace_efficiency > 1e5:
                    efficiency_class = "good"
                elif namespace_efficiency > 1e4:
                    efficiency_class = "average"
                else:
                    efficiency_class = "poor"
                
                energy_efficiency_metrics[namespace_metric_name].labels(
                    namespace=namespace,
                    efficiency_class=efficiency_class
                ).set(namespace_efficiency)
                
                namespace_results.append({
                    "namespace": namespace,
                    "efficiency": namespace_efficiency,
                    "efficiency_class": efficiency_class
                })
                
                print(f"✅ Updated {namespace_metric_name} for {namespace} = {namespace_efficiency:.6e} ({efficiency_class})")
            else:
                energy_efficiency_metrics[namespace_metric_name].labels(
                    namespace=namespace,
                    efficiency_class="no_data"
                ).set(0)
                
        except Exception as e:
            print(f"❌ Error updating namespace energy efficiency for {namespace}: {e}")
            energy_efficiency_metrics[namespace_metric_name].labels(
                namespace=namespace,
                efficiency_class="error"
            ).set(0)
    
    pods = fetch_running_pods()
    important_namespaces = ["rating", "monitoring", "default", "ubi"]
    filtered_pods = [p for p in pods if p["namespace"] in important_namespaces]
    
    pod_results = []
    
    for pod_info in filtered_pods[:20]:
        pod_name = pod_info["pod"]
        namespace = pod_info["namespace"]
        
        try:
            pod_efficiency = calculate_energy_efficiency_pod(pod_name, namespace)
            
            if pod_efficiency > 0:
                if pod_efficiency > 1e6:
                    efficiency_class = "excellent"
                elif pod_efficiency > 1e5:
                    efficiency_class = "good"
                elif pod_efficiency > 1e4:
                    efficiency_class = "average"
                else:
                    efficiency_class = "poor"
                
                energy_efficiency_metrics[pod_metric_name].labels(
                    pod=pod_name,
                    namespace=namespace,
                    efficiency_class=efficiency_class
                ).set(pod_efficiency)
                
                pod_results.append({
                    "pod": pod_name,
                    "namespace": namespace,
                    "efficiency": pod_efficiency,
                    "efficiency_class": efficiency_class
                })
                
                print(f"✅ Updated {pod_metric_name} for {namespace}/{pod_name} = {pod_efficiency:.6e} ({efficiency_class})")
                
                try:
                    cpu_query = f'sum(rate(container_cpu_usage_seconds_total{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}}[5m])) / server_energy_consumption_by_pod{{pod="{pod_name}", namespace="{namespace}"}}'
                    cpu_efficiency = get_prometheus_current_value(cpu_query)
                    energy_efficiency_metrics[cpu_efficiency_metric].labels(
                        pod=pod_name, namespace=namespace
                    ).set(cpu_efficiency)
                    
                    memory_query = f'sum(container_memory_working_set_bytes{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}}) / server_energy_consumption_by_pod{{pod="{pod_name}", namespace="{namespace}"}}'
                    memory_efficiency = get_prometheus_current_value(memory_query)
                    energy_efficiency_metrics[memory_efficiency_metric].labels(
                        pod=pod_name, namespace=namespace
                    ).set(memory_efficiency)
                    
                    resource_query = f'sum(rate(container_cpu_usage_seconds_total{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}}[5m])) * sum(container_memory_working_set_bytes{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}})'
                    resource_score = get_prometheus_current_value(resource_query)
                    energy_efficiency_metrics[resource_score_metric].labels(
                        pod=pod_name, namespace=namespace
                    ).set(resource_score)
                    
                except Exception as debug_e:
                    print(f"⚠️ Error calculating debug metrics for {namespace}/{pod_name}: {debug_e}")
                
            else:
                energy_efficiency_metrics[pod_metric_name].labels(
                    pod=pod_name,
                    namespace=namespace,
                    efficiency_class="no_data"
                ).set(0)
                
                energy_efficiency_metrics[cpu_efficiency_metric].labels(
                    pod=pod_name, namespace=namespace
                ).set(0)
                energy_efficiency_metrics[memory_efficiency_metric].labels(
                    pod=pod_name, namespace=namespace
                ).set(0)
                energy_efficiency_metrics[resource_score_metric].labels(
                    pod=pod_name, namespace=namespace
                ).set(0)
                
        except Exception as e:
            print(f"❌ Error updating pod energy efficiency for {namespace}/{pod_name}: {e}")
            energy_efficiency_metrics[pod_metric_name].labels(
                pod=pod_name,
                namespace=namespace,
                efficiency_class="error"
            ).set(0)
    
    if pod_results:
        print(f"\n📊 Energy Efficiency Summary:")
        print(f"🏗️ Cluster Efficiency: {cluster_efficiency:.6e}")
        print(f"📦 Processed {len(pod_results)} pods across {len(namespace_results)} namespaces")
        
        sorted_pods = sorted(pod_results, key=lambda x: x["efficiency"], reverse=True)
        print("🏆 Top 3 most efficient pods:")
        for i, result in enumerate(sorted_pods[:3], 1):
            print(f"   {i}. {result['namespace']}/{result['pod']}: {result['efficiency']:.6e} ({result['efficiency_class']})")
        
        sorted_namespaces = sorted(namespace_results, key=lambda x: x["efficiency"], reverse=True)
        print("🎯 Top 3 most efficient namespaces:")
        for i, result in enumerate(sorted_namespaces[:3], 1):
            print(f"   {i}. {result['namespace']}: {result['efficiency']:.6e} ({result['efficiency_class']})")
    else:
        print("⚠️ No valid energy efficiency data calculated")

def get_namespace_network_performance(namespace, timeframe="5m"):
    query = f'''
    sum(rate(container_network_transmit_bytes_total{{namespace="{namespace}"}}[{timeframe}])) + 
    sum(rate(container_network_receive_bytes_total{{namespace="{namespace}"}}[{timeframe}]))
    '''
    
    return get_prometheus_current_value(query)

def get_namespace_energy_consumption(namespace):
    query = f'sum(server_energy_consumption_by_pod{{namespace="{namespace}"}})'
    
    return get_prometheus_current_value(query)

def calculate_network_slice_efficiency(namespace):
    try:
        network_performance = get_namespace_network_performance(namespace)
        
        energy_consumption = get_namespace_energy_consumption(namespace)
        
        if energy_consumption > 0:
            network_performance_kb = network_performance / 1024
            efficiency = network_performance_kb / energy_consumption
            
            return {
                "namespace": namespace,
                "network_performance_bytes_sec": network_performance,
                "network_performance_kb_sec": network_performance_kb,
                "energy_consumption_watts": energy_consumption,
                "efficiency_kb_sec_per_watt": efficiency
            }
        else:
            return None
            
    except Exception as e:
        print(f"Error calculating network slice efficiency for {namespace}: {e}")
        return None

def update_network_slice_metrics():
    global network_slice_metrics
    
    print("🌐 Updating Network Slice Energy Efficiency metrics...")
    
    metric_name = "network_slice_energy_efficiency_by_namespace"
    if metric_name not in network_slice_metrics:
        network_slice_metrics[metric_name] = Gauge(
            metric_name,
            "Network Slice Energy Efficiency by namespace (KB/sec/W) - Higher is better",
            ["namespace", "efficiency_class"]
        )
    
    network_performance_metric = "network_slice_performance_by_namespace"
    if network_performance_metric not in network_slice_metrics:
        network_slice_metrics[network_performance_metric] = Gauge(
            network_performance_metric,
            "Network performance by namespace (KB/sec)",
            ["namespace"]
        )
    
    energy_consumption_metric = "network_slice_energy_by_namespace"
    if energy_consumption_metric not in network_slice_metrics:
        network_slice_metrics[energy_consumption_metric] = Gauge(
            energy_consumption_metric,
            "Energy consumption by namespace (W)",
            ["namespace"]
        )
    
    active_namespaces = fetch_active_namespaces()
    
    namespace_results = []
    processed_namespaces = set()
    
    for namespace in active_namespaces:
        if namespace in processed_namespaces:
            print(f"⚠️ WARNING: Namespace '{namespace}' already processed, skipping duplicate")
            continue
        
        processed_namespaces.add(namespace)
        
        try:
            result = calculate_network_slice_efficiency(namespace)
            
            if result:
                efficiency = result["efficiency_kb_sec_per_watt"]
                network_kb = result["network_performance_kb_sec"]
                energy = result["energy_consumption_watts"]
                
                if not (efficiency > 0):
                    print(f"⚠️ Invalid efficiency value for {namespace}: {efficiency}, skipping")
                    continue
                
                if efficiency > 1.0:
                    efficiency_class = "excellent"
                elif efficiency > 0.5:
                    efficiency_class = "good"
                elif efficiency > 0.2:
                    efficiency_class = "poor"
                else:
                    efficiency_class = "very_poor"
                
                network_slice_metrics[metric_name].labels(
                    namespace=namespace,
                    efficiency_class=efficiency_class
                ).set(efficiency)
                
                network_slice_metrics[network_performance_metric].labels(
                    namespace=namespace
                ).set(network_kb)
                
                network_slice_metrics[energy_consumption_metric].labels(
                    namespace=namespace
                ).set(energy)
                
                namespace_results.append({
                    "namespace": namespace,
                    "efficiency": efficiency,
                    "efficiency_class": efficiency_class,
                    "network_kb": network_kb,
                    "energy": energy
                })
                
                print(f"✅ Updated Network Slice Efficiency for {namespace} = {efficiency:.3f} KB/sec/W ({efficiency_class})")
                
            else:
                print(f"⚠️ No data available for namespace '{namespace}', setting to 0")
                network_slice_metrics[metric_name].labels(
                    namespace=namespace,
                    efficiency_class="no_data"
                ).set(0)
                network_slice_metrics[network_performance_metric].labels(
                    namespace=namespace
                ).set(0)
                network_slice_metrics[energy_consumption_metric].labels(
                    namespace=namespace
                ).set(0)
                
        except Exception as e:
            print(f"❌ Error updating network slice efficiency for {namespace}: {e}")
            network_slice_metrics[metric_name].labels(
                namespace=namespace,
                efficiency_class="error"
            ).set(0)
            network_slice_metrics[network_performance_metric].labels(
                namespace=namespace
            ).set(0)
            network_slice_metrics[energy_consumption_metric].labels(
                namespace=namespace
            ).set(0)
    
    if namespace_results:
        print(f"\n📊 Network Slice Efficiency Summary ({len(namespace_results)} namespaces processed):")
        print(f"🔍 Processed namespaces: {sorted(processed_namespaces)}")
        
        sorted_results = sorted(namespace_results, key=lambda x: x["efficiency"], reverse=True)
        
        print("🏆 Top 3 most efficient network slices:")
        for i, result in enumerate(sorted_results[:3], 1):
            print(f"   {i}. {result['namespace']}: {result['efficiency']:.3f} KB/sec/W ({result['efficiency_class']})")
        
        efficiencies = [r["efficiency"] for r in namespace_results]
        avg_efficiency = sum(efficiencies) / len(efficiencies)
        max_efficiency = max(efficiencies)
        min_efficiency = min(efficiencies)
        
        print(f"📈 Average Efficiency: {avg_efficiency:.3f} KB/sec/W")
        print(f"🎯 Best: {max_efficiency:.3f}, Worst: {min_efficiency:.3f} KB/sec/W")
    else:
        print("⚠️ No valid network slice efficiency data calculated")

def get_prometheus_range_average(query, hours_ago_start, hours_ago_end):
    try:
        now = datetime.now()
        start_time = now - timedelta(hours=hours_ago_start)
        end_time = now - timedelta(hours=hours_ago_end)
        
        params = {
            "query": query,
            "start": start_time.timestamp(),
            "end": end_time.timestamp(),
            "step": "60s"
        }
        
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success" and data["data"]["result"]:
            values = data["data"]["result"][0].get("values", [])
            if values:
                total = sum(float(val[1]) for val in values)
                return total / len(values)
        
        return 0
        
    except Exception as e:
        print(f"Error getting range average: {e}")
        return 0

def calculate_energy_reduction_percentage(metric_name, pod_name=None, namespace=None):
    try:
        if pod_name and namespace:
            query = f'{metric_name}{{pod="{pod_name}", namespace="{namespace}"}}'
        else:
            query = metric_name
        
        old_consumption = get_prometheus_range_average(query, 2, 1)
        new_consumption = get_prometheus_range_average(query, 1, 0)
        
        if old_consumption > 0:
            reduction_percentage = ((old_consumption - new_consumption) / old_consumption) * 100
            return reduction_percentage
        else:
            return 0
            
    except Exception as e:
        print(f"Error calculating energy reduction: {e}")
        return 0

def update_energy_reduction_metrics():
    global energy_reduction_metrics
    
    print("🔄 Updating Energy Reduction metrics...")
    
    cluster_metric_name = "energy_consumption_reduction_cluster"
    if cluster_metric_name not in energy_reduction_metrics:
        energy_reduction_metrics[cluster_metric_name] = Gauge(
            cluster_metric_name,
            "Energy consumption reduction percentage for the entire cluster (%) - (Old-New)/Old*100"
        )
    
    try:
        cluster_reduction = calculate_energy_reduction_percentage("server_energy_consumption")
        energy_reduction_metrics[cluster_metric_name].set(cluster_reduction)
        print(f"Updated {cluster_metric_name} = {cluster_reduction:.4f}%")
    except Exception as e:
        print(f"Error updating cluster energy reduction: {e}")
        energy_reduction_metrics[cluster_metric_name].set(0)
    
    pod_metric_name = "energy_consumption_reduction_by_pod"
    if pod_metric_name not in energy_reduction_metrics:
        energy_reduction_metrics[pod_metric_name] = Gauge(
            pod_metric_name,
            "Energy consumption reduction percentage by pod (%) - (Old-New)/Old*100",
            ["pod", "namespace"]
        )
    
    pods = fetch_running_pods()
    
    important_namespaces = ["rating", "monitoring", "default"]
    filtered_pods = [p for p in pods if p["namespace"] in important_namespaces]
    
    for pod_info in filtered_pods[:15]:
        pod_name = pod_info["pod"]
        namespace = pod_info["namespace"]
        
        try:
            pod_reduction = calculate_energy_reduction_percentage(
                "server_energy_consumption_by_pod", 
                pod_name, 
                namespace
            )
            
            energy_reduction_metrics[pod_metric_name].labels(
                pod=pod_name, 
                namespace=namespace
            ).set(pod_reduction)
            
            print(f"Updated {pod_metric_name} for {namespace}/{pod_name} = {pod_reduction:.4f}%")
            
        except Exception as e:
            print(f"Error updating pod energy reduction for {namespace}/{pod_name}: {e}")
            energy_reduction_metrics[pod_metric_name].labels(
                pod=pod_name, 
                namespace=namespace
            ).set(0)

def calculate_carbon_reduction_percentage(metric_name, pod_name=None, namespace=None):
    try:
        if pod_name and namespace:
            query = f'{metric_name}{{pod="{pod_name}", namespace="{namespace}"}}'
        else:
            query = metric_name
        
        old_emissions = get_prometheus_range_average(query, 2, 1)
        new_emissions = get_prometheus_range_average(query, 1, 0)
        
        if old_emissions > 0:
            reduction_percentage = ((old_emissions - new_emissions) / old_emissions) * 100
            return reduction_percentage
        else:
            return 0
            
    except Exception as e:
        print(f"Error calculating carbon reduction: {e}")
        return 0

def get_available_carbon_metrics():
    carbon_metrics = [
        "carbon_simulation_de",
        "carbon_simulation_it", 
        "carbon_simulation_fr",
        "carbon_simulation_eu"
    ]
    
    return carbon_metrics

def update_carbon_reduction_metrics():
    global carbon_reduction_metrics
    
    print("🌱 Updating Carbon Emission Reduction metrics...")
    
    carbon_metrics = get_available_carbon_metrics()
    
    for base_carbon_metric in carbon_metrics:
        try:
            test_response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", 
                                       params={"query": base_carbon_metric})
            test_data = test_response.json()
            
            if test_data["status"] != "success" or not test_data["data"]["result"]:
                print(f"⚠️  Skipping {base_carbon_metric} - no cluster data")
                continue
                
        except Exception as e:
            print(f"⚠️  Skipping {base_carbon_metric} - error: {e}")
            continue
        
        cluster_metric_name = f"carbon_emission_reduction_{base_carbon_metric.replace('carbon_simulation_', '')}"
        cluster_metric_name = sanitize_metric_name(cluster_metric_name)
        
        if cluster_metric_name not in carbon_reduction_metrics:
            carbon_reduction_metrics[cluster_metric_name] = Gauge(
                cluster_metric_name,
                f"Carbon emission reduction percentage for {base_carbon_metric} cluster (%) - (Old-New)/Old*100"
            )
        
        try:
            cluster_reduction = calculate_carbon_reduction_percentage(base_carbon_metric)
            carbon_reduction_metrics[cluster_metric_name].set(cluster_reduction)
            print(f"Updated {cluster_metric_name} = {cluster_reduction:.4f}%")
        except Exception as e:
            print(f"Error updating cluster carbon reduction for {base_carbon_metric}: {e}")
            carbon_reduction_metrics[cluster_metric_name].set(0)
        
        pod_carbon_metric = f"{base_carbon_metric}_by_pod"
        
        try:
            test_response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", 
                                       params={"query": pod_carbon_metric})
            test_data = test_response.json()
            
            if test_data["status"] != "success" or not test_data["data"]["result"]:
                print(f"⚠️  No pod data for {pod_carbon_metric}")
                continue
                
        except Exception as e:
            print(f"⚠️  Pod metric {pod_carbon_metric} error: {e}")
            continue
        
        pod_metric_name = f"carbon_emission_reduction_{base_carbon_metric.replace('carbon_simulation_', '')}_by_pod"
        pod_metric_name = sanitize_metric_name(pod_metric_name)
        
        if pod_metric_name not in carbon_reduction_metrics:
            carbon_reduction_metrics[pod_metric_name] = Gauge(
                pod_metric_name,
                f"Carbon emission reduction percentage by pod for {base_carbon_metric} (%) - (Old-New)/Old*100",
                ["pod", "namespace"]
            )
        
        pods = fetch_running_pods()
        important_namespaces = ["rating", "monitoring", "default"]
        filtered_pods = [p for p in pods if p["namespace"] in important_namespaces]
        
        for pod_info in filtered_pods[:10]:
            pod_name = pod_info["pod"]
            namespace = pod_info["namespace"]
            
            try:
                pod_reduction = calculate_carbon_reduction_percentage(
                    pod_carbon_metric, 
                    pod_name, 
                    namespace
                )
                
                carbon_reduction_metrics[pod_metric_name].labels(
                    pod=pod_name, 
                    namespace=namespace
                ).set(pod_reduction)
                
                print(f"Updated {pod_metric_name} for {namespace}/{pod_name} = {pod_reduction:.4f}%")
                
            except Exception as e:
                print(f"Error updating pod carbon reduction for {namespace}/{pod_name}: {e}")
                carbon_reduction_metrics[pod_metric_name].labels(
                    pod=pod_name, 
                    namespace=namespace
                ).set(0)

def get_prometheus_range_average_minutes(query, minutes_ago_start, minutes_ago_end):
    try:
        now = datetime.now()
        start_time = now - timedelta(minutes=minutes_ago_start)
        end_time = now - timedelta(minutes=minutes_ago_end)
        
        params = {
            "query": query,
            "start": start_time.timestamp(),
            "end": end_time.timestamp(),
            "step": "10s"
        }
        
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success" and data["data"]["result"]:
            values = data["data"]["result"][0].get("values", [])
            if values:
                total = sum(float(val[1]) for val in values)
                return total / len(values)
        
        return 0
        
    except Exception as e:
        print(f"Error getting range average (minutes): {e}")
        return 0

def calculate_energy_performance_index(metric_name, pod_name=None, namespace=None):
    try:
        if pod_name and namespace:
            query = f'{metric_name}{{pod="{pod_name}", namespace="{namespace}"}}'
        else:
            query = metric_name
        
        actual_consumption = get_prometheus_range_average_minutes(query, 1, 0)
        expected_consumption = get_prometheus_range_average_minutes(query, 2, 1)
        
        if expected_consumption > 0:
            performance_index = actual_consumption / expected_consumption
            return performance_index
        else:
            return 1.0
            
    except Exception as e:
        print(f"Error calculating energy performance index: {e}")
        return 1.0

def update_energy_performance_index_metrics():
    global energy_performance_metrics
    
    print("⚡ Updating Energy Performance Index metrics...")
    
    cluster_metric_name = "energy_performance_index_per_minute_cluster"
    if cluster_metric_name not in energy_performance_metrics:
        energy_performance_metrics[cluster_metric_name] = Gauge(
            cluster_metric_name,
            "Energy Performance Index per minute for the entire cluster (Actual/Expected) - >1 = degradation, <1 = improvement"
        )
    
    try:
        cluster_performance = calculate_energy_performance_index("server_energy_consumption")
        energy_performance_metrics[cluster_metric_name].set(cluster_performance)
        
        if cluster_performance > 1.05:
            status = "DÉGRADATION"
        elif cluster_performance < 0.95:
            status = "AMÉLIORATION"
        else:
            status = "STABLE"
            
        print(f"Updated {cluster_metric_name} = {cluster_performance:.6f} ({status})")
    except Exception as e:
        print(f"Error updating cluster energy performance index: {e}")
        energy_performance_metrics[cluster_metric_name].set(1.0)
    
    pod_metric_name = "energy_performance_index_per_minute_by_pod"
    if pod_metric_name not in energy_performance_metrics:
        energy_performance_metrics[pod_metric_name] = Gauge(
            pod_metric_name,
            "Energy Performance Index per minute by pod (Actual/Expected) - >1 = degradation, <1 = improvement",
            ["pod", "namespace"]
        )
    
    pods = fetch_running_pods()
    
    important_namespaces = ["rating", "monitoring", "default"]
    filtered_pods = [p for p in pods if p["namespace"] in important_namespaces]
    
    for pod_info in filtered_pods[:15]:
        pod_name = pod_info["pod"]
        namespace = pod_info["namespace"]
        
        try:
            pod_performance = calculate_energy_performance_index(
                "server_energy_consumption_by_pod", 
                pod_name, 
                namespace
            )
            
            energy_performance_metrics[pod_metric_name].labels(
                pod=pod_name, 
                namespace=namespace
            ).set(pod_performance)
            
            if pod_performance > 1.05:
                status = "↗️"
            elif pod_performance < 0.95:
                status = "↘️"
            else:
                status = "➡️"
            
            print(f"Updated {pod_metric_name} for {namespace}/{pod_name} = {pod_performance:.6f} {status}")
            
        except Exception as e:
            print(f"Error updating pod energy performance index for {namespace}/{pod_name}: {e}")
            energy_performance_metrics[pod_metric_name].labels(
                pod=pod_name, 
                namespace=namespace
            ).set(1.0)

def get_prometheus_max_value_in_range(query, hours_back):
    try:
        now = datetime.now()
        start_time = now - timedelta(hours=hours_back)
        end_time = now
        
        params = {
            "query": query,
            "start": start_time.timestamp(),
            "end": end_time.timestamp(),
            "step": "60s"
        }
        
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success" and data["data"]["result"]:
            values = data["data"]["result"][0].get("values", [])
            if values:
                max_value = max(float(val[1]) for val in values)
                return max_value
        
        return 0
        
    except Exception as e:
        print(f"Error getting max value in range: {e}")
        return 0

def calculate_capacity_utilization_rate(metric_name, pod_name=None, namespace=None):
    try:
        if pod_name and namespace:
            query = f'{metric_name}{{pod="{pod_name}", namespace="{namespace}"}}'
        else:
            query = metric_name
        
        actual_energy = get_prometheus_current_value(query)
        
        max_possible_energy = get_prometheus_max_value_in_range(query, 3)
        
        if max_possible_energy > 0:
            utilization_rate = (actual_energy / max_possible_energy) * 100
            return utilization_rate
        else:
            return 0.0
            
    except Exception as e:
        print(f"Error calculating capacity utilization rate: {e}")
        return 0.0

def update_capacity_utilization_rate_metrics():
    global capacity_utilization_metrics
    
    print("📊 Updating Capacity Utilization Rate metrics...")
    
    cluster_metric_name = "capacity_utilization_rate_cluster"
    if cluster_metric_name not in capacity_utilization_metrics:
        capacity_utilization_metrics[cluster_metric_name] = Gauge(
            cluster_metric_name,
            "Capacity Utilization Rate for the entire cluster (%) - Current/Max*100 over 3h window"
        )
    
    try:
        cluster_utilization = calculate_capacity_utilization_rate("server_energy_consumption")
        capacity_utilization_metrics[cluster_metric_name].set(cluster_utilization)
        
        if cluster_utilization >= 90:
            status = "HIGH LOAD"
        elif cluster_utilization >= 70:
            status = "MODERATE"
        elif cluster_utilization >= 50:
            status = "NORMAL"
        else:
            status = "LOW LOAD"
            
        print(f"Updated {cluster_metric_name} = {cluster_utilization:.2f}% ({status})")
    except Exception as e:
        print(f"Error updating cluster capacity utilization rate: {e}")
        capacity_utilization_metrics[cluster_metric_name].set(0)
    
    pod_metric_name = "capacity_utilization_rate_by_pod"
    if pod_metric_name not in capacity_utilization_metrics:
        capacity_utilization_metrics[pod_metric_name] = Gauge(
            pod_metric_name,
            "Capacity Utilization Rate by pod (%) - Current/Max*100 over 3h window",
            ["pod", "namespace"]
        )
    
    pods = fetch_running_pods()
    
    important_namespaces = ["rating", "monitoring", "default"]
    filtered_pods = [p for p in pods if p["namespace"] in important_namespaces]
    
    for pod_info in filtered_pods[:15]:
        pod_name = pod_info["pod"]
        namespace = pod_info["namespace"]
        
        try:
            pod_utilization = calculate_capacity_utilization_rate(
                "server_energy_consumption_by_pod", 
                pod_name, 
                namespace
            )
            
            capacity_utilization_metrics[pod_metric_name].labels(
                pod=pod_name, 
                namespace=namespace
            ).set(pod_utilization)
            
            if pod_utilization >= 90:
                status = "🔥"
            elif pod_utilization >= 70:
                status = "⚠️"
            elif pod_utilization >= 50:
                status = "✅"
            else:
                status = "📉"
            
            print(f"Updated {pod_metric_name} for {namespace}/{pod_name} = {pod_utilization:.2f}% {status}")
            
        except Exception as e:
            print(f"Error updating pod capacity utilization rate for {namespace}/{pod_name}: {e}")
            capacity_utilization_metrics[pod_metric_name].labels(
                pod=pod_name, 
                namespace=namespace
            ).set(0)

def create_pod_specific_promql_direct(metric_name, spec, pod_name, namespace):
    if "carbon_simulation" in metric_name or "carbon-simulation" in metric_name:
        price = spec.get("price", "0.253")
        
        promql = f'''
        (
          (sum(container_memory_usage_bytes{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}}) or vector(0)) / (1024*1024*1024) +
          (sum(rate(container_cpu_usage_seconds_total{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}}[5m])) or vector(0)) +
          0.1
        ) * 220 / 1000 * {price}
        '''
    
    elif "server_energy" in metric_name or "server-energy" in metric_name:
        promql = f'''
        (
          25 + 
          100 * (sum(rate(container_cpu_usage_seconds_total{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}}[5m])) or vector(0)) + 
          3 * (sum(container_memory_usage_bytes{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}}) or vector(0)) / (8 * 1024*1024*1024) + 
          2 + 
          6 * ((sum(rate(container_cpu_usage_seconds_total{{pod="{pod_name}", namespace="{namespace}", container!="POD", container!=""}}[5m])) or vector(0)) * 0.1) + 
          5 + 
          10 * ((sum(rate(container_network_transmit_bytes_total{{pod="{pod_name}", namespace="{namespace}"}}[5m])) or vector(0)) + 
                (sum(rate(container_network_receive_bytes_total{{pod="{pod_name}", namespace="{namespace}"}}[5m])) or vector(0))) / (100 * 1024 * 1024) + 
          15
        ) / 0.92
        '''
    
    else:
        base_metric = metric_name.replace("_by_pod", "").replace("-", "_")
        promql = f'''
        (
          scalar({base_metric}) * 
          kube_pod_info{{pod="{pod_name}",namespace="{namespace}"}} / 
          scalar(count(kube_pod_info))
        )
        '''
    
    return promql.strip().replace('\n', ' ').replace('  ', ' ')

def update_regular_metrics():
    global regular_metrics
    instance_data_list = fetch_instances_from_api()

    for item in instance_data_list:
        metric_name = item["metric_name"]
        spec = item["spec"]
        
        promql = spec.get("metric", "")
        promql = promql.replace("\\", "")
        if not promql:
            continue
            
        replacements = {
            "{price}": spec.get("price", "0"),
            "{memory}": spec.get("memory", "1"),
            "{cpu}": spec.get("cpu", "1"),
        }

        for placeholder, value in replacements.items():
            promql = promql.replace(placeholder, str(value))
        
        sanitized_metric_name = sanitize_metric_name(metric_name)
        
        if sanitized_metric_name not in regular_metrics:
            regular_metrics[sanitized_metric_name] = Gauge(
                sanitized_metric_name, f"Cluster-level rating metric for {metric_name}"
            )

        try:
            prometheus_response = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": promql},
            )
            prometheus_response.raise_for_status()
            prometheus_data = prometheus_response.json()

            value = extract_prometheus_value(prometheus_data)
            
            if value is not None:
                regular_metrics[sanitized_metric_name].set(value)
                print(f"Updated cluster {sanitized_metric_name} = {value}")
            else:
                regular_metrics[sanitized_metric_name].set(0)
                
        except Exception as e:
            print(f"Error updating metric {metric_name}: {e}")
            regular_metrics[sanitized_metric_name].set(0)

def update_pod_metrics():
    global pod_metrics
    
    instance_data_list = fetch_instances_from_api()
    pods = fetch_running_pods()
    
    print(f"Creating VALIDATED pod metrics for {len(pods)} pods and {len(instance_data_list)} metric types")
    
    for item in instance_data_list:
        metric_name = item["metric_name"]
        spec = item["spec"]
        
        original_promql = spec.get("metric", "")
        original_promql = original_promql.replace("\\", "")
        if not original_promql:
            continue
            
        replacements = {
            "{price}": spec.get("price", "0"),
            "{memory}": spec.get("memory", "1"),
            "{cpu}": spec.get("cpu", "1"),
        }

        for placeholder, value in replacements.items():
            original_promql = original_promql.replace(placeholder, str(value))
        
        sanitized_metric_name = sanitize_metric_name(f"{metric_name}_by_pod")
        
        if sanitized_metric_name not in pod_metrics:
            pod_metrics[sanitized_metric_name] = Gauge(
                sanitized_metric_name, 
                f"Pod-specific rating metric for {metric_name} (DIRECT calculation)",
                ["pod", "namespace"]
            )

        for pod_info in pods:
            pod_name = pod_info["pod"]
            namespace = pod_info["namespace"]
            
            try:
                pod_promql = create_pod_specific_promql_direct(metric_name, spec, pod_name, namespace)
                
                if "ubuntu-rdp" in pod_name and namespace == "ubi":
                    print(f"DEBUG: VALIDATED PromQL for {pod_name}: {pod_promql}")
                
                prometheus_response = requests.get(
                    f"{PROMETHEUS_URL}/api/v1/query",
                    params={"query": pod_promql},
                )
                prometheus_response.raise_for_status()
                prometheus_data = prometheus_response.json()

                if "ubuntu-rdp" in pod_name and namespace == "ubi":
                    print(f"DEBUG: VALIDATED Response for {pod_name}: {prometheus_data}")

                value = extract_prometheus_value(prometheus_data)
                
                if value is not None and value > 0:
                    pod_metrics[sanitized_metric_name].labels(pod=pod_name, namespace=namespace).set(value)
                    print(f"Updated VALIDATED pod {metric_name} for {namespace}/{pod_name} = {value:.6f}")
                else:
                    pod_metrics[sanitized_metric_name].labels(pod=pod_name, namespace=namespace).set(0)
                    if "ubuntu-rdp" in pod_name and namespace == "ubi":
                        print(f"DEBUG: Zero value for {pod_name}, value was: {value}")
                    
            except Exception as e:
                print(f"Error updating DIRECT pod metric {metric_name} for {namespace}/{pod_name}: {e}")
                pod_metrics[sanitized_metric_name].labels(pod=pod_name, namespace=namespace).set(0)

if __name__ == "__main__":
    start_http_server(8000)
    print("Custom metrics server started on port 8000")
    print("Exposing cluster-level, pod-specific, Energy Reduction, Carbon Reduction, Energy Performance, Capacity Utilization, Network Slice Energy Efficiency, and Energy Efficiency (Resource Utilization) Rating metrics")

    while True:
        print(f"\n--- Updating metrics at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        
        print("1. Updating cluster-level Rating metrics...")
        update_regular_metrics()
        
        print("2. Updating VALIDATED pod-specific Rating metrics...")
        update_pod_metrics()
        
        print("3. Updating Energy Reduction metrics...")
        update_energy_reduction_metrics()
        
        print("4. Updating Carbon Emission Reduction metrics...")
        update_carbon_reduction_metrics()
        
        print("5. Updating Energy Performance Index metrics...")
        update_energy_performance_index_metrics()
        
        print("6. Updating Capacity Utilization Rate metrics...")
        update_capacity_utilization_rate_metrics()
        
        print("7. Updating Network Slice Energy Efficiency metrics...")
        update_network_slice_metrics()
        
        print("8. Updating Energy Efficiency (Resource Utilization) metrics...")
        update_energy_efficiency_metrics()
        
        time.sleep(60)