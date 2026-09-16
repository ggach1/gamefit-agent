import unittest
from agent_server.ocr import validate_image_url, recognize

class OCRTests(unittest.TestCase):
    def test_only_allowed_https_hosts(self):
        for url in ['http://image.ninehire.com/a.png', 'https://127.0.0.1/a', 'https://image.ninehire.com.evil.test/a', 'https://image.ninehire.com:8000/a']:
            with self.assertRaises(ValueError): validate_image_url(url)
        validate_image_url('https://image.ninehire.com/a.png')

    def test_invalid_image_reports_error(self):
        with self.assertRaises(ValueError): recognize(b'not an image')
