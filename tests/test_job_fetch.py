import unittest
from unittest.mock import patch
from agent_server.job_fetch import fetch_job, validate, plain

class FetchTests(unittest.TestCase):
    def test_disallow_external_and_private_urls(self):
        for url in ['http://127.0.0.1/recruit/', 'https://evil.com/recruit/', 'https://www.gamejob.co.kr.evil.com/recruit/']:
            with self.assertRaises(ValueError): validate(url)

    def test_remove_scripts_and_head(self):
        self.assertEqual(plain('<head><title>Ignored</title></head><p>Unity</p><script>Redis</script>'), 'Unity')

    @patch('agent_server.job_fetch.download')
    def test_text_frames(self, get):
        get.side_effect=['<iframe src="/Recruit/GI_Read_Comt_Ifrm?gno=1"></iframe>', '<p>Unity C# 개발자를 모집합니다. 게임 클라이언트 개발 경험과 협업 경험이 필요합니다.</p>']
        self.assertIn('Unity', fetch_job('https://www.gamejob.co.kr/Recruit/GI_Read/View?GI_No=1')['text'])

    @patch('agent_server.job_fetch.recognize_url')
    @patch('agent_server.job_fetch.download')
    def test_image_ocr_is_used(self, get, ocr):
        get.side_effect=['<iframe src="/Recruit/GI_Read_Comt_Ifrm?gno=1"></iframe>', '<img src="https://image.ninehire.com/poster.png">']
        ocr.return_value = 'Unity C# 개발 경험이 있는 게임 클라이언트 개발자를 모집합니다. 포트폴리오 제출이 필요합니다.'
        result = fetch_job('https://www.gamejob.co.kr/Recruit/GI_Read/View?GI_No=1')
        self.assertEqual(result['ocr_images'], 1)
        self.assertIn('Unity', result['text'])
