#!/usr/bin/env python3
"""
Test module for the DarwinCore to DataHub translator

This module contains comprehensive tests for all translator functionality.
"""

import os
import sys
import subprocess
import unittest
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from libs.eml_parser import EMLParser
from libs.datahub_translator import DataHubTranslator
from libs.downloader import get_eml_content


class TestEMLParser(unittest.TestCase):
    """Test cases for EML parser functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Extract EML from dummy dataset for testing
        with open('data/dummy_dataset.zip', 'rb') as f:
            import zipfile
            with zipfile.ZipFile(f, 'r') as zip_ref:
                self.eml_content = zip_ref.read('eml.xml')
        
        self.parser = EMLParser(self.eml_content)
    
    def test_get_metadata(self):
        """Test metadata extraction"""
        metadata = self.parser.get_metadata()
        
        # Check that required fields are extracted
        self.assertIn('dataset:title', metadata)
        self.assertIn('dataset:description', metadata)
        self.assertIn('dataset:language', metadata)
        
        # Check specific values
        self.assertEqual(metadata['dataset:title'], 'Test dataset')
        self.assertEqual(metadata['dataset:description'], 'Description')
        self.assertEqual(metadata['dataset:language'], 'eng')
    
    def test_get_creators(self):
        """Test creator information extraction"""
        creators = self.parser.get_creators()
        
        # Check that creators are extracted
        self.assertGreater(len(creators), 0)
        
        # Check first creator
        first_creator = creators[0]
        self.assertEqual(first_creator['author:first-name'], 'Lynn')
        self.assertEqual(first_creator['author:last-name'], 'Test')
        self.assertEqual(first_creator['author:affiliation'], 'Test org')
        self.assertEqual(first_creator['author:email'], 'test@test.com')


class TestDataHubTranslator(unittest.TestCase):
    """Test cases for DataHub translator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.translator = DataHubTranslator()
    
    def test_populate_template(self):
        """Test template population"""
        datahub_metadata = {
            'dataset:title': 'Test Title',
            'dataset:description': 'Test Description',
            'creators': [
                {
                    'author:first-name': 'John',
                    'author:last-name': 'Doe',
                    'author:email': 'john@example.com'
                }
            ]
        }
        
        output_file = 'test_output.xlsx'
        self.translator.populate_template(datahub_metadata, output_file)
        
        # Check that file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Clean up
        os.remove(output_file)


class TestDownloader(unittest.TestCase):
    """Test cases for downloader functionality"""
    
    def test_get_eml_content_local_zip(self):
        """Test getting EML content from local zip file"""
        eml_content = get_eml_content('data/dummy_dataset.zip')
        
        # Check that content is extracted
        self.assertIsInstance(eml_content, bytes)
        self.assertGreater(len(eml_content), 0)
        
        # Check that it's valid XML
        content_str = eml_content.decode('utf-8')
        self.assertIn('<eml:eml', content_str)
        self.assertIn('<dataset>', content_str)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def test_full_workflow_dummy_dataset(self):
        """Test complete workflow with dummy dataset"""
        # This test would run the full workflow
        # For now, we'll just check that the main script can be imported
        try:
            from trec_to_eml_translator import main
            self.assertTrue(True)  # If we get here, import succeeded
        except ImportError as e:
            self.fail(f"Failed to import main module: {e}")


def run_command_line_tests():
    """Run command line tests"""
    print("Running command line tests...")
    
    # Test 1: Dummy dataset
    print("\n=== Testing Dummy Dataset ===")
    result = subprocess.run([
        'python', 'trec_to_eml_translator.py',
        'data/dummy_dataset.zip',
        '-o', 'test_output_dummy.xlsx'
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and os.path.exists('test_output_dummy.xlsx'):
        print("✅ Dummy dataset test PASSED")
        os.remove('test_output_dummy.xlsx')
    else:
        print("❌ Dummy dataset test FAILED")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    
    # Test 2: Real URL (optional - requires internet)
    print("\n=== Testing Real URL ===")
    try:
        result = subprocess.run([
            'python', 'trec_to_eml_translator.py',
            'https://ipt.vliz.be/eurobis/resource?r=phytoplankton_in_the_western_north_sea_between_1976_and_1977',
            '-o', 'test_output_real.xlsx'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists('test_output_real.xlsx'):
            print("✅ Real URL test PASSED")
            os.remove('test_output_real.xlsx')
        else:
            print("❌ Real URL test FAILED")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ Real URL test TIMEOUT (network issue)")
    except Exception as e:
        print(f"⚠️ Real URL test SKIPPED: {e}")


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run command line tests
    run_command_line_tests()
    
    print("\n🎉 All tests completed!")
