"""Bundled Tesseract OCR. Images are processed locally, never sent to an OCR API."""
import io
import os
from pathlib import Path
import subprocess
import tempfile
import threading
from .safe_images import fetch_image, public_addresses

ROOT = Path(__file__).resolve().parent.parent
LOCK = threading.Lock()

def validate_image_url(url):
    public_addresses(url)

def image_bytes(url):
    return fetch_image(url)

def recognize(data):
    engine = ROOT / 'vendor' / 'tesseract' / 'tesseract.exe'
    models = engine.parent / 'tessdata'
    if not engine.exists() or not (models / 'kor.traineddata').exists():
        raise ValueError('OCR 엔진이 없습니다. OCR 포함 Windows 배포본을 사용하세요.')
    try:
        from PIL import Image, ImageOps
    except ImportError as e:
        raise ValueError('이미지 처리 라이브러리가 없습니다. 배포본을 사용하세요.') from e
    if not LOCK.acquire(blocking=False):
        raise ValueError('다른 OCR 작업이 실행 중입니다. 잠시 후 다시 시도하세요.')
    try:
        with Image.open(io.BytesIO(data)) as original:
            if original.format not in ('PNG', 'JPEG', 'WEBP', 'GIF', 'BMP', 'TIFF'):
                raise ValueError('PNG, JPG, WEBP, GIF, BMP, TIFF 이미지만 지원합니다.')
            if original.width * original.height > 25_000_000:
                raise ValueError('이미지 해상도가 너무 큽니다.')
            # Animated artwork: only first frame; relevant static posters are processed separately.
            original.seek(0)
            rgba = ImageOps.exif_transpose(original).convert('RGBA')
            white = Image.new('RGBA', rgba.size, 'white')
            white.alpha_composite(rgba)
            img = ImageOps.grayscale(white.convert('RGB'))
        if img.width < 1400:
            scale = min(2, 1400 / img.width, (25_000_000 / (img.width * img.height)) ** 0.5)
            img = img.resize((round(img.width * scale), round(img.height * scale)))
        env = os.environ.copy()
        env['OMP_THREAD_LIMIT'] = '2'
        with tempfile.TemporaryDirectory(prefix='gamefit-ocr-') as folder:
            path = Path(folder) / 'input.png'
            img.save(path)
            process = subprocess.run([str(engine), str(path), 'stdout', '--tessdata-dir',
                str(models), '-l', 'kor+eng', '--psm', '6'],
                capture_output=True, timeout=90, env=env,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            if process.returncode:
                raise ValueError('OCR 실행에 실패했습니다. 배포 폴더 전체를 다시 압축 해제해 주세요.')
            return process.stdout.decode('utf-8', errors='replace').strip()
    except subprocess.TimeoutExpired as e:
        raise ValueError('OCR 시간이 초과되었습니다. 공고 본문을 직접 입력하세요.') from e
    except (OSError, Image.DecompressionBombError) as e:
        raise ValueError('이미지를 읽지 못했습니다.') from e
    finally:
        LOCK.release()

def recognize_url(url):
    return recognize(image_bytes(url))
