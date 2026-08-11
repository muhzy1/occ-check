import os
import subprocess
from typing import List, Optional, Dict, Any

class EnvironmentAdapter:
    """Base interface for platform-specific discovery."""
    
    def name(self) -> str:
        raise NotImplementedError

    def detect(self) -> bool:
        raise NotImplementedError

    def get_apache_config_paths(self) -> List[str]:
        return []

    def get_log_sources(self) -> List[Dict[str, str]]:
        return []

    def get_php_fpm_pools(self) -> List[Dict[str, str]]:
        return []

    def get_mysql_socket(self) -> Optional[str]:
        for sock in ["/var/lib/mysql/mysql.sock", "/var/run/mysqld/mysqld.sock", "/tmp/mysql.sock"]:
            if os.path.exists(sock):
                return sock
        return None

def exec_cmd(cmd: List[str], timeout: int = 5) -> str:
    """Executes shell command safely with timeout."""
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return res.stdout.strip()
    except Exception:
        return ""
