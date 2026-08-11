from typing import Dict, Any, List

class Finding:
    def __init__(self, category: str, severity: str, finding: str, evidence: List[str], confidence: str):
        self.category = category
        self.severity = severity
        self.finding = finding
        self.evidence = evidence
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity,
            "finding": self.finding,
            "evidence": self.evidence,
            "confidence": self.confidence
        }

def diagnose(system_data: Dict[str, Any], traffic_data: Dict[str, Any]) -> List[Finding]:
    findings = []

    load_ratio = system_data.get('load_ratio', 0)
    xmlrpc_hits = sum(traffic_data.get('wp_stats', {}).get('/xmlrpc.php', {}).values())
    total_reqs = traffic_data.get('total_requests', 1)

    if load_ratio > 2.0 and xmlrpc_hits > 1000:
        evidence = [
            "Load average: {} on {} vCPUs".format(system_data['load1'], system_data['cpu_cores']),
            "XML-RPC requests in window: {} ({}% of total traffic)".format(
                xmlrpc_hits, round((xmlrpc_hits / max(1, total_reqs)) * 100, 1)
            ),
            "Top XML-RPC Source IP: {}".format(
                list(traffic_data['wp_stats']['/xmlrpc.php'].keys())[0] if traffic_data['wp_stats']['/xmlrpc.php'] else "Unknown"
            )
        ]
        findings.append(Finding(
            category="traffic_wp_attack",
            severity="CRITICAL",
            finding="High-volume WordPress XML-RPC abuse driving system load",
            evidence=evidence,
            confidence="HIGH"
        ))

    if system_data.get('mem_pct', 0) > 90.0:
        findings.append(Finding(
            category="resource_memory",
            severity="CRITICAL" if system_data.get('swap_used_gb', 0) > 2.0 else "WARNING",
            finding="Memory saturation detected with active swapping",
            evidence=[
                "RAM Used: {}GB / {}GB ({}%)".format(system_data['mem_used_gb'], system_data['mem_total_gb'], system_data['mem_pct']),
                "Swap Used: {}GB".format(system_data['swap_used_gb'])
            ],
            confidence="HIGH"
        ))

    return findings
