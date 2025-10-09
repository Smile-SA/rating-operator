# Rating Rules Documentation

## Available Rating Metrics
### Energy Consumption Metrics

| Metric | Description |
|--------|-------------|
| `energy-consumption` | Calculates realistic server energy consumption in watts considering CPU, memory, disk and network usage. Formula based on: base consumption (25W) + dynamic CPU + memory + disk + network + overhead, divided by energy efficiency (92%) |
| `energy_consumption_by_pod` | Calculates realistic energy consumption per specific pod in watts. Uses container metrics for CPU, memory and network of the given pod. Allows energy consumption attribution at pod granular level |

### Carbon Simulation Metrics

| Metric | Description | Carbon coefficent (kgCO2eq/kWh) |
|--------|-------------|---------------------|
| `carbon-simulation-de` | Calculates carbon footprint for Germany in kg CO2 based on memory, CPU and storage usage. Formula: (memory_GB + CPU_cores + storage_GB) × 220g CO2/kWh × DE_carbon_coefficient | 0.253 |
| `carbon-simulation-eu` | Calculates carbon footprint for Europe (average) in kg CO2 using the same model as Germany but with European average carbon coefficient | 0.238 |
| `carbon-simulation-fr` | Calculates carbon footprint for France in kg CO2.  | 0.28 |
| `carbon-simulation-it` | Calculates carbon footprint for Italy in kg CO2.  | 0.297 |
| `carbon_simulation_de_by_pod` | Calculates carbon footprint per specific pod in Germany. Simplified formula: (pod_memory_GB + pod_CPU_usage + 0.1_overhead) × 220g_CO2/kWh × DE_coefficient | 0.253 |
| `carbon_simulation_fr_by_pod` | Calculates carbon footprint per specific pod in France | 0.28 |
| `carbon_simulation_it_by_pod` | Calculates carbon footprint per specific pod in Italy  | 0.297 |
| `carbon_simulation_eu_by_pod` | Calculates carbon footprint per specific pod for Europe  | 0.238 |

## Legacy Metrics (API v2)
These metrics were originally created using API v2 but remain available in the current API v3 for backward compatibility.
### Node Cost Simulation Metrics

#### Azure AKS
| Metric | Description | Instance Type | CPU | Memory | Price ($/h) |
|--------|-------------|---------------|-----|--------|-------------|
| `node_cost_simulation_aks_a8` | Calculates node cost simulation for Azure AKS A8 instance. Uses max(memory_ratio/memory_limit, cpu_ratio/cpu_limit) to determine resource utilization multiplied by hourly cost | A8 | 8 vCPU | 16 GB | 0.4000 |
| `node_cost_simulation_aks_b1ms` | Calculates node cost simulation for Azure AKS B1ms instance (burstable performance) | B1ms | 1 vCPU | 2 GB | 0.0250 |
| `node_cost_simulation_aks_b1s` | Calculates node cost simulation for Azure AKS B1s instance (burstable performance) | B1s | 1 vCPU | 1 GB | 0.0125 |
| `node_cost_simulation_aks_b2ms` | Calculates node cost simulation for Azure AKS B2ms instance (burstable performance) | B2ms | 2 vCPU | 8 GB | 0.0998 |
| `node_cost_simulation_aks_b2s` | Calculates node cost simulation for Azure AKS B2s instance (burstable performance) | B2s | 2 vCPU | 4 GB | 0.0499 |
| `node_cost_simulation_aks_b4ms` | Calculates node cost simulation for Azure AKS B4ms instance (burstable performance) | B4ms | 4 vCPU | 16 GB | 0.2000 |

#### AWS
| Metric | Description | Instance Type | CPU | Memory | Price ($/h) |
|--------|-------------|---------------|-----|--------|-------------|
| `node_cost_simulation_aws_a1_2_xlarge` | Calculates node cost simulation for AWS A1.2xlarge instance (ARM-based Graviton processor) | a1.2xlarge | 8 vCPU | 16 GB | 0.204 |
| `node_cost_simulation_aws_a1_large` | Calculates node cost simulation for AWS A1.large instance (ARM-based Graviton processor) | a1.large | 2 vCPU | 4 GB | 0.051 |
| `node_cost_simulation_aws_a1_medium` | Calculates node cost simulation for AWS A1.medium instance (ARM-based Graviton processor) | a1.medium | 1 vCPU | 2 GB | 0.0255 |
| `node_cost_simulation_aws_a1_xlarge` | Calculates node cost simulation for AWS A1.xlarge instance (ARM-based Graviton processor) | a1.xlarge | 4 vCPU | 8 GB | 0.102 |
| `node_cost_simulation_aws_m6g_large` | Calculates node cost simulation for AWS M6g.large instance (ARM-based Graviton2 processor) | m6g.large | 2 vCPU | 8 GB | 0.077 |
| `node_cost_simulation_aws_m6g_medium` | Calculates node cost simulation for AWS M6g.medium instance (ARM-based Graviton2 processor) | m6g.medium | 1 vCPU | 4 GB | 0.0385 |
| `node_cost_simulation_aws_t4g_micro` | Calculates node cost simulation for AWS T4g.micro instance (burstable ARM-based Graviton2) | t4g.micro | 2 vCPU | 1 GB | 0.0084 |
| `node_cost_simulation_aws_t4g_nano` | Calculates node cost simulation for AWS T4g.nano instance (burstable ARM-based Graviton2) | t4g.nano | 2 vCPU | 0.5 GB | 0.0042 |

