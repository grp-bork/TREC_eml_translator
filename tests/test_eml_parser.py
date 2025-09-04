#!/usr/bin/env python3
"""
Unit tests for EML Parser

This module contains comprehensive unit tests for the EMLParser class.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from libs.eml_parser import EMLParser


class TestEMLParser(unittest.TestCase):
    """Test cases for EMLParser class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a minimal valid EML content for testing
        self.minimal_eml = '''<?xml version="1.0" encoding="UTF-8"?>
<eml:eml xmlns:eml="https://eml.ecoinformatics.org/eml-2.2.0">
    <dataset>
        <title>Test Dataset</title>
        <creator>
            <individualName>
                <givenName>John</givenName>
                <surName>Doe</surName>
            </individualName>
            <organizationName>Test University</organizationName>
            <electronicMailAddress>john.doe@test.edu</electronicMailAddress>
            <userId directory="https://orcid.org/">0000-0000-0000-0001</userId>
        </creator>
        <creator>
            <individualName>
                <givenName>Jane</givenName>
                <surName>Smith</surName>
            </individualName>
            <organizationName>Test Institute</organizationName>
            <electronicMailAddress>jane.smith@test.edu</electronicMailAddress>
        </creator>
        <pubDate>2023-01-15</pubDate>
        <language>eng</language>
        <abstract>This is a test dataset for unit testing.</abstract>
        <keywordSet>
            <keyword>test</keyword>
            <keyword>unit testing</keyword>
            <keyword>EML</keyword>
        </keywordSet>
        <intellectualRights>Creative Commons Attribution 4.0</intellectualRights>
        <geographicCoverage>
            <geographicDescription>Test region</geographicDescription>
            <boundingCoordinates>
                <westBoundingCoordinate>-180.0</westBoundingCoordinate>
                <eastBoundingCoordinate>180.0</eastBoundingCoordinate>
                <northBoundingCoordinate>90.0</northBoundingCoordinate>
                <southBoundingCoordinate>-90.0</southBoundingCoordinate>
            </boundingCoordinates>
        </geographicCoverage>
        <temporalCoverage>
            <rangeOfDates>
                <beginDate>
                    <calendarDate>2023-01-01</calendarDate>
                </beginDate>
                <endDate>
                    <calendarDate>2023-12-31</calendarDate>
                </endDate>
            </rangeOfDates>
        </temporalCoverage>
        <methods>
            <sampling>
                <samplingDescription>
                    <para>Test sampling description for unit testing.</para>
                </samplingDescription>
            </sampling>
        </methods>
    </dataset>
</eml:eml>'''
        
        # Create EML with collective author
        self.collective_eml = '''<?xml version="1.0" encoding="UTF-8"?>
<eml:eml xmlns:eml="https://eml.ecoinformatics.org/eml-2.2.0">
    <dataset>
        <title>Collective Author Dataset</title>
        <creator>
            <organizationName>Test Consortium</organizationName>
            <electronicMailAddress>consortium@test.org</electronicMailAddress>
        </creator>
        <pubDate>2023-06-01</pubDate>
        <language>eng</language>
        <abstract>Dataset with collective author.</abstract>
    </dataset>
</eml:eml>'''
        
        # Create EML with missing elements
        self.minimal_eml_missing = '''<?xml version="1.0" encoding="UTF-8"?>
<eml:eml xmlns:eml="https://eml.ecoinformatics.org/eml-2.2.0">
    <dataset>
        <title>Minimal Dataset</title>
        <creator>
            <individualName>
                <givenName>Test</givenName>
                <surName>User</surName>
            </individualName>
        </creator>
    </dataset>
</eml:eml>'''
    
    def test_init_with_valid_eml(self):
        """Test EMLParser initialization with valid EML content"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        self.assertIsNotNone(parser.root)
        self.assertIsNotNone(parser.namespaces)
    
    def test_init_with_invalid_eml(self):
        """Test EMLParser initialization with invalid XML"""
        with self.assertRaises(Exception):
            EMLParser(b"<invalid>xml<unclosed>")
    
    def test_get_text_simple(self):
        """Test get_text method with simple xpath"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        title = parser.get_text('//dataset/title')
        self.assertEqual(title, 'Test Dataset')
    
    def test_get_text_with_default(self):
        """Test get_text method with default value"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        # Test non-existent element with default
        result = parser.get_text('//dataset/nonexistent', default='default_value')
        self.assertEqual(result, 'default_value')
    
    def test_get_text_empty_element(self):
        """Test get_text method with empty element"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        # Test element that exists but has no text
        result = parser.get_text('//dataset/creator[1]/organizationName')
        self.assertEqual(result, 'Test University')
    
    def test_get_text_list(self):
        """Test get_text_list method"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        keywords = parser.get_text_list('//dataset//keyword')
        expected = ['test', 'unit testing', 'EML']
        self.assertEqual(keywords, expected)
    
    def test_get_text_list_empty(self):
        """Test get_text_list method with no matching elements"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        result = parser.get_text_list('//dataset/nonexistent')
        self.assertEqual(result, [])
    
    def test_get_metadata_basic_fields(self):
        """Test get_metadata method for basic fields"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        metadata = parser.get_metadata()
        
        # Test basic fields
        self.assertEqual(metadata['dataset:title'], 'Test Dataset')
        self.assertEqual(metadata['dataset:description'], 'This is a test dataset for unit testing.')
        self.assertEqual(metadata['dataset:language'], 'eng')
        self.assertEqual(metadata['dataset:license'], 'Creative Commons Attribution 4.0')
        self.assertEqual(metadata['dataset:date-first-created'], '2023-01-15')
    
    def test_get_metadata_keywords(self):
        """Test get_metadata method for keywords"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        metadata = parser.get_metadata()
        
        expected_keywords = 'test, unit testing, EML'
        self.assertEqual(metadata['dataset:keywords'], expected_keywords)
    
    def test_get_metadata_geographic_coverage(self):
        """Test get_metadata method for geographic coverage"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        metadata = parser.get_metadata()
        
        self.assertEqual(metadata['dataset:geographic-area'], 'Test region')
        self.assertEqual(metadata['dataset:longitude-min'], '-180.0')
        self.assertEqual(metadata['dataset:longitude-max'], '180.0')
        self.assertEqual(metadata['dataset:latitude-min'], '-90.0')
        self.assertEqual(metadata['dataset:latitude-max'], '90.0')
    
    def test_get_metadata_temporal_coverage(self):
        """Test get_metadata method for temporal coverage"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        metadata = parser.get_metadata()
        
        self.assertEqual(metadata['dataset:datetime-min'], '2023-01-01')
        self.assertEqual(metadata['dataset:datetime-max'], '2023-12-31')
    
    def test_get_metadata_methods(self):
        """Test get_metadata method for methods"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        metadata = parser.get_metadata()
        
        self.assertEqual(metadata['analysis:description'], 'Test sampling description for unit testing.')
    
    def test_get_metadata_missing_fields(self):
        """Test get_metadata method with missing fields"""
        parser = EMLParser(self.minimal_eml_missing.encode('utf-8'))
        metadata = parser.get_metadata()
        
        # Should have default values for missing fields
        self.assertEqual(metadata['dataset:title'], 'Minimal Dataset')
        self.assertEqual(metadata['dataset:description'], '')
        self.assertEqual(metadata['dataset:language'], 'en')  # Default value
        self.assertEqual(metadata['dataset:keywords'], '')
    
    def test_get_creators_individual(self):
        """Test get_creators method for individual authors"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        creators = parser.get_creators()
        
        self.assertEqual(len(creators), 2)
        
        # Test first creator
        first_creator = creators[0]
        self.assertEqual(first_creator['author:type'], 'individual author')
        self.assertEqual(first_creator['author:first-name'], 'John')
        self.assertEqual(first_creator['author:last-name'], 'Doe')
        self.assertEqual(first_creator['author:affiliation'], 'Test University')
        self.assertEqual(first_creator['author:email'], 'john.doe@test.edu')
        self.assertEqual(first_creator['author:pid'], '0000-0000-0000-0001')
        
        # Test second creator
        second_creator = creators[1]
        self.assertEqual(second_creator['author:type'], 'individual author')
        self.assertEqual(second_creator['author:first-name'], 'Jane')
        self.assertEqual(second_creator['author:last-name'], 'Smith')
        self.assertEqual(second_creator['author:affiliation'], 'Test Institute')
        self.assertEqual(second_creator['author:email'], 'jane.smith@test.edu')
        self.assertEqual(second_creator['author:pid'], '')
    
    def test_get_creators_collective(self):
        """Test get_creators method for collective authors"""
        parser = EMLParser(self.collective_eml.encode('utf-8'))
        creators = parser.get_creators()
        
        self.assertEqual(len(creators), 1)
        
        creator = creators[0]
        self.assertEqual(creator['author:type'], 'collective author')
        self.assertEqual(creator['author:first-name'], '')
        self.assertEqual(creator['author:last-name'], '')
        self.assertEqual(creator['author:affiliation'], 'Test Consortium')
        self.assertEqual(creator['author:email'], 'consortium@test.org')
        self.assertEqual(creator['author:pid'], '')
    
    def test_get_creators_mixed(self):
        """Test get_creators method with mixed individual and collective authors"""
        mixed_eml = '''<?xml version="1.0" encoding="UTF-8"?>
<eml:eml xmlns:eml="https://eml.ecoinformatics.org/eml-2.2.0">
    <dataset>
        <title>Mixed Authors Dataset</title>
        <creator>
            <individualName>
                <givenName>Individual</givenName>
                <surName>Author</surName>
            </individualName>
        </creator>
        <creator>
            <organizationName>Collective Organization</organizationName>
        </creator>
    </dataset>
</eml:eml>'''
        
        parser = EMLParser(mixed_eml.encode('utf-8'))
        creators = parser.get_creators()
        
        self.assertEqual(len(creators), 2)
        self.assertEqual(creators[0]['author:type'], 'individual author')
        self.assertEqual(creators[1]['author:type'], 'collective author')
    
    def test_get_creators_no_creators(self):
        """Test get_creators method with no creators"""
        no_creators_eml = '''<?xml version="1.0" encoding="UTF-8"?>
<eml:eml xmlns:eml="https://eml.ecoinformatics.org/eml-2.2.0">
    <dataset>
        <title>No Creators Dataset</title>
    </dataset>
</eml:eml>'''
        
        parser = EMLParser(no_creators_eml.encode('utf-8'))
        creators = parser.get_creators()
        
        self.assertEqual(creators, [])
    
    def test_get_text_list_with_empty_elements(self):
        """Test get_text_list method with empty elements"""
        eml_with_empty = '''<?xml version="1.0" encoding="UTF-8"?>
<eml:eml xmlns:eml="https://eml.ecoinformatics.org/eml-2.2.0">
    <dataset>
        <title>Empty Elements Test</title>
        <keywordSet>
            <keyword>valid</keyword>
            <keyword></keyword>
            <keyword>   </keyword>
            <keyword>another valid</keyword>
        </keywordSet>
    </dataset>
</eml:eml>'''
        
        parser = EMLParser(eml_with_empty.encode('utf-8'))
        keywords = parser.get_text_list('//dataset//keyword')
        
        # Should only return non-empty, non-whitespace keywords
        expected = ['valid', 'another valid']
        self.assertEqual(keywords, expected)
    
    def test_error_handling_invalid_xpath(self):
        """Test error handling with invalid xpath"""
        parser = EMLParser(self.minimal_eml.encode('utf-8'))
        
        # Should not raise exception, should return default
        result = parser.get_text('invalid[xpath]', default='default')
        self.assertEqual(result, 'default')
    
    def test_error_handling_malformed_xml(self):
        """Test error handling with malformed XML"""
        with self.assertRaises(Exception):
            EMLParser(b"<eml:eml><dataset><title>Unclosed tag")
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters"""
        unicode_eml = '''<?xml version="1.0" encoding="UTF-8"?>
<eml:eml xmlns:eml="https://eml.ecoinformatics.org/eml-2.2.0">
    <dataset>
        <title>Unicode Test: éñçå</title>
        <creator>
            <individualName>
                <givenName>José</givenName>
                <surName>García</surName>
            </individualName>
        </creator>
        <abstract>Test with Unicode: αβγδε</abstract>
    </dataset>
</eml:eml>'''
        
        parser = EMLParser(unicode_eml.encode('utf-8'))
        metadata = parser.get_metadata()
        creators = parser.get_creators()
        
        self.assertEqual(metadata['dataset:title'], 'Unicode Test: éñçå')
        self.assertEqual(metadata['dataset:description'], 'Test with Unicode: αβγδε')
        self.assertEqual(creators[0]['author:first-name'], 'José')
        self.assertEqual(creators[0]['author:last-name'], 'García')


if __name__ == '__main__':
    unittest.main(verbosity=2)
