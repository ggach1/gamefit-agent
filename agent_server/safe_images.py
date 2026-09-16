"""Fetch public images with DNS/IP checks and pinned connections (no proxies)."""
import http.client
import ipaddress
import socket
import ssl
import time
from urllib.parse import urlsplit, urljoin

MAX_IMAGE_BYTES = 12_000_000

def public_addresses(url):
    try:
        p = urlsplit(url)
        port = p.port or (443 if p.scheme == 'https' else 80)
        if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password:
            raise ValueError('HTTP 또는 HTTPS 공개 이미지 주소만 지원합니다.')
        if port != (443 if p.scheme == 'https' else 80) or '\\' in url or any(ord(c) < 32 for c in url):
            raise ValueError('지원하지 않는 이미지 주소입니다.')
        host = p.hostname.encode('idna').decode('ascii')
        records = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        addresses = list(dict.fromkeys(record[4][0] for record in records))
        if not addresses:
            raise ValueError('이미지 서버 주소를 찾지 못했습니다.')
        for address in addresses:
            ip = ipaddress.ip_address(address)
            # Disallow private, loopback, link-local, reserved and IPv6 transition addresses.
            if not ip.is_global or ip.is_multicast or (ip.version == 6 and (ip.ipv4_mapped or ip.sixtofour or ip.teredo)):
                raise ValueError('내부 네트워크 주소의 이미지는 가져올 수 없습니다. 파일 업로드를 이용하세요.')
        return p, host, port, addresses
    except (OSError, UnicodeError) as e:
        raise ValueError('이미지 서버 주소를 확인하지 못했습니다. 파일 업로드를 이용하세요.') from e

class PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, port, address):
        super().__init__(host, port, timeout=15)
        self.address = address
    def connect(self):
        self.sock = socket.create_connection((self.address, self.port), self.timeout)

class PinnedHTTPS(PinnedHTTP):
    def connect(self):
        raw = socket.create_connection((self.address, self.port), self.timeout)
        try:
            self.sock = ssl.create_default_context().wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise

def fetch_image(url):
    deadline = time.monotonic() + 60
    for _ in range(5):
        p, host, port, addresses = public_addresses(url)
        connection = (PinnedHTTPS if p.scheme == 'https' else PinnedHTTP)(host, port, addresses[0])
        try:
            target = p.path or '/'
            if p.query: target += '?' + p.query
            connection.request('GET', target, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'image/*', 'Accept-Encoding': 'identity'})
            response = connection.getresponse()
            if response.status in (301, 302, 303, 307, 308):
                location = response.getheader('Location')
                if not location: raise ValueError('이미지 이동 주소가 없습니다.')
                url = urljoin(url, location)
                continue
            if response.status != 200:
                raise ValueError(f'이미지 서버가 다운로드를 거부했습니다(HTTP {response.status}). 직접 업로드하세요.')
            mime = response.getheader('Content-Type', '').split(';')[0].strip().lower()
            if not (mime.startswith('image/') or mime in ('', 'application/octet-stream', 'binary/octet-stream')):
                raise ValueError('이미지 대신 웹페이지가 반환되었습니다. 직접 업로드하세요.')
            length = response.getheader('Content-Length')
            if length and int(length) > MAX_IMAGE_BYTES: raise ValueError('이미지는 12MB 이하여야 합니다.')
            chunks = []; size = 0
            while True:
                if time.monotonic() > deadline: raise ValueError('이미지 다운로드 시간이 초과되었습니다.')
                chunk = response.read(min(65536, MAX_IMAGE_BYTES + 1 - size))
                if not chunk: break
                size += len(chunk)
                if size > MAX_IMAGE_BYTES: raise ValueError('이미지는 12MB 이하여야 합니다.')
                chunks.append(chunk)
            return b''.join(chunks)
        except (OSError, http.client.HTTPException, UnicodeError) as e:
            raise ValueError('이미지 다운로드 실패. 공고 이미지를 저장해 직접 업로드하세요.') from e
        finally:
            connection.close()
    raise ValueError('이미지 이동 횟수가 너무 많습니다. 직접 업로드하세요.')
