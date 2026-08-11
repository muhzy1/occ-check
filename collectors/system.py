import os
from typing import Dict, Any

def collect_system_metrics() -> Dict[str, Any]:
    with open('/proc/loadavg', 'r') as f:
        parts = f.read().split()
        load1, load5, load15 = float(parts[0]), float(parts[1]), float(parts[2])

    cpu_cores = 0
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line.startswith('processor'):
                cpu_cores += 1
    cpu_cores = max(1, cpu_cores)

    mem_info = {}
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                val = int(parts[1].split()[0])
                mem_info[key] = val

    total_mem = mem_info.get('MemTotal', 1)
    free_mem = mem_info.get('MemAvailable', mem_info.get('MemFree', 0))
    used_mem = total_mem - free_mem
    
    swap_total = mem_info.get('SwapTotal', 0)
    swap_free = mem_info.get('SwapFree', 0)
    swap_used = swap_total - swap_free

    return {
        "load1": load1,
        "load5": load5,
        "load15": load15,
        "cpu_cores": cpu_cores,
        "load_ratio": round(load1 / cpu_cores, 2),
        "mem_total_gb": round(total_mem / 1024 / 1024, 2),
        "mem_used_gb": round(used_mem / 1024 / 1024, 2),
        "mem_pct": round((used_mem / total_mem) * 100, 1),
        "swap_used_gb": round(swap_used / 1024 / 1024, 2),
    }
