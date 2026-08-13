import sys
import argparse
from occ.collectors.kernel_oom import OOMCollector
from occ.collectors.apache import ApacheStatusCollector

def main():
    parser = argparse.ArgumentParser(prog="occ-check", description="Server Emergency Diagnostics Tool")
    parser.add_argument("--traffic", action="store_true", help="Run traffic analysis")
    parser.add_argument("--last", type=str, default="15m", help="Time window")
    args, unknown = parser.parse_known_args()

    oom = OOMCollector().collect()
    apache = ApacheStatusCollector().collect()

    print("========================================================")
    print("OCC EMERGENCY DIAGNOSTICS")
    print("========================================================")
    print(f"[+] Kernel OOM Events Detected: {oom['count']}")
    if oom['count'] > 0:
        for event in oom['oom_events']:
            print(f"    - Killed PID {event['pid']} ({event['process']}) - Freed {event['rss_mb']} MB")
            
    print(f"[+] Apache Scoreboard Available: {apache['available']}")
    if apache['available']:
        print(f"    - Busy Workers: {apache['busy_workers']}")
        print(f"    - Exhausted: {apache['is_exhausted']}")
    print("========================================================")

if __name__ == "__main__":
    main()