#### Google Cloud Platform
| Metric | Description | Instance Type | CPU | Memory | Price ($/h) |
|--------|-------------|---------------|-----|--------|-------------|
| `node_cost_simulation_gcp_c2_standard_4` | Calculates node cost simulation for GCP C2-standard-4 instance (compute-optimized) | c2-standard-4 | 4 vCPU | 16 GB | 0.2088 |
| `node_cost_simulation_gcp_c2_standard_8` | Calculates node cost simulation for GCP C2-standard-8 instance (compute-optimized) | c2-standard-8 | 8 vCPU | 32 GB | 0.4176 |
| `node_cost_simulation_gcp_e2_highcpu_4` | Calculates node cost simulation for GCP E2-highcpu-4 instance (high CPU, low memory) | e2-highcpu-4 | 4 vCPU | 4 GB | 0.09894 |
| `node_cost_simulation_gcp_e2_highmem_2` | Calculates node cost simulation for GCP E2-highmem-2 instance (high memory, low CPU) | e2-highmem-2 | 2 vCPU | 16 GB | 0.0904 |
| `node_cost_simulation_gcp_e2_large` | Calculates node cost simulation for GCP E2-large instance (balanced resources) | e2-large | 2 vCPU | 8 GB | 0.067 |
| `node_cost_simulation_gcp_e2_medium` | Calculates node cost simulation for GCP E2-medium instance (general purpose) | e2-medium | 1 vCPU | 4 GB | 0.0355 |
| `node_cost_simulation_gcp_e2_micro` | Calculates node cost simulation for GCP E2-micro instance (shared-core) | e2-micro | 1 vCPU | 1 GB | 0.0084 |
| `node_cost_simulation_gcp_e2_xlarge` | Calculates node cost simulation for GCP E2-xlarge instance (balanced resources) | e2-xlarge | 4 vCPU | 16 GB | 0.134 |

### Number of Instance Simulation Metrics

#### Azure AKS
| Metric | Description | Instance Type | CPU | Memory |
|--------|-------------|---------------|-----|--------|
| `number_instance_simulation_aks_a8` | Calculates number of A8 instances needed based on max(memory_requirement/16GB, cpu_requirement/8cores) | A8 | 8 vCPU | 16 GB |
| `number_instance_simulation_aks_b1ms` | Calculates number of B1ms instances needed based on max(memory_requirement/2GB, cpu_requirement/1core) | B1ms | 1 vCPU | 2 GB |
| `number_instance_simulation_aks_b1s` | Calculates number of B1s instances needed based on max(memory_requirement/1GB, cpu_requirement/1core) | B1s | 1 vCPU | 1 GB |
| `number_instance_simulation_aks_b2ms` | Calculates number of B2ms instances needed based on max(memory_requirement/8GB, cpu_requirement/2cores) | B2ms | 2 vCPU | 8 GB |
| `number_instance_simulation_aks_b2s` | Calculates number of B2s instances needed based on max(memory_requirement/4GB, cpu_requirement/2cores) | B2s | 2 vCPU | 4 GB |
| `number_instance_simulation_aks_b4ms` | Calculates number of B4ms instances needed based on max(memory_requirement/16GB, cpu_requirement/4cores) | B4ms | 4 vCPU | 16 GB |

