#!/usr/bin/env python3
"""
DarwinCore to DataHub Metadata Translator

This script translates metadata from DarwinCore Archive EML files to DataHub metadata template format.
It can process both local DarwinCore archives and remote URLs.
"""

import argparse

from libs import EMLParser, DataHubTranslator, get_eml_content


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Translate DarwinCore EML to DataHub template')
    parser.add_argument('input', help='Input DarwinCore archive file or URL')
    parser.add_argument('-o', '--output', default='datahub_metadata.xlsx', 
                       help='Output Excel file (default: datahub_metadata.xlsx)')
    parser.add_argument('-t', '--template', default='data/template.xlsx',
                       help='Template file (default: data/template.xlsx)')
    
    args = parser.parse_args()
    
    
    # Initialize translator
    translator = DataHubTranslator(args.template)
    
    # Get EML content
    eml_content = get_eml_content(args.input)
    
    # Parse EML
    print("Parsing EML content...")
    eml_parser = EMLParser(eml_content)
    eml_metadata = eml_parser.get_metadata()
    creators = eml_parser.get_creators()
    
    # Add creators to metadata
    eml_metadata['creators'] = creators

    # Populate template
    print(f"Creating output file: {args.output}")
    translator.populate_template(eml_metadata, args.output)
    
    print("Translation completed successfully!")
    print(f"Output saved to: {args.output}")


if __name__ == "__main__":
    main()
