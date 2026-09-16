"""Run with .build-venv/Scripts/python.exe after preparing vendor/tesseract."""
from pathlib import Path
import shutil
import subprocess
import sys
import hashlib
import importlib.metadata

ROOT = Path(__file__).resolve().parent
def main():
    engine = ROOT / 'vendor/tesseract'
    if not (engine / 'tesseract.exe').exists():
        raise SystemExit('Prepare vendor/tesseract first. See README.')
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
        '--name', 'GameFit', '--onedir', '--console', '--add-data', 'web;web',
        '--add-data', 'vendor/tesseract;vendor/tesseract', 'desktop.py'], cwd=ROOT, check=True)
    output = ROOT / 'dist/GameFit'
    for name in ('PORTABLE_README.txt', 'THIRD_PARTY_NOTICES.md'):
        shutil.copy2(ROOT / name, output / name)
    licenses = output / 'licenses'
    licenses.mkdir(exist_ok=True)
    shutil.copy2(Path(sys.base_prefix) / 'LICENSE.txt', licenses / 'Python-LICENSE.txt')
    for package in ('pillow', 'pyinstaller'):
        dist = importlib.metadata.distribution(package)
        for item in dist.files or []:
            if 'license' in str(item).lower() or 'copying' in str(item).lower():
                source = Path(dist.locate_file(item))
                if source.is_file(): shutil.copy2(source, licenses / (package + '-' + source.name))
    release = ROOT / 'release'; release.mkdir(exist_ok=True)
    archive = Path(shutil.make_archive(str(release / 'GameFit-Windows-x64'), 'zip', ROOT / 'dist', 'GameFit'))
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (release / 'SHA256SUMS.txt').write_text(f'{checksum}  {archive.name}\n', encoding='utf-8')
    print(archive, archive.stat().st_size, checksum)

if __name__ == '__main__': main()
