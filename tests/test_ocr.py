import io
import unittest
from unittest.mock import patch, MagicMock
from agent_server.ocr import recognize
from agent_server.safe_images import public_addresses, fetch_image, PinnedHTTPS

def records(*ips):
    return [(2, 1, 6, '', (ip, 443)) for ip in ips]

class OCRTests(unittest.TestCase):
    @patch('agent_server.safe_images.socket.getaddrinfo', return_value=records('8.8.8.8'))
    def test_public_hosts_not_limited_to_allowlist(self, dns):
        self.assertEqual(public_addresses('https://new-company.example/poster.png')[3], ['8.8.8.8'])
        public_addresses('http://new-company.example/poster.png')

    def test_invalid_urls_rejected_before_dns(self):
        for url in ['file:///a', 'ftp://host/a','https://user:pass@host/a','https://host:8000/a']:
            with self.assertRaises(ValueError): public_addresses(url)

    @patch('agent_server.safe_images.socket.getaddrinfo')
    def test_private_and_mixed_dns_rejected(self, dns):
        for ip in ['127.0.0.1','10.0.0.1','192.168.1.1','169.254.169.254','::1','fc00::1','::ffff:8.8.8.8','224.0.0.1']:
            dns.return_value = records('8.8.8.8', ip)
            with self.assertRaises(ValueError): public_addresses('https://company.example/a')

    @patch('agent_server.safe_images.PinnedHTTPS')
    @patch('agent_server.safe_images.socket.getaddrinfo')
    def test_redirect_to_private_rejected(self, dns, connection):
        dns.side_effect = [records('8.8.8.8'), records('127.0.0.1')]
        response = connection.return_value.getresponse.return_value
        response.status = 302
        response.getheader.return_value = 'https://localhost/internal'
        with self.assertRaises(ValueError): fetch_image('https://public.example/a')
        self.assertEqual(connection.call_count, 1)

    @patch('agent_server.safe_images.ssl.create_default_context')
    @patch('agent_server.safe_images.socket.create_connection')
    def test_connection_pinned_with_original_tls_hostname(self, connect, context):
        conn = PinnedHTTPS('company.example',443,'8.8.8.8'); conn.connect()
        connect.assert_called_once_with(('8.8.8.8',443),15)
        context.return_value.wrap_socket.assert_called_once_with(connect.return_value,server_hostname='company.example')

    @patch('agent_server.safe_images.PinnedHTTPS')
    @patch('agent_server.safe_images.socket.getaddrinfo', return_value=records('8.8.8.8'))
    def test_html_and_large_responses_rejected(self, dns, connection):
        response = connection.return_value.getresponse.return_value
        response.status = 200
        for headers in [{'Content-Type':'text/html'},{'Content-Type':'image/png','Content-Length':'12000001'}]:
            response.getheader.side_effect = lambda key, default=None: headers.get(key, default)
            with self.assertRaises(ValueError): fetch_image('https://company.example/a')

    def test_invalid_image_reports_error(self):
        with self.assertRaises(ValueError): recognize(b'not an image')
