import unittest
import json
import os
import tempfile
from unittest.mock import MagicMock, patch
from io import StringIO
from modern_kata_kupas.cli import segment_word, reconstruct_word, batch_segment
from modern_kata_kupas import ModernKataKupas

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.mock_mkk = MagicMock(spec=ModernKataKupas)
        self.mock_mkk.segment.return_value = "di~makan"
        self.mock_mkk.reconstruct.return_value = "dimakan"

    def test_segment_word_text(self):
        result = segment_word(self.mock_mkk, "dimakan", format_output='text')
        self.assertEqual(result, "dimakan → di~makan")
        self.mock_mkk.segment.assert_called_with("dimakan")

    def test_segment_word_json(self):
        result = segment_word(self.mock_mkk, "dimakan", format_output='json')
        data = json.loads(result)
        self.assertEqual(data['word'], "dimakan")
        self.assertEqual(data['segmented'], "di~makan")

    def test_reconstruct_word_text(self):
        result = reconstruct_word(self.mock_mkk, "di~makan", format_output='text')
        self.assertEqual(result, "di~makan → dimakan")
        self.mock_mkk.reconstruct.assert_called_with("di~makan")

    def test_reconstruct_word_json(self):
        result = reconstruct_word(self.mock_mkk, "di~makan", format_output='json')
        data = json.loads(result)
        self.assertEqual(data['segmented'], "di~makan")
        self.assertEqual(data['reconstructed'], "dimakan")

    def test_batch_segment_text(self):
        # Create temp input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp_in:
            tmp_in.write("dimakan\nterbawa")
            tmp_in_path = tmp_in.name

        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', new=captured_output):
            batch_segment(self.mock_mkk, tmp_in_path, format_output='text')
        
        output = captured_output.getvalue().strip().split('\n')
        self.assertEqual(len(output), 2)
        # Mock returns same result for all calls because side_effect wasn't set, just return_value
        self.assertIn("dimakan → di~makan", output[0]) 
        
        os.unlink(tmp_in_path)

    def test_batch_segment_csv_to_file(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp_in:
            tmp_in.write("dimakan")
            tmp_in_path = tmp_in.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tmp_out:
            tmp_out_path = tmp_out.name
        tmp_out.close() # Close to allow writing by cli

        # Capture stdout to silence "Results written to..."
        with patch('sys.stdout', new=StringIO()):
            batch_segment(self.mock_mkk, tmp_in_path, output_file=tmp_out_path, format_output='csv')

        with open(tmp_out_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        self.assertEqual(content, "dimakan,di~makan")

        os.unlink(tmp_in_path)
        os.unlink(tmp_out_path)

if __name__ == '__main__':
    unittest.main()
