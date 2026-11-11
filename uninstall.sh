#!/bin/bash
set -euo pipefail

if [[ $# -ne 0 ]]; then
    printf 'Cách dùng: ./uninstall.sh\n' >&2
    exit 2
fi
if [[ "$(/usr/bin/uname -s)" != Darwin || "$(/usr/bin/id -u)" == 0 ]]; then
    printf 'Hãy chạy bằng tài khoản macOS đã đăng nhập, không dùng sudo.\n' >&2
    exit 1
fi

app_dir="$HOME/Library/Application Support/Tet Countdown 2027"
label="local.tet-countdown-2027"
domain="gui/$(/usr/bin/id -u)"
service="$domain/$label"
plist="$HOME/Library/LaunchAgents/$label.plist"

if ! /bin/launchctl print "$domain" >/dev/null 2>&1; then
    printf 'Hãy mở Terminal trong phiên đăng nhập macOS rồi chạy lại.\n' >&2
    exit 1
fi
if /bin/launchctl print "$service" >/dev/null 2>&1; then
    /bin/launchctl bootout "$service"
fi

/bin/rm -f "$plist" "$app_dir"/{bot.py,webhook,last-sent,last-sent.tmp,send.lock,stdout.log,stderr.log}
if [[ -d "$app_dir" ]]; then
    /bin/rmdir "$app_dir" 2>/dev/null || printf 'Thư mục còn tệp khác: %s\n' "$app_dir"
fi
printf 'Đã gỡ lịch Tết Countdown 2027.\n'
