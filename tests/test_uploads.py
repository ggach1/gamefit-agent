import base64
import unittest
from unittest.mock import patch
from agent_server.uploads import extract_uploads

class UploadTests(unittest.TestCase):
    @patch('agent_server.uploads.recognize', side_effect=['Unity C#', 'Git Redis'])
    def test_preserves_order(self, ocr):
        items = [{'data':base64.b64encode(x).decode()} for x in [b'first',b'second']]
        result = extract_uploads(items)
        self.assertEqual(result['text'], 'Unity C#\n\nGit Redis')
        self.assertEqual(result['ocr_images'],2)
        self.assertEqual([call.args[0] for call in ocr.call_args_list],[b'first',b'second'])

    @patch('agent_server.uploads.recognize')
    def test_bad_uploads_fail_before_ocr(self, ocr):
        for items in [[], [{}]*7, [{'data':'%%%'}], [{'data':''}], [{'data':5}], {}]:
            with self.assertRaises(ValueError): extract_uploads(items)
        ocr.assert_not_called()

    @patch('agent_server.uploads.recognize', return_value='')
    def test_unreadable_image_not_silently_skipped(self, ocr):
        with self.assertRaisesRegex(ValueError,'1번째'):
            extract_uploads([{'data':'YQ=='}])
