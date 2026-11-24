"""Lightweight checks that can run without Qt: assets and source layout."""
from pathlib import Path
import struct
root = Path(__file__).resolve().parents[1]
for name in ('file-icon.png', 'folder-icon.png'):
    data = (root/'src/modules/assets'/name).read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II', data[16:24]) == (64, 64)
for file in ('src/app.cpp','src/settings.h','src/settings.cpp','src/popup.cpp','src/modules/filemanager.cpp','src/modules/terminal.cpp','src/modules/monitoring.cpp'):
    assert (root/file).is_file(), file
print('PASS: original 64x64 assets and expected C++ source layout')
