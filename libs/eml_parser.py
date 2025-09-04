#!/usr/bin/env python3
"""
EML (Ecological Metadata Language) Parser

This module provides functionality to parse EML files and extract metadata.
"""

from lxml import etree


class EMLParser:
    """Parser for EML (Ecological Metadata Language) files"""
    
    def __init__(self, eml_content):
        """Initialize parser with EML content"""
        self.root = etree.fromstring(eml_content)
        # Define namespaces
        self.namespaces = {
            'eml': 'https://eml.ecoinformatics.org/eml-2.2.0',
            'dc': 'http://purl.org/dc/terms/'
        }
    
    def get_text(self, xpath, default="", root=None):
        """Extract text from XML using xpath"""
        if root is None:
            root = self.root
        elements = root.xpath(xpath, namespaces=self.namespaces)
        if elements:
            return elements[0].text.strip() if elements[0].text else default
        return default
    
    def get_text_list(self, xpath):
        """Extract list of text values from XML using xpath"""
        elements = self.root.xpath(xpath)
        return [elem.text.strip() for elem in elements if elem.text and elem.text.strip()]
    
    def get_attribute(self, xpath, attribute, default=""):
        """Extract attribute value from XML using xpath"""
        elements = self.root.xpath(xpath)
        if elements:
            return elements[0].get(attribute, default)
        else:
            return default
    
    def get_creators(self):
        """Extract creator information"""
        creators = []
        creator_elements = self.root.xpath('//dataset/creator')
        
        for creator in creator_elements:
            creator_info = {}
            
            # Get individual name
            given_name = self.get_text('.//givenName', root=creator)
            sur_name = self.get_text('.//surName', root=creator)
            
            if sur_name:
                creator_info['author:type'] = 'individual author'
                creator_info['author:first-name'] = given_name
                creator_info['author:last-name'] = sur_name
            else:
                creator_info['author:type'] = 'collective author'
                creator_info['author:first-name'] = ""
                creator_info['author:last-name'] = ""
            
            # Get organization
            creator_info['author:affiliation'] = self.get_text('.//organizationName', root=creator)
            
            # Get email
            creator_info['author:email'] = self.get_text('.//electronicMailAddress', root=creator)
            
            # Get ORCID
            orcid = creator.xpath('.//userId[@directory="https://orcid.org/"]')
            creator_info['author:pid'] = orcid[0].text.strip() if orcid and orcid[0].text else ""
            
            creators.append(creator_info)
        
        return creators
    
    def get_metadata(self):
        """Extract all metadata from EML"""
        metadata = {}
        
        # Basic dataset information
        metadata['dataset:title'] = self.get_text('//dataset/title')
        metadata['dataset:description'] = self.get_text('//dataset/abstract')
        metadata['dataset:language'] = self.get_text('//dataset/language', 'en')
        metadata['dataset:license'] = self.get_text('//dataset/intellectualRights')
        metadata['dataset:pid'] = self.get_text('//dataset/alternateIdentifier')
        if metadata['dataset:pid']:
            metadata['dataset:pid-source'] = 'GBIF UUID'
            metadata['dataset:pid-url'] = f'https://www.gbif.org/dataset/{metadata["dataset:pid"]}'
        
        # Keywords
        keywords = self.get_text_list('//dataset//keyword')
        metadata['dataset:keywords'] = ', '.join(keywords) if keywords else ""
        
        # Dates
        metadata['dataset:date-first-created'] = self.get_text('//dataset/pubDate')
        
        # Geographic coverage
        metadata['dataset:geographic-area'] = self.get_text('//dataset//geographicCoverage/geographicDescription')
        metadata['dataset:latitude-min'] = self.get_text('//dataset//geographicCoverage//southBoundingCoordinate')
        metadata['dataset:latitude-max'] = self.get_text('//dataset//geographicCoverage//northBoundingCoordinate')
        metadata['dataset:longitude-min'] = self.get_text('//dataset//geographicCoverage//westBoundingCoordinate')
        metadata['dataset:longitude-max'] = self.get_text('//dataset//geographicCoverage//eastBoundingCoordinate')
        
        # Temporal coverage
        metadata['dataset:datetime-min'] = self.get_text('//dataset//temporalCoverage//beginDate//calendarDate')
        metadata['dataset:datetime-max'] = self.get_text('//dataset//temporalCoverage//endDate//calendarDate')
        
        # Methods
        metadata['analysis:description'] = self.get_text('//dataset//sampling/samplingDescription//para')

        metadata['dataset:acknowledgements-contributions'] = self.get_text('//dataset//acknowledgements')

        return metadata
