"""제한된 공개 공고 URL에서 본문을 추출한다."""
import re
import json
from html.parser import HTMLParser
from urllib.parse import urlsplit, urljoin
from urllib.request import Request, build_opener, HTTPRedirectHandler
from .ocr import recognize_url

def validate(url):
    p = urlsplit(url)
    if p.scheme != 'https' or p.hostname not in {'www.gamejob.co.kr','gamejob.co.kr','www.jobkorea.co.kr','jobkorea.co.kr'} or p.username or p.password or p.port not in (None,443) or not p.path.lower().startswith('/recruit/'):
        raise ValueError('게임잡 또는 잡코리아 HTTPS 공고 상세 링크를 입력하세요.')

class Redirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def download(url):
    validate(url)
    try:
        with build_opener(Redirect()).open(Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=12) as r:
            raw = r.read(2000001)
            if len(raw)>2000000:
                raise ValueError('페이지 크기 초과')
            match = re.search(br'charset\s*=\s*[\"\x27]?([\w-]+)', raw[:8192], re.I)
            charset = r.headers.get_content_charset() or (match.group(1).decode() if match else 'utf-8')
            return raw.decode(charset, errors='replace')
    except Exception as e:
        raise ValueError('공고 가져오기 실패: 접근 제한이나 마감 여부를 확인하고 텍스트 입력을 이용하세요.') from e

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.text=[]; self.frames=[]; self.images=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag in ('script','style','noscript','head'): self.skip+=1
        if tag=='iframe' and a.get('src'): self.frames.append(a['src'])
        if tag=='img' and (a.get('data-src') or a.get('src')): self.images.append((a.get('data-src') or a['src'], a.get('alt', '')))
        if tag in ('br','p','div','li'): self.text.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style','noscript','head') and self.skip: self.skip-=1
    def handle_data(self, data):
        if not self.skip: self.text.append(data)
    def plain(self):
        return '\n'.join(x.strip() for x in ''.join(self.text).splitlines() if x.strip())

def plain(html):
    p=Page(); p.feed(html); return p.plain()

def fetch_job(url):
    html=download(url); page=Page(); page.feed(html); parts=[]; ocr_count=0
    seen_images = set()
    def fragment(content, base):
        nonlocal ocr_count
        detail = Page(); detail.feed(content)
        extracted = detail.plain()
        for src, alt in detail.images:
            image_url = urljoin(base, src)
            if image_url in seen_images: continue
            if len(seen_images) >= 6:
                raise ValueError('공고 이미지가 6장을 초과합니다. 필요한 이미지를 직접 업로드하세요.')
            seen_images.add(image_url)
            image_text = recognize_url(image_url)
            if image_text: extracted += '\n' + image_text
            ocr_count += 1
        return extracted
    if 'gamejob.co.kr' in urlsplit(url).hostname:
        for src in page.frames:
            target=urljoin(url,src)
            if urlsplit(target).path.lower() in ('/recruit/gi_read_comt_ifrm','/recruit/gi_read_gi_comment_ifrm'):
                content = download(target)
                parts.append(fragment(content, target))
    else:
        def visit(obj):
            if isinstance(obj,dict):
                if obj.get('@type')=='JobPosting' and isinstance(obj.get('description'),str): parts.append(fragment(obj['description'], url))
                for v in obj.values(): visit(v)
            elif isinstance(obj,list):
                for v in obj: visit(v)
        for script in re.findall(r'<script\b[^>]*type=[\"\x27]application/ld\+json[\"\x27][^>]*>(.*?)</script>',html,re.S|re.I):
            try: obj = json.loads(script)
            except ValueError: continue
            visit(obj)
    text='\n\n'.join(parts)
    if len(text.strip())<40: raise ValueError('본문 추출 실패: 이미지 또는 동적 공고일 수 있습니다. 텍스트 입력으로 전환하세요.')
    if len(text) > 60000: raise ValueError('본문이 너무 깁니다. 필요한 이미지만 직접 업로드하세요.')
    return {'url':url,'text':text, 'ocr_images':ocr_count,
            'warning':'OCR은 오탈자가 있을 수 있습니다. 추출 본문을 확인하고 수정해 재분석하세요.' if ocr_count else ''}
