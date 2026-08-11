import os
import glob
from typing import List, Dict
from occ_check.adapters.base import EnvironmentAdapter

class CPanelAdapter(EnvironmentAdapter):
    def name(self) -> str:
        return "cPanel / WHM"

    def detect(self) -> bool:
        return os.path.exists("/usr/local/cpanel/version") or os.path.exists("/etc/cpanel_version")

    def get_apache_config_paths(self) -> List[str]:
        return [
            "/etc/apache2/conf/httpd.conf",
            "/usr/local/apache/conf/httpd.conf",
            "/etc/httpd/conf/httpd.conf"
        ]

    def get_log_sources(self) -> List[Dict[str, str]]:
        sources = []
        paths = glob.glob("/usr/local/apache/domlogs/*") + glob.glob("/var/log/apache2/domlogs/*")
        for p in paths:
            if os.path.isfile(p) and not p.endswith("-bytes_log"):
                domain = os.path.basename(p)
                sources.append({
                    "domain": domain,
                    "path": p,
                    "format": "apache_combined"
                })
        if not sources:
            for err in ["/etc/apache2/logs/error_log", "/var/log/apache2/error_log", "/usr/local/apache/logs/error_log"]:
                if os.path.exists(err):
                    sources.append({"domain": "system", "path": err, "format": "error_log"})
        return sources

    def get_php_fpm_pools(self) -> List[Dict[str, str]]:
        pools = []
        for path in glob.glob("/opt/cpanel/ea-php*/root/etc/php-fpm.d/*.conf"):
            pools.append({"pool_file": path, "type": "cpanel_ea4"})
        return pools
