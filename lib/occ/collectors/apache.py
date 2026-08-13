import urllib.request

class ApacheStatusCollector:
    """Parses mod_status auto-format page to diagnose worker exhaustion."""

    def collect(self, status_url: str = "http://127.0.0.1/server-status?auto") -> dict:
        try:
            req = urllib.request.Request(status_url, headers={"User-Agent": "occ-check/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                content = resp.read().decode('utf-8')
        except Exception as e:
            return {"available": False, "error": f"Failed to fetch mod_status: {e}"}

        stats = {}
        for line in content.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                stats[key.strip()] = val.strip()

        scoreboard = stats.get("Scoreboard", "")
        busy_workers = int(stats.get("BusyWorkers", 0))
        idle_workers = int(stats.get("IdleWorkers", 0))
        total_workers = busy_workers + idle_workers

        states = {
            "waiting": scoreboard.count("_"),
            "starting": scoreboard.count("S"),
            "reading": scoreboard.count("R"),
            "writing": scoreboard.count("W"),
            "keepalive": scoreboard.count("K"),
            "open_slots": scoreboard.count(".")
        }

        is_exhausted = states["open_slots"] == 0 and total_workers > 0

        return {
            "available": True,
            "busy_workers": busy_workers,
            "idle_workers": idle_workers,
            "worker_states": states,
            "is_exhausted": is_exhausted
        }
