"""Run a bounded Godot check; explicit diagnostics fail even if exit code is zero.

Example: python <this> --timeout 90 --expect TEST_OK --log <unique.log> -- <godot> --headless ...
Only this invocation's process tree is terminated on failure/timeout. Existing apps are untouched.
"""
import argparse
import math
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import sys
import threading
import time

ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
BAD = re.compile(r"(?:^|\n)(?:SCRIPT ERROR:|ERROR:|.*(?:Parse Error:|Parser Error:|Traceback \(most recent call last\):))")

def stop_owned(process):
    if process.poll() is not None:
        return
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW, check=False)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)

def run_checked(command, timeout, expected=(), log_path=None):
    if not command or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('A command and positive timeout are required')
    log = None
    if log_path:
        log = Path(log_path).open('x', encoding='utf-8', newline='\n')
    kwargs = {'start_new_session': True} if os.name != 'nt' else {
        'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW}
    started = time.monotonic()
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding='utf-8', errors='replace', bufsize=1, **kwargs)
    except BaseException:
        if log:
            log.close()
        raise
    events = queue.Queue()
    def read_lines():
        try:
            for line in process.stdout:
                events.put(line)
        finally:
            events.put(None)
    reader = threading.Thread(target=read_lines, daemon=True)
    reader.start()
    lines = []
    reason = None
    try:
        eof = False
        while not eof:
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                reason = 'timeout'
                stop_owned(process)
                break
            try:
                line = events.get(timeout=min(.1, remaining))
            except queue.Empty:
                continue
            if line is None:
                eof = True
                continue
            lines.append(line)
            if log:
                log.write(line)
                log.flush()
            if BAD.search(ANSI.sub('', line)):
                reason = 'diagnostic'
                stop_owned(process)
                break
        # An application can close stdout while still running; the same deadline still applies.
        if process.poll() is None:
            try:
                process.wait(timeout=max(.001, timeout - (time.monotonic() - started)))
            except subprocess.TimeoutExpired:
                reason = reason or 'timeout'
                stop_owned(process)
        reader.join(timeout=2)
        while not events.empty():
            line = events.get_nowait()
            if line is not None:
                lines.append(line)
                if log:
                    log.write(line)
        text = ''.join(lines)
        reason = reason or ('diagnostic' if BAD.search(ANSI.sub('', text)) else None)
        reason = reason or ('exit-code' if process.returncode != 0 else None)
        missing = [marker for marker in expected if marker not in text]
        reason = reason or ('missing-marker' if missing else None)
        return {'passed': reason is None, 'reason': reason, 'exitCode': process.returncode,
                'missingMarkers': missing, 'elapsedSeconds': round(time.monotonic()-started, 3),
                'log': text}
    finally:
        stop_owned(process)
        if not reader.is_alive():
            process.stdout.close()
        if log:
            log.close()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--timeout', type=float, required=True)
    parser.add_argument('--expect', action='append', default=[])
    parser.add_argument('--log', required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    result = run_checked(command, args.timeout, args.expect, args.log)
    print(result['log'], end='')
    print('CHECKED_RUN', 'PASS' if result['passed'] else 'FAIL', result['reason'],
          'exit=', result['exitCode'], 'elapsed=', result['elapsedSeconds'],
          'missing=', result['missingMarkers'])
    raise SystemExit(0 if result['passed'] else 1)

if __name__ == '__main__':
    main()
