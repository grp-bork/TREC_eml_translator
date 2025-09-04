#!/usr/bin/env python3
"""
DataHub Translator

This module provides functionality to translate EML metadata to DataHub template format.
"""

import pandas as pd
import shutil


class DataHubTranslator:
    """Translator from EML to DataHub template format"""
    
    def __init__(self, template_file='data/template.xlsx'):
        """Initialize translator with mapping and template files"""
        self.template_file = template_file
    
    def populate_template(self, datahub_metadata, output_file):
        """Populate the DataHub template with translated metadata"""
        shutil.copyfile(self.template_file, output_file)
        # Read the template
        with pd.ExcelWriter(output_file, engine='openpyxl', mode="a", if_sheet_exists="overlay") as writer:
            dataset_df = pd.read_excel(self.template_file, sheet_name='dataset')
            # Create a new row with actual data
            new_row = {}
            for col in dataset_df.columns:
                if col in datahub_metadata:
                    new_row[col] = datahub_metadata[col]
                else:
                    new_row[col] = ""
            
            # Add the new row at the end
            dataset_df.loc[2] = new_row
            dataset_df.to_excel(writer, sheet_name='dataset', index=False)

            # authors
            author_df = pd.read_excel(self.template_file, sheet_name='author')
            if 'creators' in datahub_metadata:
                # Add author information
                for creator in datahub_metadata['creators']:
                    new_row = {}
                    for col in author_df.columns:
                        if col in creator:
                            new_row[col] = creator[col]
                        else:
                            new_row[col] = ""
                    author_df.loc[len(author_df)] = new_row
            
            # Write the sheet
            author_df.to_excel(writer, sheet_name='author', index=False)
