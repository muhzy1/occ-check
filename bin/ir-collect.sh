#!/bin/bash
# READ-ONLY incident evidence collector (cPanel/WHM, EL-based).
# Makes no changes. Prints to stdout.
# Run from workstation: ssh root@SERVER 'bash -s' < ir-collect.sh > ir_output.txt 2>&1
DAYS=${DAYS:-7}
SINCE=${SINCE:-"7 days ago"}
N="nice -n 19 ionice -c3"
sec(){ echo; echo "=================== $* ==================="; }
run(){ echo; echo "\$ $*"; timeout 60 bash -c "$*" 2>&1; }

sec "PHASE 1 BASELINE"
for c in "hostname" "hostnamectl" "uptime" "w" "nproc" "lscpu | head -25" "free -h" \
         "swapon --show" "df -h" "df -i" "mount | grep -vE 'cgroup|proc|sysfs|tmpfs|devpts'" \
         "systemctl --failed --no-pager" "date"; do run "$c"; done

sec "PHASE 2 CURRENT RESOURCE STATE"
for c in "top -b -n1 -H | head -80" \
         "ps aux --sort=-%cpu | head -30" \
         "ps aux --sort=-%mem | head -30" \
         "ps -eo pid,ppid,user,%cpu,%mem,rss,vsz,stat,etime,cmd --sort=-rss | head -40" \
         "vmstat 1 5" "cat /proc/loadavg" "cat /proc/meminfo" \
         "ps -eo stat | cut -c1 | sort | uniq -c" \
         "ps -eo pid,user,stat,wchan:30,etime,cmd | awk '\$3 ~ /^D/' | head -40" \
         "cat /proc/pressure/memory /proc/pressure/io /proc/pressure/cpu 2>/dev/null"; do run "$c"; done

sec "PHASE 3/5/6/7 HISTORICAL (sysstat)"
run "systemctl is-active sysstat; ls -la /var/log/sa/ /var/log/sysstat/ 2>/dev/null | head -40"
if command -v sar >/dev/null; then
  for f in $(ls -1t /var/log/sa/sa[0-9][0-9] /var/log/sysstat/sa[0-9][0-9] 2>/dev/null | head -$DAYS); do
    echo; echo "########## FILE $f ##########"
    for opt in "-q" "-u" "-r" "-S" "-W" "-B" "-d -p" "-n DEV"; do
      echo; echo "--- sar $opt -f $f"
      $N timeout 60 sar $opt -f "$f" 2>&1
    done
  done
else
  echo "sar NOT INSTALLED - historical data unavailable"
fi
run "iostat -xz 1 5"

sec "PHASE 4 OOM"
run "dmesg -T | grep -iE 'oom|out of memory|killed process|memory cgroup' | tail -100"
run "journalctl -k --no-pager | grep -iE 'oom|out of memory|killed process' | tail -100"
run "journalctl --since '$SINCE' --no-pager | grep -iE 'oom-kill|out of memory|killed process' | tail -200"
run "grep -iE 'out of memory|killed process|oom' /var/log/messages* 2>/dev/null | tail -100"
run "dmesg -T | grep -c -i 'killed process'"

sec "PHASE 5/9 MEMORY BY USER AND PROCESS TYPE"
run "ps -eo user:20,rss --no-headers | awk '{a[\$1]+=\$2; c[\$1]++} END{for(u in a) printf \"%-20s procs=%-5d RSS_MB=%.0f\n\",u,c[u],a[u]/1024}' | sort -t= -k3 -nr | head -25"
run "ps -eo comm,rss --no-headers | awk '{a[\$1]+=\$2; c[\$1]++} END{for(u in a) printf \"%-20s procs=%-5d RSS_MB=%.0f\n\",u,c[u],a[u]/1024}' | sort -t= -k3 -nr | head -20"
run "ps aux | grep -E 'php' | grep -v grep | awk '{u[\$1]++; m[\$1]+=\$6} END{for(x in u) printf \"%-20s php_procs=%-4d RSS_MB=%.0f\n\",x,u[x],m[x]/1024}' | sort -t= -k3 -nr | head -25"
run "ps -eo pid,user,etime,rss,cmd | grep -E 'php' | grep -v grep | sort -k4 -nr | head -25"
run "ls /opt/cpanel/ea-php*/root/etc/php-fpm.d/ 2>/dev/null | head -50"

sec "PHASE 8 APACHE"
run "systemctl status httpd --no-pager | head -20"
run "apachectl -t"
run "apachectl fullstatus 2>&1 | head -60"
run "pgrep -c httpd; ps aux | grep '[h]ttpd' | wc -l"
run "grep -E 'MaxRequestWorkers|ServerLimit|MaxConnectionsPerChild|StartServers' /etc/apache2/conf.modules.d/*mpm* /etc/apache2/conf/httpd.conf /etc/apache2/conf.d/*.conf 2>/dev/null"
for L in /etc/apache2/logs/error_log /usr/local/apache/logs/error_log /var/log/httpd/error_log; do
  [ -f "$L" ] && { run "grep -cE 'AH03490|AH00484|MaxRequestWorkers|server reached' $L"
    run "grep -E 'AH03490|AH00484|MaxRequestWorkers|server reached|segfault|child pid.*exit signal|scoreboard|timeout' $L | tail -80"; }
