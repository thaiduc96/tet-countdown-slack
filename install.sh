#!/bin/bash
set -euo pipefail
umask 077

if [[ $# -gt 1 || (${1:-} != "" && ${1:-} != --replace-webhook) ]]; then
    printf 'Cách dùng: ./install.sh [--replace-webhook]\n' >&2
    exit 2
fi
if [[ "$(/usr/bin/uname -s)" != Darwin || "$(/usr/bin/id -u)" == 0 ]]; then
    printf 'Hãy chạy bằng tài khoản macOS đã đăng nhập, không dùng sudo.\n' >&2
    exit 1
fi

source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
app_dir="$HOME/Library/Application Support/Tet Countdown"
agents_dir="$HOME/Library/LaunchAgents"
label="local.tet-countdown"
domain="gui/$(/usr/bin/id -u)"
service="$domain/$label"
plist="$agents_dir/$label.plist"

if ! /bin/launchctl print "$domain" >/dev/null 2>&1; then
    printf 'Hãy mở Terminal trong phiên đăng nhập macOS rồi chạy lại.\n' >&2
    exit 1
fi
if ! command -v python3 >/dev/null || ! python="$(python3 -c '
import sys
if sys.version_info < (3, 10):
    sys.exit(1)
from zoneinfo import ZoneInfo
ZoneInfo("Asia/Ho_Chi_Minh")
print(sys.executable)
')"; then
    printf 'Cần Python 3.10 trở lên có dữ liệu múi giờ. Xem README.md.\n' >&2
    exit 1
fi

webhook_file="$app_dir/webhook"
if [[ ! -f "$webhook_file" || ${1:-} == --replace-webhook ]]; then
    printf 'Dán Slack Incoming Webhook URL rồi nhấn Enter (sẽ không hiện ký tự): ' >&2
    if ! IFS= read -rs webhook; then
        printf '\nKhông đọc được webhook.\n' >&2
        exit 1
    fi
    printf '\n' >&2
else
    webhook="$(< "$webhook_file")"
fi
webhook_pattern='^https://hooks\.slack(-gov)?\.com/services/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+$'
if [[ ! "$webhook" =~ $webhook_pattern ]]; then
    printf 'Webhook sai định dạng. Chạy ./install.sh --replace-webhook để nhập lại.\n' >&2
    exit 1
fi

/bin/mkdir -p "$app_dir" "$agents_dir"
/bin/chmod 700 "$app_dir"
tmp_plist=""
tmp_webhook=""
cleanup() {
    if [[ -n "$tmp_plist" ]]; then /bin/rm -f "$tmp_plist"; fi
    if [[ -n "$tmp_webhook" ]]; then /bin/rm -f "$tmp_webhook"; fi
}
trap cleanup EXIT
tmp_plist="$(/usr/bin/mktemp "$agents_dir/.${label}.XXXXXX")"
tmp_webhook="$(/usr/bin/mktemp "$app_dir/.webhook.XXXXXX")"
printf '%s\n' "$webhook" > "$tmp_webhook"
unset webhook

"$python" - "$tmp_plist" "$label" "$app_dir" <<'PY'
import plistlib
import sys
from pathlib import Path

plist_path, label, directory = sys.argv[1:]
app_dir = Path(directory)
agent = {
    "Label": label,
    "ProgramArguments": [sys.executable, str(app_dir / "bot.py"), "--scheduled"],
    "StartCalendarInterval": [{"Minute": minute} for minute in (0, 15, 30, 45)],
    "StandardOutPath": str(app_dir / "stdout.log"),
    "StandardErrorPath": str(app_dir / "stderr.log"),
    "Umask": 0o077,
}
with open(plist_path, "wb") as plist:
    plistlib.dump(agent, plist)
PY
/usr/bin/plutil -lint "$tmp_plist"

if /bin/launchctl print "$service" >/dev/null 2>&1; then
    /bin/launchctl bootout "$service"
fi
/usr/bin/install -m 600 "$source_dir/bot.py" "$app_dir/bot.py"
/usr/bin/install -m 600 "$source_dir/tet-dates.txt" "$app_dir/tet-dates.txt"
/bin/mv -f "$tmp_webhook" "$webhook_file"
/bin/mv -f "$tmp_plist" "$plist"
/bin/launchctl bootstrap "$domain" "$plist"
/bin/launchctl print "$service" >/dev/null

printf 'Đã cài lịch 09:00 giờ Việt Nam. Nhật ký ở %s\n' "$app_dir"
