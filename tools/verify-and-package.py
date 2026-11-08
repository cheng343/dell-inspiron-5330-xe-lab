#!/usr/bin/env python3
"""Check x86_64 Mach-O kext headers, bundle metadata and fixed source identity."""
import hashlib
import json
import os
from pathlib import Path
import plistlib
import struct
import subprocess
import tarfile

root = Path(__file__).resolve().parents[1]
lock = json.loads((root / 'UPSTREAM.lock.json').read_text())
upstream = root / 'build/upstream'
source_commit = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
if source_commit != lock['source_commit']:
    raise SystemExit('Unexpected upstream commit')
subprocess.run(['git', '-C', str(upstream), 'diff', '--exit-code'], check=True)
expected = {
    'NootedGreen': ('com.StezzaPilot.NootedGreen', '1.0.0'),
    'HookCase': ('org.smichaud.HookCase', '8.0.1'),
}
bundles = {}
for name, (identifier, version) in expected.items():
    bundle = upstream / 'build' / (name + '.kext')
    info = plistlib.loads((bundle / 'Contents/Info.plist').read_bytes())
    if (info.get('CFBundleIdentifier'), info.get('CFBundleVersion')) != (identifier, version):
        raise SystemExit(f'Unexpected {name} bundle metadata')
    binary = bundle / 'Contents/MacOS' / name
    data = binary.read_bytes()
    magic, cpu, subtype, filetype = struct.unpack_from('<IIII', data)
    if (magic, cpu, filetype) != (0xFEEDFACF, 0x01000007, 11):
        raise SystemExit(f'{name} is not an x86_64 Mach-O kernel bundle')
    subprocess.run(['codesign', '--verify', '--verbose=2', str(bundle)], check=True)
    bundles[name] = {'identifier': identifier, 'version': version,
                     'architecture': 'x86_64', 'sha256': hashlib.sha256(data).hexdigest()}
record = {'upstream_source_commit': source_commit, 'driver_source_modifications': False,
          'build_repository': os.environ.get('GITHUB_REPOSITORY', 'local'),
          'build_commit': os.environ.get('GITHUB_SHA', 'local'), 'bundles': bundles,
          'hardware_validation': 'not performed',
          'metal_acceleration': 'not tested; additional upstream graphics components required'}
manifest = root / 'build/artifact-manifest.json'
manifest.write_text(json.dumps(record, indent=2) + '\n')
with tarfile.open(root / 'build/dell5330-upstream-kexts.tar.gz', 'w:gz') as archive:
    for name in expected:
        archive.add(upstream / 'build' / (name + '.kext'), arcname=name + '.kext')
    for name in ['LICENSE-NootedGreen', 'LICENSE-HookCase']:
        archive.add(upstream / 'src' / name, arcname=name)
    archive.add(manifest, arcname='artifact-manifest.json')
    archive.add(root / 'README.md', arcname='README.md')
print(json.dumps(record, indent=2))
