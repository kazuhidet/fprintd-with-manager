#!/usr/bin/env python3
"""JSON-lines bridge between the Quickshell panel and fprintd's system bus."""
import argparse
import getpass
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile

FINGERS = [side + '-' + finger for side in ('right', 'left')
           for finger in ('thumb', 'index-finger', 'middle-finger', 'ring-finger', 'little-finger')]
SERVICES = {
    'Login screen': ['login', 'greetd', 'sddm', 'gdm-password', 'lightdm'],
    'Lock screen': ['omarchy-lock-fingerprint', 'hyprlock', 'kde-fingerprint'],
    'sudo': ['sudo'], 'polkit': ['polkit-1'],
}
# PAM services of each display manager, keyed by systemd unit name. Leftover
# packages (e.g. gdm next to sddm) must not decide the login screen's state.
DISPLAY_MANAGERS = {
    'plasmalogin': ['plasmalogin'], 'sddm': ['sddm'],
    'gdm': ['gdm-password', 'gdm-fingerprint'],
    'greetd': ['greetd', 'cosmic-greeter', 'login'],
    'cosmic-greeter': ['cosmic-greeter', 'greetd', 'login'],
    'lightdm': ['lightdm'], 'lxdm': ['lxdm'],
}
DM_UNIT = Path('/etc/systemd/system/display-manager.service')
PAM_DIR = Path('/etc/pam.d')
VENDOR_DIR = Path('/usr/lib/pam.d')
MARK = '# fprintd-manager-managed'
BUS = 'net.reactivated.Fprint'
INTERFACE = BUS + '.Device'


def emit(**data):
    print(json.dumps(data, ensure_ascii=False), flush=True)


def pam_path(name):
    path = PAM_DIR / name
    return path if path.exists() else VENDOR_DIR / name


def location_services(location):
    if location == 'Login screen':
        unit = DM_UNIT.resolve().name
        if unit.endswith('.service') and unit[:-len('.service')] in DISPLAY_MANAGERS:
            return DISPLAY_MANAGERS[unit[:-len('.service')]]
    return SERVICES[location]


def pam_stack(name, seen=None):
    seen = set() if seen is None else seen
    if name in seen or not re.fullmatch(r'[\w.-]+', name):
        return []
    seen.add(name)
    path = pam_path(name)
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    result = list(lines)
    for line in lines:
        parts = line.split('#', 1)[0].split()
        if len(parts) >= 3 and parts[0] == 'auth' and parts[1] in ('include', 'substack'):
            result.extend(pam_stack(parts[2], seen))
        elif len(parts) == 2 and parts[0] == '@include':
            result.extend(pam_stack(parts[1], seen))
    return result


def fingerprint_line(line):
    return bool(re.search(r'\bpam_fprintd\.so\b', line.split('#', 1)[0]))


def pam_status():
    result = []
    tries, timeout = 7, 30
    for location in SERVICES:
        names = location_services(location)
        available = [name for name in names if pam_path(name).exists()]
        lines = [line for name in available for line in pam_stack(name)]
        fp = [line for line in lines if fingerprint_line(line)]
        native = any(MARK not in line for line in fp)
        for line in fp:
            if MARK in line:
                for option, value in re.findall(r'(max-tries|timeout)=(\d+)', line):
                    if option == 'max-tries':
                        tries = int(value)
                    else:
                        timeout = int(value)
        result.append(dict(name=location, enabled=bool(fp), available=bool(available), native=native))
    return result, tries, timeout


def apply_pam(location, enable, tries, timeout):
    """Only edit this plugin's own lines; leave existing authentication intact."""
    if location not in SERVICES or not 1 <= tries <= 15 or not 5 <= timeout <= 120:
        raise ValueError('Invalid PAM settings')
    for name in location_services(location):
        src = pam_path(name)
        if not src.exists():
            continue
        original = src.read_text()
        if any(fingerprint_line(line) and MARK not in line for line in pam_stack(name)):
            continue  # Existing native fingerprint stacks belong to the administrator.
        lines = [line for line in original.splitlines(keepends=True) if MARK not in line]
        if enable:
            # Keep required checks before the sufficient fingerprint line.
            required = [i for i, line in enumerate(lines)
                        if re.match(r'^\s*auth\s+(required|requisite|\[)', line)]
            anchors = [i for i, line in enumerate(lines)
                       if re.match(r'^\s*auth\s+(include|substack)\s+', line)]
            position = max(required, default=-1) + 1
            if anchors and position > anchors[0]:
                raise ValueError(f'{name}: authentication order needs administrator review')
            if anchors:
                position = anchors[0]
            lines.insert(position, f'auth sufficient pam_fprintd.so max-tries={tries} timeout={timeout} {MARK}\n')
        updated = ''.join(lines)
        if updated == original:
            continue
        dst = PAM_DIR / name
        backup = dst.with_name(name + '.fprintd-manager.bak')
        if dst.exists() and not backup.exists():
            backup.write_bytes(dst.read_bytes())
            backup.chmod(0o600)
        fd, tmp = tempfile.mkstemp(prefix='.' + name, dir=PAM_DIR)
        try:
            with os.fdopen(fd, 'w') as stream:
                stream.write(updated)
            os.chmod(tmp, src.stat().st_mode & 0o777)
            os.replace(tmp, dst)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)