done

sec "PHASE 10 MYSQL/MARIADB"
run "systemctl status mariadb mysql mysqld --no-pager 2>&1 | head -25"
run "mysqladmin status 2>&1; mysqladmin processlist 2>&1 | head -60"
run "mysql -e 'SHOW GLOBAL STATUS WHERE Variable_name IN (\"Threads_connected\",\"Threads_running\",\"Max_used_connections\",\"Aborted_connects\",\"Aborted_clients\",\"Uptime\"); SHOW VARIABLES LIKE \"max_connections\"; SHOW VARIABLES LIKE \"innodb_buffer_pool_size\";' 2>&1"
for L in /var/lib/mysql/*.err /var/log/mariadb/mariadb.log; do
  [ -f "$L" ] && run "tail -80 $L"
done
run "journalctl -u mariadb -u mysqld --since '$SINCE' --no-pager | tail -60"

sec "PHASE 11 NETWORK / HTTP TRAFFIC"
run "ss -s"
run "ss -ant state established '( sport = :80 or sport = :443 )' | awk 'NR>1{split(\$4,a,\":\"); print a[1]}' | sort | uniq -c | sort -nr | head -20"
DL=/usr/local/apache/domlogs
if [ -d $DL ]; then
  run "ls -lt $DL | head -15"
  run "for f in \$(ls -t $DL/* 2>/dev/null | grep -vE 'ftp|bytes|offsets' | head -10); do echo \"== \$f\"; tail -n 20000 \$f | awk '{print \$1}' | sort | uniq -c | sort -nr | head -5; done"
  run "for f in \$(ls -t $DL/* 2>/dev/null | grep -vE 'ftp|bytes|offsets' | head -10); do echo \"== \$f\"; tail -n 20000 \$f | awk '{print \$7}' | cut -d'?' -f1 | sort | uniq -c | sort -nr | head -5; done"
  run "for f in \$(ls -t $DL/* 2>/dev/null | grep -vE 'ftp|bytes|offsets' | head -10); do tail -n 20000 \$f; done | awk -F'\"' '{print \$6}' | sort | uniq -c | sort -nr | head -15"
  run "for f in \$(ls -t $DL/* 2>/dev/null | grep -vE 'ftp|bytes|offsets' | head -10); do tail -n 20000 \$f; done | awk '{print substr(\$4,2,14)}' | sort | uniq -c | sort -nr | head -15"
fi

sec "PHASE 12 CRON / BACKUPS"
run "cat /etc/crontab; ls -la /etc/cron.d /etc/cron.hourly /etc/cron.daily /etc/cron.weekly"
run "for u in \$(cut -d: -f1 /etc/passwd); do crontab -l -u \$u 2>/dev/null | grep -v '^#' | sed \"s/^/[\$u] /\"; done | head -80"
run "grep -E 'BACKUPENABLE|BACKUPDAYS|BACKUPTYPE|BACKUPACCTS' /var/cpanel/backups/config 2>/dev/null"
run "ls -lt /usr/local/cpanel/logs/cpbackup/ 2>/dev/null | head -8"
run "grep -iE 'cron' /var/log/cron 2>/dev/null | tail -60"

sec "PHASE 13 SERVICES / SECURITY SOFTWARE"
run "systemctl list-units --type=service --state=running --no-pager | grep -iE 'clam|spam|exim|dovecot|named|imunify|lfd|csf|cpanel|cpsrvd|chkservd|redis|memcache|elastic'"
run "ps -eo pid,user,rss,etime,cmd --sort=-rss | grep -iE 'clamd|spamd|exim|dovecot|named|imunify|lfd|maldet|cphulk' | grep -v grep | head -20"
run "exim -bpc 2>&1"
run "tail -60 /var/log/chkservd.log 2>/dev/null"
run "tail -40 /var/log/lfd.log 2>/dev/null"
run "journalctl --since '$SINCE' --no-pager -u clamd@scan -u clamd -u imunify360-agent -u spamd 2>&1 | tail -40"

sec "PHASE 14 HARDWARE / HYPERVISOR"
run "systemd-detect-virt"
run "dmesg -T | grep -iE 'i/o error|ata[0-9]|blk_update|ext4-fs error|xfs.*(error|corrupt)|hung task|blocked for more than|soft lockup|hardware error|mce|balloon|virtio_balloon' | tail -60"
run "top -b -n1 | grep -E '^%?Cpu'"
run "journalctl -p err --since '$SINCE' --no-pager | tail -60"

sec "PHASE 15 MONITORING"
run "ps aux | grep -iE 'nrpe|zabbix|snmpd|nagios|datadog|telegraf|node_exporter|netdata' | grep -v grep"
run "grep -rIl -iE 'check_http|check_ssh|check_load|check_ping' /etc 2>/dev/null | head"
run "last -x -F | head -20"
run "journalctl --list-boots --no-pager | tail -5"

echo; echo "=================== DONE $(date) ==================="
