from typing import Dict, Any, List
from occ_check.diagnosis.engine import Finding

def render_report(profile: Dict[str, Any], system: Dict[str, Any], traffic: Dict[str, Any], findings: List[Finding]):
    print("=" * 70)
    print("OCC SERVER INCIDENT REPORT")
    print("=" * 70)
    print("HOST      : {}".format(profile.get('hostname', 'unknown')))
    print("PANEL     : {}".format(profile.get('adapter', 'Generic')))
    print("CPU / MEM : {} vCPUs | {} GB RAM".format(system['cpu_cores'], system['mem_total_gb']))
    print("=" * 70)

    print("\n------------------------------------------------------------")
    print("PRIMARY FINDINGS")
    print("------------------------------------------------------------")
    if not findings:
        print("[OK] System healthy. No critical anomalies identified.")
    else:
        for f in findings:
            print("[{}] {}".format(f.severity, f.finding))
            print("Confidence : {}".format(f.confidence))
            print("Evidence   :")
            for ev in f.evidence:
                print("  - {}".format(ev))
            print()

    print("------------------------------------------------------------")
    print("RESOURCE SNAPSHOT")
    print("------------------------------------------------------------")
    print("Load Average : {}, {}, {} (Core Ratio: {})".format(system['load1'], system['load5'], system['load15'], system['load_ratio']))
    print("Memory Usage : {} GB / {} GB ({}%)".format(system['mem_used_gb'], system['mem_total_gb'], system['mem_pct']))
    print("Swap Usage   : {} GB".format(system['swap_used_gb']))

    print("\n------------------------------------------------------------")
    print("TRAFFIC FORENSICS (Window: Last 15 minutes)")
    print("------------------------------------------------------------")
    print("Total Reqs   : {} ({:.2f} req/sec)".format(traffic['total_requests'], traffic['rps']))
    print("\nTop Domains:")
    for dom, count in traffic['top_domains']:
        print("  {:6d}  {}".format(count, dom))

    print("\nTop IPs:")
    for ip, count in traffic['top_ips']:
        print("  {:6d}  {}".format(count, ip))

    print("\nTop URIs:")
    for uri, count in traffic['top_uris']:
        print("  {:6d}  {}".format(count, uri))

    print("\n============================================================")
    print("NO AUTOMATIC CHANGES WERE MADE (Read-Only Execution)")
    print("============================================================\n")
