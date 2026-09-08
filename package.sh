#!/usr/bin/env sh
# Run from any directory; include only distributable source files.
set -eu
cd -- "$(dirname -- "$0")"
exec python3 -B - <<'PY'
from pathlib import Path
import hashlib
import tarfile
root = Path.cwd()
output = root.parent / 'PCBridgeLinux.tar.gz'
files = [*root.glob('*.py'), *root.glob('*.md'), *root.glob('*.sh'),
         root / 'requirements.txt', root / 'requirements.lock',
         root / '.gitignore', root / '.gitattributes']
for directory in ('docs', 'ops', '.github'):
    files.extend(p for p in (root / directory).rglob('*') if p.is_file()
                 and '__pycache__' not in p.parts and p.suffix != '.pyc')
with tarfile.open(output, 'w:gz') as archive:
    for path in sorted(set(files)):
        if path.is_symlink():
            raise SystemExit(f'Recusa empacotar symlink: {path}')
        archive.add(path, arcname=str(Path('PCBridgeLinux') / path.relative_to(root)), recursive=False)
digest = hashlib.sha256(output.read_bytes()).hexdigest()
output.with_suffix(output.suffix + '.sha256').write_text(f'{digest}  {output.name}\n')
print(output)
PY
