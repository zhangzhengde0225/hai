#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKER_SCRIPT="$SCRIPT_DIR/minimax_worker.py"

echo "Starting minimax worker..."
echo "Script: $WORKER_SCRIPT"

# 使用 watchmedo 实现文件变更自动重载（pip install watchdog）
if command -v watchmedo &>/dev/null; then
    echo "Auto-reload: watchmedo (monitors *.py / *.yaml / *.json)"
    exec watchmedo auto-restart \
        --patterns="*.py;*.yaml;*.json" \
        --recursive \
        --directory="$SCRIPT_DIR" \
        -- python "$WORKER_SCRIPT" "$@"
else
    # 降级：进程崩溃自动重启
    echo "watchmedo not found — using crash-restart loop."
    echo "Install for file-change reload:  pip install watchdog"
    while true; do
        python "$WORKER_SCRIPT" "$@"
        EXIT_CODE=$?
        [[ $EXIT_CODE -eq 0 ]] && { echo "Worker exited cleanly."; break; }
        echo "Worker crashed (exit $EXIT_CODE). Restarting in 3s..."
        sleep 3
    done
fi
