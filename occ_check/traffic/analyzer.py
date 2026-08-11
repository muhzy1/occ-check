from collections import Counter, defaultdict
from typing import List, Dict, Any
from occ_check.traffic.parser import parse_line
from occ_check.traffic.window import binary_search_log_start

WP_ENDPOINTS = [
    "/wp-login.php", "/xmlrpc.php", "/wp-admin/", 
    "/wp-admin/admin-ajax.php", "/wp-cron.php", "/wp-json/"
]

KNOWN_BOTS = {
    "googlebot": "Googlebot", "bingbot": "Bingbot", "semrushbot": "SemrushBot",
    "ahrefsbot": "AhrefsBot", "petalbot": "PetalBot", "claudebot": "ClaudeBot",
    "gptbot": "GPTBot", "siteauditbot": "SiteAuditBot"
}

def analyze_logs(log_sources: List[Dict[str, str]], start_ts: float, end_ts: float) -> Dict[str, Any]:
    total_requests = 0
    domains = Counter()
    ips = Counter()
    uris = Counter()
    methods = Counter()
    statuses = Counter()
    user_agents = Counter()
    ip_uri_pairs = Counter()
    wp_stats = defaultdict(Counter)
    classified_bots = Counter()

    for source in log_sources:
        path = source['path']
        domain = source.get('domain', 'unknown')

        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                binary_search_log_start(f, start_ts, lambda l: (parse_line(l) or {}).get('timestamp'))

                for line in f:
                    record = parse_line(line)
                    if not record:
                        continue

                    ts = record['timestamp']
                    if ts < start_ts:
                        continue
                    if ts > end_ts:
                        break

                    total_requests += 1
                    domains[domain] += 1
                    ip = record['ip']
                    uri = record['uri'] or '/'
                    agent = record['agent'] or 'Empty'

                    ips[ip] += 1
                    uris[uri] += 1
                    methods[record['method'] or 'GET'] += 1
                    statuses[record['status']] += 1
                    user_agents[agent] += 1
                    ip_uri_pairs[(ip, uri)] += 1

                    for wp_ep in WP_ENDPOINTS:
                        if wp_ep in uri:
                            wp_stats[wp_ep][ip] += 1

                    agent_lower = agent.lower()
                    for bot_key, bot_name in KNOWN_BOTS.items():
                        if bot_key in agent_lower:
                            classified_bots[bot_name] += 1

        except Exception:
            continue

    duration = max(1.0, end_ts - start_ts)
    return {
        "total_requests": total_requests,
        "rps": round(total_requests / duration, 2),
        "top_domains": domains.most_common(5),
        "top_ips": ips.most_common(10),
        "top_uris": uris.most_common(10),
        "methods": dict(methods),
        "statuses": dict(statuses),
        "top_ip_uri_pairs": ip_uri_pairs.most_common(10),
        "wp_stats": {k: dict(v.most_common(5)) for k, v in wp_stats.items()},
        "classified_bots": dict(classified_bots),
        "top_user_agents": user_agents.most_common(5)
    }