def gio():
    import gi
    from gi.repository import Gio, GLib
    return Gio, GLib


def proxy(path, interface):
    Gio, _ = gio()
    return Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SYSTEM, Gio.DBusProxyFlags.NONE,
                                        None, BUS, path, interface, None)


def call(device, method, signature=None, values=()):
    Gio, GLib = gio()
    params = GLib.Variant(signature, values) if signature else None
    return device.call_sync(method, params, Gio.DBusCallFlags.ALLOW_INTERACTIVE_AUTHORIZATION,
                            30000, None).unpack()


def prop(device, name, default):
    value = device.get_cached_property(name)
    return value.unpack() if value is not None else default


def devices():
    manager = proxy('/net/reactivated/Fprint/Manager', BUS + '.Manager')
    return call(manager, 'GetDevices')[0]


def status():
    locations, tries, timeout = pam_status()
    readers = []
    error = ''
    try:
        for path in devices():
            device = proxy(path, INTERFACE)
            try:
                fingers = call(device, 'ListEnrolledFingers', '(s)', (getpass.getuser(),))[0]
            except Exception as exc:
                if 'NoEnrolledPrints' not in str(exc):
                    raise
                fingers = []
            readers.append(dict(path=path, name=prop(device, 'name', path),
                                stages=prop(device, 'num-enroll-stages', 1), fingers=fingers))
    except Exception as exc:
        error = str(exc)
    emit(type='state', devices=readers, locations=locations, tries=tries, timeout=timeout, error=error)


def operation(action, path, finger):
    _, GLib = gio()
    if path not in devices():
        raise ValueError('The selected reader is no longer available')
    device = proxy(path, INTERFACE)
    claimed = started = False
    loop = GLib.MainLoop()
    outcome = dict(success=False, message='Operation ended')
    stages = max(1, prop(device, 'num-enroll-stages', 1))
    count = 0
    def cancel(*_):
        outcome.update(success=False, message='Cancelled')
        loop.quit()
    def timed_out():
        outcome.update(success=False, message='Timed out')
        loop.quit()
        return False
    def received(_proxy, _sender, name, params):
        nonlocal count
        if name != ('EnrollStatus' if action == 'enroll' else 'VerifyStatus'):
            return
        result, done = params.unpack()
        if result == 'enroll-stage-passed':
            count += 1
        emit(type='progress', message=result, progress=min(count / stages, 1))
        if done:
            outcome.update(success=result in ('enroll-completed', 'verify-match'), message=result)
            loop.quit()
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda: (cancel(), False)[1])
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, lambda: (cancel(), False)[1])
    try:
        call(device, 'Claim', '(s)', (getpass.getuser(),))
        claimed = True
        stages = max(1, prop(device, "num-enroll-stages", 1))
        if action == 'delete':
            call(device, 'DeleteEnrolledFinger' if finger else 'DeleteEnrolledFingers2',
                 '(s)' if finger else None, (finger,) if finger else ())
            outcome.update(success=True, message='Fingerprints deleted')
        else:
            device.connect('g-signal', received)
            call(device, 'EnrollStart' if action == 'enroll' else 'VerifyStart', '(s)', (finger or 'any',))
            started = True
            emit(type='progress', message='Touch the reader', progress=0)
            # Unix GLib sources interrupt the loop even while no device signal arrives.
            GLib.timeout_add_seconds(120, timed_out)
            loop.run()
    finally:
        if started:
            try:
                call(device, 'EnrollStop' if action == 'enroll' else 'VerifyStop')
            except Exception:
                pass
        if claimed:
            call(device, 'Release')
    emit(type='result', **outcome)
    return 0 if outcome['success'] else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['status', 'enroll', 'verify', 'delete', 'pam', 'pam-root'])
    parser.add_argument('--device', default='')
    parser.add_argument('--finger', choices=FINGERS, default=None)
    parser.add_argument('--location', choices=list(SERVICES))
    parser.add_argument('--enable', choices=['0', '1'], default='1')
    parser.add_argument('--tries', type=int, default=7)
    parser.add_argument('--timeout', type=int, default=30)
    args = parser.parse_args()
    try:
        if args.action == 'status':
            status()
        elif args.action in ('pam', 'pam-root'):
            if args.action == 'pam-root':
                if os.geteuid() != 0:
                    raise PermissionError('Administrator authentication required')
                apply_pam(args.location, args.enable == '1', args.tries, args.timeout)
            else:
                command = ['pkexec', '/usr/bin/python3', str(Path(__file__).resolve()), 'pam-root',
                           '--location', args.location or '', '--enable', args.enable,
                           '--tries', str(args.tries), '--timeout', str(args.timeout)]
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode:
                    raise RuntimeError(result.stderr or result.stdout or 'Authentication cancelled')
            emit(type='result', success=True, message='Authentication settings updated')
        else:
            if args.action == 'enroll' and not args.finger:
                raise ValueError('Select a finger')
            return operation(args.action, args.device, args.finger)
        return 0
    except Exception as exc:
        emit(type='result', success=False, message=str(exc))
        return 1


if __name__ == '__main__':
    sys.exit(main())
