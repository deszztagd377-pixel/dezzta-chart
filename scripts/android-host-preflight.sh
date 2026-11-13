#!/usr/bin/env sh
# Read-only Android/Termux capability inventory for the DEZZTA CHART host POC.
# This script deliberately installs nothing, starts no services, and prints no secrets.
set -u

printf '%s\n' "DEZZTA CHART Android host preflight (read-only)"
printf '%s\n' "No packages will be installed and no services will be started."
printf '\n'

report_value() {
  label=$1
  value=$2
  if [ -n "$value" ]; then
    printf 'INFO  %-24s %s\n' "$label" "$value"
  else
    printf 'INFO  %-24s unavailable\n' "$label"
  fi
}

report_command() {
  label=$1
  command_name=$2
  if command -v "$command_name" >/dev/null 2>&1; then
    printf 'FOUND %-24s %s\n' "$label" "$(command -v "$command_name")"
  else
    printf 'MISS  %-24s %s\n' "$label" "$command_name"
  fi
}

report_value "kernel" "$(uname -s 2>/dev/null || true)"
report_value "machine" "$(uname -m 2>/dev/null || true)"
report_value "android_abi" "$(getprop ro.product.cpu.abi 2>/dev/null || true)"
report_value "android_release" "$(getprop ro.build.version.release 2>/dev/null || true)"

if [ -n "${PREFIX:-}" ] && [ -n "${TERMUX_VERSION:-}" ]; then
  report_value "termux" "detected"
elif [ -n "${PREFIX:-}" ]; then
  report_value "termux" "prefix-present; version-unconfirmed"
else
  report_value "termux" "not-detected"
fi

if [ -n "${HOME:-}" ] && [ -d "$HOME" ]; then
  free_kb=$(df -Pk "$HOME" 2>/dev/null | awk 'NR == 2 {print $4}')
  report_value "home_free_kb" "${free_kb:-unavailable}"
else
  report_value "home_storage" "unavailable"
fi

if [ -r /proc/meminfo ]; then
  available_kb=$(awk '/^MemAvailable:/ {print $2; exit}' /proc/meminfo)
  report_value "memory_available_kb" "${available_kb:-unavailable}"
else
  report_value "memory_available" "unavailable"
fi

printf '\n%s\n' "Runtime command availability:"
report_command "python3" "python3"
report_command "pip" "pip"
report_command "openssl" "openssl"
report_command "redis-server" "redis-server"
report_command "redis-cli" "redis-cli"
report_command "curl" "curl"
report_command "termux-wake-lock" "termux-wake-lock"

if command -v python3 >/dev/null 2>&1; then
  printf '\n%s\n' "Python module availability (imports only; no network or writes):"
  python3 -c 'import importlib.util; names=("fastapi","uvicorn","redis","cryptography","firebase_admin","databento"); [print(("FOUND " if importlib.util.find_spec(name) else "MISS  ") + name) for name in names]' 2>/dev/null || printf '%s\n' "INFO  python_import_probe      unavailable"
else
  printf '\n%s\n' "INFO  python_import_probe      skipped (python3 missing)"
fi

printf '\n%s\n' "PRECHECK ONLY: these results do not certify production readiness."
printf '%s\n' "No secret values, environment dump, process list, or network probe is collected."
exit 0