#### AWS
| Metric | Description | Instance Type | CPU | Memory |
|--------|-------------|---------------|-----|--------|
| `number_instance_simulation_aws_a1_2_xlarge` | Calculates number of A1.2xlarge instances needed based on max(memory_requirement/16GB, cpu_requirement/8cores) | a1.2xlarge | 8 vCPU | 16 GB |
| `number_instance_simulation_aws_a1_large` | Calculates number of A1.large instances needed based on max(memory_requirement/4GB, cpu_requirement/2cores) | a1.large | 2 vCPU | 4 GB |
| `number_instance_simulation_aws_a1_medium` | Calculates number of A1.medium instances needed based on max(memory_requirement/2GB, cpu_requirement/1core) | a1.medium | 1 vCPU | 2 GB |
| `number_instance_simulation_aws_a1_xlarge` | Calculates number of A1.xlarge instances needed based on max(memory_requirement/8GB, cpu_requirement/4cores) | a1.xlarge | 4 vCPU | 8 GB |
| `number_instance_simulation_aws_m6g_large` | Calculates number of M6g.large instances needed based on max(memory_requirement/8GB, cpu_requirement/2cores) | m6g.large | 2 vCPU | 8 GB |
| `number_instance_simulation_aws_m6g_medium` | Calculates number of M6g.medium instances needed based on max(memory_requirement/4GB, cpu_requirement/1core) | m6g.medium | 1 vCPU | 4 GB |
| `number_instance_simulation_aws_t4g_micro` | Calculates number of T4g.micro instances needed based on max(memory_requirement/1GB, cpu_requirement/2cores) | t4g.micro | 2 vCPU | 1 GB |
| `number_instance_simulation_aws_t4g_nano` | Calculates number of T4g.nano instances needed based on max(memory_requirement/0.5GB, cpu_requirement/2cores) | t4g.nano | 2 vCPU | 0.5 GB |

#### Google Cloud Platform
| Metric | Description | Instance Type | CPU | Memory |
|--------|-------------|---------------|-----|--------|
| `number_instance_simulation_gcp_c2_standard_4` | Calculates number of C2-standard-4 instances needed based on max(memory_requirement/16GB, cpu_requirement/4cores) | c2-standard-4 | 4 vCPU | 16 GB |
| `number_instance_simulation_gcp_c2_standard_8` | Calculates number of C2-standard-8 instances needed based on max(memory_requirement/32GB, cpu_requirement/8cores) | c2-standard-8 | 8 vCPU | 32 GB |
| `number_instance_simulation_gcp_e2_highcpu_4` | Calculates number of E2-highcpu-4 instances needed based on max(memory_requirement/4GB, cpu_requirement/4cores) | e2-highcpu-4 | 4 vCPU | 4 GB |
| `number_instance_simulation_gcp_e2_highmem_2` | Calculates number of E2-highmem-2 instances needed based on max(memory_requirement/16GB, cpu_requirement/2cores) | e2-highmem-2 | 2 vCPU | 16 GB |
| `number_instance_simulation_gcp_e2_large` | Calculates number of E2-large instances needed based on max(memory_requirement/8GB, cpu_requirement/2cores) | e2-large | 2 vCPU | 8 GB |
| `number_instance_simulation_gcp_e2_medium` | Calculates number of E2-medium instances needed based on max(memory_requirement/4GB, cpu_requirement/1core) | e2-medium | 1 vCPU | 4 GB |
| `number_instance_simulation_gcp_e2_micro` | Calculates number of E2-micro instances needed based on max(memory_requirement/1GB, cpu_requirement/1core) | e2-micro | 1 vCPU | 1 GB |
| `number_instance_simulation_gcp_e2_xlarge` | Calculates number of E2-xlarge instances needed based on max(memory_requirement/16GB, cpu_requirement/4cores) | e2-xlarge | 4 vCPU | 16 GB |

### Node CPU/Memory Ratio Metrics

| Metric | Description |
|--------|-------------|
| `node_cpu_memory_ratio` | Calculates the CPU to memory utilization ratio per instance. Shows the relationship between CPU usage and memory usage for each node |
| `node_cpu_memory_ratio_advanced` | Advanced CPU to memory ratio calculation using average aggregation without instance labels. Provides a cluster-wide view of CPU/memory balance |
| `node_cpu_memory_ratio_evolution` | Tracks the evolution of CPU to memory ratio over 24 hours using rate functions. Shows trending patterns in resource utilization balance |

### Resource Usage Metrics

| Metric | Description |
|--------|-------------|
| `pods_usage_cpu` | Measures actual CPU usage by pods in CPU cores, combining container CPU usage with pod metadata to include node information |
| `pods_usage_memory` | Measures actual memory usage by pods in GB (divided by 10^10), combining container memory usage with pod metadata |
| `pods_request_cpu` | Tracks CPU resource requests by pods, showing the requested CPU cores per pod across namespaces and nodes |
| `pods_request_memory` | Tracks memory resource requests by pods in GB, showing requested memory per pod across namespaces and nodes |

### Storage and System Metrics

| Metric | Description |
|--------|-------------|
| `prometheus_oldest_data` | Returns the timestamp of the oldest data stored in Prometheus TSDB. Useful for data retention monitoring |
| `prometheus_storage_size` | Calculates total Prometheus storage size in GB by summing all TSDB storage blocks |
| `rating_storage_size` | Monitors the storage utilization percentage of the rating PostgreSQL database persistent volume |
| `tenant_storage_use` | Calculates actual storage usage per tenant in GB by measuring used storage across all persistent volume claims |
| `storage_ram_ratio` | Calculates the ratio between storage utilization percentage and memory utilization per node. Helps identify storage vs memory pressure correlation |


