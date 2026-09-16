"""Validate all uploads before OCR; preserve the selected file order."""
import base64
import binascii
from .ocr import recognize

def extract_uploads(items):
    if not isinstance(items, list) or not 1 <= len(items) <= 6:
        raise ValueError('이미지를 1~6장 선택하세요.')
    decoded = []; total = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get('data'), str):
            raise ValueError('잘못된 이미지 업로드 형식입니다.')
        try:
            data = base64.b64decode(item['data'], validate=True)
        except (ValueError, binascii.Error) as e:
            raise ValueError('이미지 인코딩이 잘못되었습니다.') from e
        total += len(data)
        if not data or len(data) > 12_000_000 or total > 24_000_000:
            raise ValueError('이미지는 장당 12MB, 전체 24MB 이하여야 합니다.')
        decoded.append(data)
    texts = []
    for index, data in enumerate(decoded, 1):
        try:
            text = recognize(data)
        except ValueError as e:
            raise ValueError(f'{index}번째 이미지: {e}') from e
        if not text.strip():
            raise ValueError(f'{index}번째 이미지에서 글자를 읽지 못했습니다. 더 선명한 이미지를 선택하세요.')
        texts.append(text)
    text = '\n\n'.join(texts)
    if len(text) > 60000:
        raise ValueError('인식된 본문이 너무 깁니다. 이미지를 나누어 분석하세요.')
    return {'text': text, 'url': None, 'ocr_images': len(items), 'kind': 'upload',
            'warning': '선택한 순서로 이미지를 읽었습니다. GIF는 첫 프레임, TIFF는 첫 페이지만 읽습니다. OCR 오탈자를 확인하고 수정 후 재분석하세요.'}
