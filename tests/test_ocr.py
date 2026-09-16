import unittest
from agent_server.ocr import validate_image_url, recognize

class OCRTests(unittest.TestCase):
    def test_only_allowed_https_hosts(self):
        for url in ['http://image.ninehire.com/a.png', 'https://127.0.0.1/a', 'https://image.ninehire.com.evil.test/a', 'https://image.ninehire.com:8000/a']:
            with self.assertRaises(ValueError): validate_image_url(url)
        validate_image_url('https://image.ninehire.com/a.png')

    def test_com2us_recruiter_host(self):
        validate_image_url('https://com2us.recruiter.co.kr/upload/57043/image/202609/poster.png')
        for url in ['https://com2us.recruiter.co.kr.evil.test/upload/a.png',
                    'https://other.recruiter.co.kr/upload/a.png',
                    'https://com2us.recruiter.co.kr:8000/upload/a.png']:
            with self.assertRaises(ValueError):
                validate_image_url(url)

    def test_invalid_image_reports_error(self):
        with self.assertRaises(ValueError): recognize(b'not an image')
