import os
import glob
from typing import List, Dict
from occ_check.adapters.base import EnvironmentAdapter

class PleskAdapter(EnvironmentAdapter):
    def name(self) -> str:
        return "Plesk"

    def detect(self) -> bool:
        return os.path.exists("/usr/local/psa") or os.path.exists("/etc/psa/psa.conf")

    def get_apache_config_paths(self) -> List[str]:
        return ["/etc/httpd/conf/httpd.conf", "/etc/apache2/apache2.conf"]

    def get_log_sources(self) -> List[Dict[str, str]]:
        sources = []
        for p in glob.glob("/var/www/vhosts/system/*/logs/access_log*"):
            parts = p.split("/")
            domain = parts[5] if len(parts) > 5 else "unknown"
            sources.append({"domain": domain, "path": p, "format": "apache_combined"})
        return sources
