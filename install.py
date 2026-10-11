#!/usr/bin/env python3
"""Install without overwriting existing project configuration. Python 3.9+."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
MARKER = '<!-- claude-feature-mvp -->'

def install(target):
    target = target.resolve()
    g = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=target, capture_output=True, text=True)
    if g.returncode or Path(g.stdout.strip()).resolve() != target:
        raise ValueError('Target must be the root of an existing git repository.')
    files = sorted(p for p in (SOURCE / '.claude').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    writes = []
    for p in files:
        dest = target / p.relative_to(SOURCE)
        if dest.resolve() != dest.absolute():
            raise ValueError('Symlinked destination is unsupported: ' + str(dest))
        if dest.exists():
            if dest == target / '.claude/settings.json':
                json.loads(dest.read_text())  # preserve current permissions and hooks
                continue
            if dest.read_bytes() != p.read_bytes():
                raise ValueError('Existing file differs; no files changed: ' + str(dest))
        else:
            writes.append((p, dest))
    claude = target / 'CLAUDE.md'
    if claude.resolve() != claude.absolute():
        raise ValueError('Symlinked CLAUDE.md is unsupported.')
    existing = claude.read_text(encoding='utf-8') if claude.exists() else ''
    for p, dest in writes:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dest)
    if MARKER not in existing:
        addition = SOURCE.joinpath('CLAUDE.md').read_text(encoding='utf-8')
        claude.write_text(existing.rstrip() + '\n\n' + MARKER + '\n' + addition, encoding='utf-8')
    print('Installed. Existing settings.json preserved when present.')
    print('Commit installed configuration, restart Claude Code, check /agents and /feature-plan.')

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('repository', type=Path)
    args = p.parse_args()
    try:
        install(args.repository)
    except (ValueError, OSError) as e:
        p.exit(1, str(e) + '\n')
