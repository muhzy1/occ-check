import sys
import argparse
import socket
from occ_check.adapters.cpanel import CPanelAdapter
from occ_check.adapters.plesk import PleskAdapter
from occ_check.adapters.generic import GenericLinuxAdapter
from occ_check.collectors.system import collect_system_metrics
from occ_check.traffic.window import parse_time_window
from occ_check.traffic.analyzer import analyze_logs
from occ_check.diagnosis.engine import diagnose
from occ_check.reporting.text import render_report

def main():
    parser = argparse.ArgumentParser(description="OCC Server Incident Forensic Engine")
    parser.add_argument("--traffic", action="store_true", help="Force traffic engine execution")
    parser.add_argument("--last", type=str, default="15m", help="Time window (e.g. 5m, 15m, 1h)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    adapters = [CPanelAdapter(), PleskAdapter(), GenericLinuxAdapter()]
    selected_adapter = None
    for adapter in adapters:
        if adapter.detect():
            selected_adapter = adapter
            break

    profile = {
        "hostname": socket.gethostname(),
        "adapter": selected_adapter.name()
    }

    system_metrics = collect_system_metrics()
    start_ts, end_ts = parse_time_window(last_str=args.last)
    log_sources = selected_adapter.get_log_sources()
    traffic_metrics = analyze_logs(log_sources, start_ts, end_ts)

    findings = diagnose(system_metrics, traffic_metrics)
    render_report(profile, system_metrics, traffic_metrics, findings)

    has_critical = any(f.severity == "CRITICAL" for f in findings)
    sys.exit(2 if has_critical else 0)

if __name__ == "__main__":
    main()
