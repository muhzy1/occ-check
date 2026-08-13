import re
import subprocess

class OOMCollector:
    """Parses dmesg for kernel OOM-killer invocations."""
    
    OOM_PATTERN = re.compile(
        r'\[(?P<timestamp>[^\]]+)\]\s+Out of memory:\s+Killed process\s+(?P<pid>\d+)\s+\((?P<process>[^\)]+)\)\s+total-vm:(?P<vm>\d+)kB,\s+anon-rss:(?P<rss>\d+)kB'
    )

    def collect(self, window_minutes: int = 60) -> dict:
        findings = []
        try:
            raw_output = subprocess.check_output(
                ["dmesg", "-T"], stderr=subprocess.DEVNULL, text=True
            )
        except Exception:
            return {"oom_events": [], "count": 0}

        for line in raw_output.splitlines():
            if "Out of memory" in line or "killed process" in line.lower():
                match = self.OOM_PATTERN.search(line)
                if match:
                    data = match.groupdict()
                    findings.append({
                        "process": data["process"],
                        "pid": data["pid"],
                        "rss_mb": round(int(data["rss"]) / 1024, 2),
                        "total_vm_mb": round(int(data["vm"]) / 1024, 2),
                        "raw": line.strip()
                    })

        return {
            "oom_events": findings,
            "count": len(findings),
            "has_recent_oom": len(findings) > 0
        }
