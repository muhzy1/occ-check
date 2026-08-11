import os
import glob
from typing import List, Dict
from occ_check.adapters.base import EnvironmentAdapter

class GenericLinuxAdapter(EnvironmentAdapter):
    def name(self) -> str:
        return "Generic Linux / Unmanaged"

    def detect(self) -> bool:
        return True

    def get_apache_config_paths(self) -> List[str]:
        return ["/etc/apache2/apache2.conf", "/etc/httpd/conf/httpd.conf"]

    def get_log_sources(self) -> List[Dict[str, str]]:
        sources = []
        candidates = [
            "/var/log/apache2/access.log", "/var/log/httpd/access_log",
            "/var/log/nginx/access.log"
        ]
        for c in candidates:
            if os.path.exists(c):
                sources.append({"domain": "default", "path": c, "format": "apache_combined"})
        return sources
