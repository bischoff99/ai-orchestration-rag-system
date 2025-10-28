#!/usr/bin/env python3
"""
RAM Usage Monitor for Ollama Performance Testing
"""

import psutil
import time
import json
from datetime import datetime

def monitor_ram_usage(duration=60, interval=1, output_file=None):
    """Monitor RAM usage over time"""
    
    print(f"📊 Monitoring RAM usage for {duration} seconds...")
    print("Press Ctrl+C to stop early\n")
    
    start_time = time.time()
    ram_data = []
    
    try:
        while time.time() - start_time < duration:
            ram = psutil.virtual_memory()
            timestamp = datetime.now().isoformat()
            
            data = {
                "timestamp": timestamp,
                "elapsed_sec": time.time() - start_time,
                "ram_total_gb": ram.total / (1024**3),
                "ram_used_gb": ram.used / (1024**3),
                "ram_available_gb": ram.available / (1024**3),
                "ram_percent": ram.percent,
                "swap_used_gb": psutil.swap_memory().used / (1024**3)
            }
            
            ram_data.append(data)
            
            print(f"{data['elapsed_sec']"6.1f"}s | RAM: {data['ram_used_gb']"5.2f"}GB ({data['ram_percent']"5.1f"}%) | Available: {data['ram_available_gb']"5.2f"}GB")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
    
    # Save data
    if output_file:
        with open(output_file, 'w') as f:
            json.dump({
                "monitor_info": {
                    "start_time": ram_data[0]["timestamp"] if ram_data else None,
                    "end_time": ram_data[-1]["timestamp"] if ram_data else None,
                    "duration_sec": duration,
                    "interval_sec": interval
                },
                "ram_data": ram_data
            }, f, indent=2)
        print(f"\n💾 RAM data saved to: {output_file}")
    
    return ram_data

def analyze_ram_efficiency(ram_data):
    """Analyze RAM usage patterns"""
    if not ram_data:
        return {}
    
    used_values = [d["ram_used_gb"] for d in ram_data]
    percent_values = [d["ram_percent"] for d in ram_data]
    
    return {
        "avg_ram_used_gb": sum(used_values) / len(used_values),
        "max_ram_used_gb": max(used_values),
        "min_ram_used_gb": min(used_values),
        "avg_ram_percent": sum(percent_values) / len(percent_values),
        "max_ram_percent": max(percent_values),
        "ram_efficiency_score": (100 - (sum(percent_values) / len(percent_values))) / 100  # Higher is better
    }

if __name__ == "__main__":
    import sys
    
    duration = 60  # Default 60 seconds
    interval = 1   # Default 1 second
    output_file = "/Users/andrejsp/ai/benchmarks/performance/ram_monitor_latest.json"
    
    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
    if len(sys.argv) > 2:
        interval = float(sys.argv[2])
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    
    ram_data = monitor_ram_usage(duration, interval, output_file)
    analysis = analyze_ram_efficiency(ram_data)
    
    print("
📈 RAM Analysis:"    print(f"  Average RAM Used: {analysis.get('avg_ram_used_gb', 0):.2".2f"B")
    print(f"  Max RAM Used: {analysis.get('max_ram_used_gb', 0):.2".2f"B")
    print(f"  Average RAM %: {analysis.get('avg_ram_percent', 0):.1".1f")
    print(f"  Max RAM %: {analysis.get('max_ram_percent', 0):.1".1f")
    print(f"  Efficiency Score: {analysis.get('ram_efficiency_score', 0):.2".2f"
