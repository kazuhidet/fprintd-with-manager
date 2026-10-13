#!/usr/bin/env python3
"""Install the panel without changing existing Omarchy settings."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import tempfile


def install(config):
    source = Path(__file__).parent / 'fprintd.manager'
    destination = config / 'plugins' / 'fprintd.manager'
    destination.mkdir(parents=True, exist_ok=True)
    for name in ('manifest.json', 'Panel.qml', 'backend.py'):
        shutil.copy2(source / name, destination / name)
    path = config / 'shell.json'
    if path.exists():
        data = json.loads(path.read_text())
        backup = path.with_name('shell.json.fprintd-manager.' + datetime.now().strftime('%Y%m%d%H%M%S%f') + '.bak')
        shutil.copy2(path, backup)
    else:
        data = {'version': 1}
    plugins = data.setdefault('plugins', [])
    if not any(entry.get('id') == 'fprintd.manager' for entry in plugins):
        plugins.append({'id': 'fprintd.manager'})
    if 'disabledPlugins' in data:
        data['disabledPlugins'] = [p for p in data['disabledPlugins'] if p != 'fprintd.manager']
    fd, temporary = tempfile.mkstemp(prefix='.shell.', dir=config)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path,
                        default=Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'omarchy')
    args = parser.parse_args()
    print(install(args.config))
    print("Open: omarchy-shell shell summon fprintd.manager '{}'")
